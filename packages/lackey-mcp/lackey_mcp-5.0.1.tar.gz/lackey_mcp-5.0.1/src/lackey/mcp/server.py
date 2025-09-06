"""Gateway-based MCP server implementation for Lackey task management."""

import functools
import logging
import time
from typing import Any, Awaitable, Callable, Dict, Optional, TypeVar, cast

from mcp.server import FastMCP

from lackey import LackeyCore, __api_version__
from lackey.mcp.gateways.lackey_analyze import LackeyAnalyzeGateway
from lackey.mcp.gateways.lackey_do import LackeyDoGateway
from lackey.mcp.gateways.lackey_get import LackeyGetGateway
from lackey.mcp.gateways.lackey_schema import LackeySchemaGateway
from lackey.mcp.tool_analytics import get_analytics_manager
from lackey.rate_limiting import get_rate_limit_manager
from lackey.validation import InputValidator

F = TypeVar("F", bound=Callable[..., Awaitable[Any]])
logger = logging.getLogger(__name__)


def mcp_analytics_tracking() -> Callable[[F], F]:
    """Analytics tracking decorator for MCP tools."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            success = False
            error_message = None

            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error_message = str(e)
                raise
            finally:
                execution_time_ms = (time.time() - start_time) * 1000

                try:
                    analytics_manager = get_analytics_manager()
                    analytics_manager.record_tool_usage(
                        tool_name=func.__name__,
                        execution_time_ms=execution_time_ms,
                        success=success,
                        error_message=error_message,
                        parameters={
                            k: str(v)[:100] for k, v in kwargs.items()
                        },  # Truncate long values
                        user_context="mcp_stdio",
                    )
                except Exception as analytics_error:
                    # Don't let analytics errors break tool execution
                    logger.warning(
                        f"Analytics tracking failed for {func.__name__}: "
                        f"{analytics_error}"
                    )

        return cast(F, wrapper)

    return decorator


def mcp_rate_limit(rule_name: str = "default") -> Callable[[F], F]:
    """Rate limiting decorator specifically for MCP stdio communication."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            manager = get_rate_limit_manager()

            # Use localhost IP as the identifier for MCP stdio communication
            identifier = "127.0.0.1"
            endpoint = func.__name__

            # Check rate limit
            is_allowed, rate_info = manager.check_rate_limit(
                identifier, endpoint, rule_name
            )

            if not is_allowed:
                from lackey.security import SecurityError

                error_msg = f"Rate limit exceeded. Status: {rate_info['status']}"
                if rate_info.get("retry_after", 0) > 0:
                    error_msg += f" Retry after {rate_info['retry_after']:.0f} seconds."
                raise SecurityError(error_msg)

            return await func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator


def mcp_security_required(
    validate_input: bool = True,
    validation_rules: Optional[Dict[str, str]] = None,
) -> Callable[[F], F]:
    """Security decorator specifically for MCP stdio communication."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            from lackey.security import SecurityEvent, get_security_manager
            from lackey.validation import SecurityError, ValidationError

            # Get security manager instance
            security_manager = get_security_manager()

            # Input validation
            if validate_input and validation_rules:
                try:
                    # Validate and sanitize kwargs
                    sanitized_kwargs = security_manager.validate_and_sanitize_input(
                        kwargs, validation_rules
                    )
                    kwargs.update(sanitized_kwargs)
                except (ValidationError, SecurityError) as e:
                    security_manager.log_security_event(
                        SecurityEvent(
                            event_type="endpoint_security_violation",
                            severity="medium",
                            message=f"Security violation in {func.__name__}: {str(e)}",
                            metadata={"function": func.__name__, "error": str(e)},
                        )
                    )
                    raise

            # Call original function
            return await func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator


# MCP API Version (follows semantic versioning)
MCP_API_VERSION = __api_version__  # "1.0.0"

# Create the FastMCP server instance
mcp_server = FastMCP("lackey")

# Global variables for core components and gateways
lackey_core: Optional[LackeyCore] = None
validator: Optional[InputValidator] = None
do_gateway: Optional[LackeyDoGateway] = None
get_gateway: Optional[LackeyGetGateway] = None
analyze_gateway: Optional[LackeyAnalyzeGateway] = None
schema_gateway: Optional[LackeySchemaGateway] = None


def create_server(lackey_dir_path: str = ".lackey") -> FastMCP:
    """Create and configure the Gateway-based Lackey MCP server.

    Args:
        lackey_dir_path: Path to the .lackey directory where files are stored

    Returns:
        Configured FastMCP server instance with 3 semantic gateways
    """
    global lackey_core, validator, do_gateway, get_gateway, analyze_gateway
    global schema_gateway

    # Initialize core components first
    lackey_core = LackeyCore(lackey_dir_path)
    validator = InputValidator()

    # Now initialize the 4 gateways (they can access the global lackey_core)
    do_gateway = LackeyDoGateway()
    get_gateway = LackeyGetGateway()
    analyze_gateway = LackeyAnalyzeGateway()
    schema_gateway = LackeySchemaGateway()

    # Configure rate limiting for gateway endpoints
    _configure_gateway_rate_limiting()

    logger.info(
        f"Lackey core and gateways initialized with data directory: "
        f"{lackey_dir_path}"
    )
    logger.info(
        f"Gateway tool counts: do={len(do_gateway.tool_registry)}, "
        f"get={len(get_gateway.tool_registry)}, "
        f"analyze={len(analyze_gateway.tool_registry)}"
    )
    return mcp_server


def _configure_gateway_rate_limiting() -> None:
    """Configure rate limiting rules for the 3 gateway endpoints."""
    rate_manager = get_rate_limit_manager()

    # lackey_get - read operations (lenient: 120 req/min, burst 20)
    rate_manager.assign_rule_to_endpoint("lackey_get", "lenient")

    # lackey_schema - schema introspection (lenient: 120 req/min, burst 20)
    rate_manager.assign_rule_to_endpoint("lackey_schema", "lenient")

    # lackey_do - write operations (default: 60 req/min, burst 10)
    rate_manager.assign_rule_to_endpoint("lackey_do", "default")

    # lackey_analyze - analysis operations (adaptive: 60 req/min, adaptive behavior)
    rate_manager.assign_rule_to_endpoint("lackey_analyze", "adaptive")


def _ensure_initialized() -> tuple[LackeyCore, InputValidator]:
    """Ensure core components are initialized."""
    if lackey_core is None or validator is None:
        raise RuntimeError("Lackey core not initialized")
    return lackey_core, validator


def _ensure_gateways_initialized() -> (
    tuple[LackeyDoGateway, LackeyGetGateway, LackeyAnalyzeGateway, LackeySchemaGateway]
):
    """Ensure gateway components are initialized."""
    if do_gateway is None or get_gateway is None or analyze_gateway is None:
        raise RuntimeError("Gateway components not initialized")
    if schema_gateway is None:
        raise RuntimeError("Schema gateway not initialized")
    return do_gateway, get_gateway, analyze_gateway, schema_gateway


# Gateway Tool 1: lackey_do - All state-changing operations
@mcp_analytics_tracking()
@mcp_rate_limit(rule_name="default")
@mcp_security_required(validate_input=True)
async def lackey_do(
    action: str,
    data: Optional[Dict[str, Any]] = None,
    target: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
) -> str:
    """Perform state-changing operations on tasks and projects.

    This gateway consolidates ALL state-changing operations into a single
    semantic interface:
    - Create projects, tasks, notes
    - Update project/task information and status
    - Complete tasks and task steps
    - Assign and reassign tasks
    - Archive tasks
    - Add/remove task dependencies
    - Bulk operations for efficiency

    Args:
        action: The action to perform (create, update, complete, assign,
                archive, add, remove, bulk)
        target: The target of the action (project, task, note, dependency,
                steps, status, assignment)
        data: Action-specific data and parameters
        options: Optional settings (atomic, validate, etc.)

    Returns:
        Result of the state-changing operation with confirmation details
    """
    try:
        do_gw, _, _, _ = _ensure_gateways_initialized()

        request = {
            "action": action,
            "target": target,
            "data": data or {},
            "options": options or {},
        }

        result = await do_gw.route_request(request)

        # Debug logging for MCP response
        logger.debug(f"lackey_do: Action={action}, Success={result.success}")
        logger.debug(f"lackey_do: Result content type: {type(result.content)}")
        if hasattr(result.content, "dependencies"):
            logger.debug(
                f"lackey_do: Task dependencies before serialization: "
                f"{result.content.dependencies}"
            )
            logger.debug(f"lackey_do: Task object id: {id(result.content)}")

        target_display = target or ""
        if result.success:
            # Debug the string conversion
            content_str = str(result.content)
            logger.debug(f"lackey_do: Serialized content length: {len(content_str)}")
            if hasattr(result.content, "dependencies"):
                logger.debug(
                    f"lackey_do: Task dependencies after str() conversion: "
                    f"{result.content.dependencies}"
                )
            return (
                f"✅ {action} {target_display} completed successfully\n\n{content_str}"
            )
        else:
            return f"❌ {action} {target_display} failed: {result.content}"

    except Exception as e:
        logger.error(f"lackey_do failed: {e}")
        target_display = target or ""
        return f"Error executing {action} {target_display}: {str(e)}"


# Register the tool
mcp_server.tool(description="Perform state-changing operations on tasks and projects")(
    lackey_do
)


# Gateway Tool 2: lackey_get - All read operations
@mcp_analytics_tracking()
@mcp_rate_limit(rule_name="lenient")
@mcp_security_required(validate_input=True)
async def lackey_get(query: str, context: Optional[Dict[str, Any]] = None) -> str:
    """Retrieve information about tasks, projects, and system status.

    This gateway consolidates ALL read operations into a single semantic interface:
    - Get tasks, projects, status, progress, notes, dependencies
    - Advanced filtering by status, complexity, assignee, tags, date ranges
    - Search functionality with text indexing and ranking
    - Support for pagination and result limiting

    Args:
        query: Natural language query describing what information to retrieve
        context: Additional context for filtering and scoping

    Returns:
        Requested information formatted for readability
    """
    try:
        _, get_gw, _, _ = _ensure_gateways_initialized()

        request = {"query": query, "context": context or {}}

        result = await get_gw.route_request(request)

        if result.success:
            return f"📊 Query Results\n\n{result.content}"
        else:
            return f"❌ Query failed: {result.content}"

    except Exception as e:
        logger.error(f"lackey_get failed: {e}")
        return f"Error executing query: {str(e)}"


# Register the tool
mcp_server.tool(
    description="Retrieve information about tasks, projects, and system status"
)(lackey_get)


# Gateway Tool 3: lackey_schema - Schema introspection
@mcp_analytics_tracking()
@mcp_rate_limit(rule_name="lenient")
@mcp_security_required(validate_input=True)
async def lackey_schema(
    gateway: str, tool: Optional[str] = None, disclosure_level: str = "tier2"
) -> str:
    """Get schema information for gateway tools.

    Provides schema introspection at three disclosure levels:
    - tier1: Required parameters only with basic type information
    - tier2: Required + optional parameters with detailed types
    - tier3: Full schema with constraints, validation rules, examples

    Args:
        gateway: Gateway name (lackey_get, lackey_do, lackey_analyze)
        tool: Specific tool name (optional, returns all tools if not specified)
        disclosure_level: Schema detail level (tier1, tier2, tier3, default: tier2)

    Returns:
        Schema information formatted for the specified disclosure level
    """
    try:
        _, _, _, schema_gateway = _ensure_gateways_initialized()

        if tool:
            # Get schema for specific tool
            result = await schema_gateway.get_tool_schema(
                tool_name=tool,
                gateway_name=gateway if gateway != "all" else None,
                disclosure_level=disclosure_level,
            )
            return _format_tool_schema_response(result)
        else:
            # Get schemas for all tools in gateway
            if gateway == "all":
                result = await schema_gateway.list_available_tools()
                return _format_all_tools_response(result)
            else:
                result = await schema_gateway.get_gateway_schema(
                    gateway_name=gateway, disclosure_level=disclosure_level
                )
                return _format_gateway_schema_response(result)

    except Exception as e:
        logger.error(f"lackey_schema failed: {e}")
        return f"❌ Error retrieving schema: {str(e)}"


# Register the tool
mcp_server.tool(
    description=(
        "Get schema information for gateway tools at specified disclosure levels"
    )
)(lackey_schema)


def _format_tool_schema_response(result: Dict[str, Any]) -> str:
    """Format single tool schema response."""
    tool_name = result["tool_name"]
    gateway = result["gateway"]
    level = result["disclosure_level"]
    schema = result["schema"]

    response = f"📋 Schema for {tool_name} ({gateway} gateway, {level}):\n\n"

    if level == "tier1":
        required = schema.get("required", [])
        types = schema.get("types", {})

        if not required:
            response += "No required parameters"
        else:
            response += "Required parameters:\n"
            for param in required:
                param_type = types.get(param, "value")
                response += f"  • {param}: {param_type}\n"

    elif level == "tier2":
        required = schema.get("required", [])
        optional = schema.get("optional", {})
        types = schema.get("types", {})

        if required:
            response += "Required parameters:\n"
            for param in required:
                param_type = types.get(param, "any")
                response += f"  • {param}: {param_type}\n"

        if optional:
            response += "\nOptional parameters:\n"
            for param, default in optional.items():
                param_type = types.get(param, "any")
                default_str = f" (default: {default})" if default is not None else ""
                response += f"  • {param}: {param_type}{default_str}\n"

    else:  # tier3
        required = schema.get("required", [])
        optional = schema.get("optional", {})
        types = schema.get("types", {})
        constraints = schema.get("constraints", {})

        if required:
            response += "Required parameters:\n"
            for param in required:
                param_type = types.get(param, "any")
                constraint = constraints.get(param, {})
                constraint_str = _format_constraints(constraint)
                response += f"  • {param}: {param_type}{constraint_str}\n"

        if optional:
            response += "\nOptional parameters:\n"
            for param, default in optional.items():
                param_type = types.get(param, "any")
                constraint = constraints.get(param, {})
                constraint_str = _format_constraints(constraint)
                default_str = f" (default: {default})" if default is not None else ""
                response += f"  • {param}: {param_type}{constraint_str}{default_str}\n"

    return response.rstrip()


def _format_gateway_schema_response(result: Dict[str, Any]) -> str:
    """Format gateway schema response."""
    gateway = result["gateway"]
    level = result["disclosure_level"]
    tools = result["tools"]
    tool_count = result["tool_count"]

    response = f"📋 Schema for {gateway} gateway ({level}, {tool_count} tools):\n\n"

    for tool_name, schema in tools.items():
        response += f"**{tool_name}**:\n"

        if level == "tier1":
            required = schema.get("required", [])
            types = schema.get("types", {})

            if not required:
                response += "  No required parameters\n"
            else:
                for param in required:
                    param_type = types.get(param, "value")
                    response += f"  • {param}: {param_type}\n"

        elif level == "tier2":
            required = schema.get("required", [])
            optional = schema.get("optional", {})
            types = schema.get("types", {})

            if required:
                response += "  Required:\n"
                for param in required:
                    param_type = types.get(param, "any")
                    response += f"    • {param}: {param_type}\n"

            if optional:
                response += "  Optional:\n"
                for param, default in optional.items():
                    param_type = types.get(param, "any")
                    default_str = (
                        f" (default: {default})" if default is not None else ""
                    )
                    response += f"    • {param}: {param_type}{default_str}\n"

        else:  # tier3
            required = schema.get("required", [])
            optional = schema.get("optional", {})
            types = schema.get("types", {})
            constraints = schema.get("constraints", {})

            if required:
                response += "  Required:\n"
                for param in required:
                    param_type = types.get(param, "any")
                    constraint = constraints.get(param, {})
                    constraint_str = _format_constraints(constraint)
                    response += f"    • {param}: {param_type}{constraint_str}\n"

            if optional:
                response += "  Optional:\n"
                for param, default in optional.items():
                    param_type = types.get(param, "any")
                    constraint = constraints.get(param, {})
                    constraint_str = _format_constraints(constraint)
                    default_str = (
                        f" (default: {default})" if default is not None else ""
                    )
                    response += (
                        f"    • {param}: {param_type}{constraint_str}{default_str}\n"
                    )

        response += "\n"

    return response.rstrip()


def _format_all_tools_response(result: Dict[str, Any]) -> str:
    """Format response for all available tools."""
    tools_by_gateway = result["tools_by_gateway"]
    total_count = result["total_tool_count"]
    gateway_count = result["gateway_count"]

    response = (
        f"📋 All available tools ({total_count} tools across "
        f"{gateway_count} gateways):\n\n"
    )

    for gateway, tools in tools_by_gateway.items():
        response += f"**{gateway}** ({len(tools)} tools):\n"
        for tool in tools:
            response += f"  • {tool}\n"
        response += "\n"

    return response.rstrip()


def _format_constraints(constraint: Dict[str, Any]) -> str:
    """Format constraint information for display."""
    if not constraint:
        return ""

    parts = []
    if "min_length" in constraint:
        parts.append(f"min_len={constraint['min_length']}")
    if "max_length" in constraint:
        parts.append(f"max_len={constraint['max_length']}")
    if "enum" in constraint:
        values = constraint["enum"]
        if len(values) <= 3:
            parts.append(f"values={values}")
        else:
            parts.append(f"values=[{len(values)} options]")

    return f" ({', '.join(parts)})" if parts else ""


# Gateway Tool 4: lackey_analyze - All analysis operations
@mcp_analytics_tracking()
@mcp_rate_limit(rule_name="adaptive")
@mcp_security_required(validate_input=True)
async def lackey_analyze(
    analysis_type: str, scope: Optional[Dict[str, Any]] = None
) -> str:
    """Perform analysis and provide insights on tasks, projects, and workflows.

    This gateway consolidates ALL analysis operations into a single semantic interface:
    - Dependency analysis with cycle detection and critical path identification
    - Critical path analysis with bottleneck identification and optimization suggestions
    - Blocker analysis with impact assessment and resolution recommendations
    - Timeline analysis with scheduling and milestone identification
    - Workload analysis with capacity planning and resource allocation
    - Integrity analysis with data validation and automatic fixing
    - Health analysis combining multiple metrics
    - Performance analysis with benchmarking

    Args:
        analysis_type: Type of analysis (dependencies, critical_path,
                      blockers, timeline, workload, integrity, health,
                      performance)
        scope: Scope and parameters for the analysis

    Returns:
        Analysis results with insights and recommendations
    """
    try:
        _, _, analyze_gw, _ = _ensure_gateways_initialized()

        request = {"analysis_type": analysis_type, "scope": scope or {}}

        result = await analyze_gw.route_request(request)

        if result.success:
            return f"🔍 Analysis Results\n\n{result.content}"
        else:
            return f"❌ Analysis failed: {result.content}"

    except Exception as e:
        logger.error(f"lackey_analyze failed: {e}")
        return f"Error executing analysis: {str(e)}"


# Register the tool
mcp_server.tool(
    description=(
        "Perform analysis and provide insights on tasks, projects, and workflows"
    )
)(lackey_analyze)


class LackeyMCPServer:
    """Wrapper class for the Gateway-based Lackey MCP server."""

    def __init__(self, lackey_dir_path: str = ".lackey"):
        """Initialize the server wrapper.

        Args:
            lackey_dir_path: Path to the .lackey directory where files are stored
        """
        self.lackey_dir_path = lackey_dir_path
        self.server = create_server(lackey_dir_path)

        logger.info("MCP server wrapper ready for stdio communication")

    async def run(self) -> None:
        """Run the MCP server."""
        await self.server.run_stdio_async()

    async def stop(self) -> None:
        """Stop the MCP server and clean up processes."""
        # Note: ProcessSupervisor has been eliminated as it was not actually
        # tracking any processes. Strand processes are now managed directly
        # via the working ps/kill approach in StrandExecutionBridge.
        logger.info("MCP server stopping")

        # FastMCP handles cleanup automatically
        pass

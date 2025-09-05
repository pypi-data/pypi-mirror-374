#!/usr/bin/env python3
"""Main CLI entry point for Lackey task chain management engine."""

import asyncio
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import click

from . import __version__

if TYPE_CHECKING:
    pass


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version and exit")
@click.pass_context
def main(ctx: click.Context, version: bool) -> None:
    """Lackey - Task chain management engine for AI agents.

    Lackey provides intelligent task dependency management with MCP server
    integration for AI agent collaboration.

    Local docs: src/lackey/docs/
    """
    if version:
        click.echo(f"Lackey {__version__}")
        sys.exit(0)

    # If no command provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command("serve")
@click.option(
    "--workspace",
    "-w",
    default=".lackey",
    help="Workspace directory for Lackey data (default: .lackey)",
)
@click.option(
    "--log-level",
    "-l",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    help="Logging level (default: INFO)",
)
def serve(workspace: str, log_level: str) -> None:
    """Start the Lackey MCP server.

    This starts the MCP (Model Context Protocol) server that enables
    AI agents to interact with Lackey for task management.
    """
    # Create workspace directory if it doesn't exist
    workspace_path = Path(workspace)
    workspace_path.mkdir(parents=True, exist_ok=True)

    click.echo("Starting Lackey MCP server...")
    click.echo(f"Workspace: {workspace_path.resolve()}")
    click.echo(f"Log level: {log_level}")
    click.echo("Server running in stdio mode for MCP compatibility")
    click.echo("Press Ctrl+C to stop")

    # Use the Gateway-based MCP server implementation
    import logging

    from .mcp.server import LackeyMCPServer

    # Set up logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )

    async def run_server() -> None:
        server = LackeyMCPServer(str(workspace_path))
        try:
            await server.run()
        except KeyboardInterrupt:
            logging.info("Received interrupt signal, shutting down...")
            await server.stop()
        except Exception as e:
            logging.error(f"Server error: {e}")
            sys.exit(1)

    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        click.echo("\nServer stopped.")


@main.command("version")
def version() -> None:
    """Show version information."""
    click.echo(f"Lackey {__version__}")


@main.command("doctor")
@click.option("--workspace", "-w", default=".lackey", help="Workspace directory")
def doctor(workspace: str) -> None:
    """Check system requirements and configuration."""
    import platform
    import sys
    from pathlib import Path

    click.echo("🔍 Lackey System Check")
    click.echo("=" * 50)

    # Python version check
    python_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    if sys.version_info >= (3, 10):
        click.echo(f"✅ Python version: {python_version} (compatible)")
    else:
        click.echo(f"❌ Python version: {python_version} (requires 3.10+)")

    # Platform info
    click.echo(f"✅ Platform: {platform.system()} {platform.release()}")

    # Workspace check
    workspace_path = Path(workspace)
    if workspace_path.exists():
        click.echo(f"✅ Workspace exists: {workspace_path.resolve()}")

        # Check workspace structure
        config_file = workspace_path / "config.yaml"
        index_file = workspace_path / "index.yaml"

        if config_file.exists():
            click.echo("✅ Configuration file found")
        else:
            click.echo("⚠️  Configuration file missing (will be created on first use)")

        if index_file.exists():
            click.echo("✅ Project index found")
        else:
            click.echo("⚠️  Project index missing (will be created on first use)")
    else:
        click.echo(f"⚠️  Workspace directory missing: {workspace_path.resolve()}")
        click.echo("   (will be created when running 'lackey serve')")

    # Dependencies check
    try:
        import yaml

        click.echo("✅ PyYAML available")
        del yaml  # Clean up namespace
    except ImportError:
        click.echo("❌ PyYAML missing")

    try:
        import networkx

        click.echo("✅ NetworkX available")
        del networkx  # Clean up namespace
    except ImportError:
        click.echo("❌ NetworkX missing")

    try:
        import mcp

        click.echo("✅ MCP library available")
        del mcp  # Clean up namespace
    except ImportError:
        click.echo("❌ MCP library missing")

    click.echo("\n💡 To start using Lackey:")
    click.echo("1. Use Q CLI to interact with Lackey:")
    click.echo("   q chat --agent developer")
    click.echo("   (The MCP server will start automatically)")


@main.command("init")
@click.option("--name", help="Project name")
@click.option("--description", help="Project description")
@click.option("--workspace", "-w", default=".lackey", help="Workspace directory")
def init(name: str, description: str, workspace: str) -> None:
    """Initialize a new Lackey workspace."""
    workspace_path = Path(workspace)
    workspace_path.mkdir(parents=True, exist_ok=True)

    click.echo(f"🚀 Initializing Lackey workspace at {workspace_path.resolve()}")

    # Basic initialization
    _init_basic_workspace(name, description, workspace_path)

    click.echo("\n🎉 Workspace initialized successfully!")
    click.echo("\nNext steps:")
    click.echo("1. Use Q CLI to interact with Lackey:")
    click.echo("   q chat --agent developer")
    click.echo("   (The MCP server will start automatically)")


def _init_basic_workspace(name: str, description: str, workspace_path: Path) -> None:
    """Initialize a basic workspace without templates."""
    # Create basic config
    config_content = f"""# Lackey Configuration
version: "0.1.0"
workspace_name: "{name or 'Lackey Workspace'}"
description: "{description or 'A Lackey task management workspace'}"
created_at: "{workspace_path.resolve()}"

# Task management settings
task_settings:
  auto_assign_ids: true
  require_success_criteria: true
  default_complexity: "medium"

# Agent settings
agent_settings:
  create_agents: true
  default_roles: ["manager", "developer"]

# Validation settings
validation:
  level: "basic"
  strict_mode: false
"""

    config_file = workspace_path / "config.yaml"
    with open(config_file, "w") as f:
        f.write(config_content)

    # Create lackey.config with AWS profile setting
    from lackey.config.config_manager import LackeyConfig

    lackey_config = LackeyConfig(str(workspace_path.parent))
    lackey_config.create_default_config()

    click.echo("✅ Created lackey.config with AWS profile settings")

    # Create basic index
    index_content = """# Project Index
projects: []
"""

    index_file = workspace_path / "index.yaml"
    with open(index_file, "w") as f:
        f.write(index_content)

    # Create Amazon Q rules directory and files
    rules_dir = workspace_path.parent / ".amazonq" / "rules"
    agents_dir = workspace_path.parent / ".amazonq" / "cli-agents"
    rules_dir.mkdir(parents=True, exist_ok=True)
    agents_dir.mkdir(parents=True, exist_ok=True)

    # Copy rule files from builtin templates
    builtin_rules_dir = Path(__file__).parent / "builtin_templates" / "rules"
    if builtin_rules_dir.exists():
        for rule_file in builtin_rules_dir.glob("*.md"):
            target_file = rules_dir / rule_file.name
            with open(rule_file, "r", encoding="utf-8") as src:
                content = src.read()
            with open(target_file, "w", encoding="utf-8") as dst:
                dst.write(content)

    # Copy and convert agent templates to JSON format
    builtin_templates_dir = Path(__file__).parent / "builtin_templates"
    if builtin_templates_dir.exists():
        import json

        import yaml

        for agent_file in builtin_templates_dir.glob("*.yaml"):
            with open(agent_file, "r", encoding="utf-8") as f:
                agent_template = yaml.safe_load(f)

            # Skip if not an agent template
            if agent_template.get("template_type") != "agent":
                continue

            # Extract agent name from template
            agent_name = agent_template.get("name", agent_file.stem)

            # Extract the JSON content from the template files section
            files = agent_template.get("files", {})

            # Look for the template file key (should be "{{agent_name}}.json")
            json_content = None

            for file_key, content in files.items():
                if file_key.endswith(".json") and "{{agent_name}}" in file_key:
                    json_content = content
                    break

            if json_content:
                # Replace template variables with actual values
                json_content = json_content.replace("{{agent_name}}", agent_name)

                try:
                    # Parse the JSON content directly from the template
                    agent_config = json.loads(json_content)
                except json.JSONDecodeError as e:
                    click.echo(f"⚠️  Failed to parse JSON for {agent_name}: {e}")
                    continue
            else:
                click.echo(f"⚠️  No JSON template found for {agent_name}")
                continue

            # Write JSON config file
            target_file = agents_dir / f"{agent_name}.json"
            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(agent_config, f, indent=2)

    click.echo("✅ Created workspace configuration")
    click.echo("✅ Created project index")
    click.echo("✅ Created Q agent templates")
    click.echo("✅ Created Q agent rules")


def _generate_request_schema(gateway_name: str, tool_name: str, tool_info: dict) -> str:
    """Generate request schema for a tool."""
    required = tool_info.get("required", [])
    optional = tool_info.get("optional", {})

    # Build parameter structure
    params = {}
    for param in required:
        params[param] = f"<{param}>"
    for param in optional:
        params[param] = f"<{param}> (optional)"

    # Format based on gateway type
    if gateway_name == "lackey_get":
        if params:
            return f'lackey_get(query="{tool_name}", context={params})'
        else:
            return f'lackey_get(query="{tool_name}")'
    elif gateway_name == "lackey_do":
        # Extract resource ID parameter
        resource_param = None
        for param in ["project_id", "task_id", "execution_id", "template_id"]:
            if param in params:
                resource_param = param
                break

        if resource_param:
            target_value = params.pop(resource_param)
            if params:
                return (
                    f'lackey_do(action="{tool_name}", target={target_value}, '
                    f"data={params})"
                )
            else:
                return f'lackey_do(action="{tool_name}", target={target_value})'
        else:
            if params:
                return (
                    f'lackey_do(action="{tool_name}", target="<resource-id>", '
                    f"data={params})"
                )
            else:
                return f'lackey_do(action="{tool_name}", target="<resource-id>")'
    elif gateway_name == "lackey_analyze":
        if params:
            return f'lackey_analyze(analysis_type="{tool_name}", scope={params})'
        else:
            return f'lackey_analyze(analysis_type="{tool_name}")'

    return f"{gateway_name}({params})"


@main.command("schema")
def schema() -> None:
    """Dump the complete API schema for all Lackey MCP gateways."""
    import logging

    # Suppress debug logging for cleaner output
    logging.getLogger().setLevel(logging.WARNING)

    from .mcp.gateways.lackey_schema import LackeySchemaGateway

    schema_gateway = LackeySchemaGateway()

    try:
        gateways = ["lackey_get", "lackey_do", "lackey_analyze"]

        for gateway_name in gateways:
            gateway_schema = asyncio.run(
                schema_gateway.get_gateway_schema(
                    gateway_name=gateway_name, disclosure_level="tier3"
                )
            )

            click.echo(f"GATEWAY: {gateway_name}")
            click.echo("=" * 50)

            tools = gateway_schema.get("tools", {})
            for tool_name, tool_info in tools.items():
                click.echo(f"\nTOOL: {tool_name}")

                def format_param_type(
                    param_name: str, param_type: str, tool_schema: dict
                ) -> str:
                    """Format parameter type with enum values if applicable."""
                    if param_type != "enum":
                        return param_type

                    # Look for validator in constraints
                    constraints = tool_schema.get("constraints", {}).get(param_name, {})
                    validator = constraints.get("validator")

                    # Map known validators to their enum values
                    validator_enums = {
                        "validate_note_type": [
                            "user",
                            "system",
                            "status_change",
                            "assignment",
                            "progress",
                            "dependency",
                            "archive",
                        ],
                        "validate_status": ["todo", "in_progress", "blocked", "done"],
                        "validate_complexity": ["low", "medium", "high"],
                    }

                    if validator in validator_enums:
                        enum_values = validator_enums[validator]
                        return f"enum[{', '.join(enum_values)}]"
                    else:
                        return "enum"

                required = tool_info.get("required", [])
                if required:
                    req_params = []
                    types = tool_info.get("types", {})
                    for param in required:
                        param_type = types.get(param, "unknown")
                        formatted_type = format_param_type(param, param_type, tool_info)
                        req_params.append(f"{param}({formatted_type})")
                    click.echo(f"REQUIRED: {', '.join(req_params)}")
                else:
                    click.echo("REQUIRED: none")

                optional = tool_info.get("optional", {})
                if optional:
                    opt_params = []
                    types = tool_info.get("types", {})
                    for param, default in optional.items():
                        param_type = types.get(param, "unknown")
                        formatted_type = format_param_type(param, param_type, tool_info)
                        if default is not None:
                            opt_params.append(
                                f"{param}({formatted_type}, default: {default})"
                            )
                        else:
                            opt_params.append(f"{param}({formatted_type})")
                    click.echo(f"OPTIONAL: {', '.join(opt_params)}")
                else:
                    click.echo("OPTIONAL: none")

                # Add request schema
                schema = _generate_request_schema(gateway_name, tool_name, tool_info)
                click.echo(f"REQUEST: {schema}")

            click.echo(f"\nTOOL_COUNT: {len(tools)}")
            click.echo()

        click.echo(f"TOTAL_GATEWAYS: {len(gateways)}")

    except Exception as e:
        click.echo(f"❌ Error retrieving schema: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

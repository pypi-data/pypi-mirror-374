"""Generated execution template for Strands Graph-based task execution.

This module provides the execution environment for Lackey Strand graphs,
managing task dependencies, agent creation, and real-time monitoring.
"""

# mypy: ignore-errors
# This is a template file with placeholder variables that get replaced during
# code generation

# Generated Strands Graph execution template
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import boto3
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.multiagent import GraphBuilder
from strands_tools import editor, file_read

# Bypass tool consent prompts for automated execution
os.environ["BYPASS_TOOL_CONSENT"] = "true"

# Import pipe communication system
try:
    from lackey.strands.execute.pipe_communication import get_pipe_writer_from_args

    pipe_writer = get_pipe_writer_from_args()
    # We'll log pipe writer status after setting up logging functions
except ImportError as e:
    print(f"FATAL: Cannot import pipe communication module: {e}")
    print(
        "This indicates the lackey module is not available in the current "
        "Python environment."
    )
    sys.exit(1)
except Exception as e:
    print(f"FATAL: Failed to initialize pipe writer: {e}")
    print("Pipe communication is required for execution monitoring.")
    sys.exit(1)

# Verify pipe writer was created successfully
if pipe_writer is None:
    print(
        "FATAL: Pipe writer is None - no --status-pipe argument provided or pipe setup "
        "failed"
    )
    print("Real-time execution monitoring requires pipe communication.")
    sys.exit(1)

# Type assertion since we've verified pipe_writer is not None
assert pipe_writer is not None  # nosec B101 - null check assert for type safety

# Setup pipe-only logging - all output goes through named pipe
execution_id = "__EXECUTION_ID__"

# Send execution metadata if pipe available
if pipe_writer:
    metadata = {}
    metadata["execution_id"] = execution_id
    metadata["python_executable"] = sys.executable
    metadata["working_directory"] = os.getcwd()
    metadata["bypass_tool_consent"] = os.environ.get("BYPASS_TOOL_CONSENT", "NOT_SET")
    pipe_writer.send_execution_metadata_update(metadata)


# Simple logging functions that send directly to pipe
def log_debug_message(message: str, task_id: Optional[str] = None) -> None:
    """Send debug message via pipe."""
    try:
        pipe_writer.send_log_to_pipe("DEBUG", message, task_id)
    except Exception as e:
        print(f"FATAL: Failed to send debug message via pipe: {e}")
        sys.exit(1)


def log_info_message(message: str, task_id: Optional[str] = None) -> None:
    """Send info message via pipe."""
    try:
        pipe_writer.send_log_to_pipe("INFO", message, task_id)
    except Exception as e:
        print(f"FATAL: Failed to send info message via pipe: {e}")
        sys.exit(1)


def log_warning_message(message: str, task_id: Optional[str] = None) -> None:
    """Send warning message via pipe."""
    try:
        pipe_writer.send_log_to_pipe("WARNING", message, task_id)
    except Exception as e:
        print(f"FATAL: Failed to send warning message via pipe: {e}")
        sys.exit(1)


def log_error_message(message: str, task_id: Optional[str] = None) -> None:
    """Send error message via pipe."""
    try:
        pipe_writer.send_log_to_pipe("ERROR", message, task_id)
    except Exception as e:
        print(f"FATAL: Failed to send error message via pipe: {e}")
        sys.exit(1)


# Now log pipe writer status using proper logging
log_info_message(
    "Pipe writer initialized for execution " + str(pipe_writer.execution_id)
)

# Initialize execution
log_info_message("Starting strands execution " + str(execution_id))
log_info_message("Python executable: " + str(sys.executable))
log_info_message("Current working directory: " + str(os.getcwd()))
log_info_message(
    "BYPASS_TOOL_CONSENT: " + str(os.environ.get("BYPASS_TOOL_CONSENT", "NOT_SET"))
)
log_debug_message("Environment variables loaded")
log_info_message("=" * 50)

__SESSION_SETUP__  # noqa: F821

# Define a default session if none was configured above
if "session" not in locals() and "session" not in globals():
    session = boto3.Session()

# Task execution mapping
task_mapping = __TASK_MAPPING__  # noqa: F821

# Task dependencies mapping
dependencies = __DEPENDENCIES__  # noqa: F821


def load_cost_configuration() -> Dict[str, Dict[str, float]]:
    """Load cost configuration from lackey config file."""
    import configparser

    config = configparser.ConfigParser()
    # Use absolute path to lackey config in current working directory
    config_path = Path.cwd() / ".lackey" / "lackey.config"

    if config_path.exists():
        config.read(config_path)
        if "cost_tracking" in config:
            return {
                "us.anthropic.claude-3-7-sonnet-20250219-v1:0": {
                    "input_cost": config.getfloat(
                        "cost_tracking", "claude_3_7_sonnet_input_cost", fallback=0.0
                    ),
                    "output_cost": config.getfloat(
                        "cost_tracking", "claude_3_7_sonnet_output_cost", fallback=0.0
                    ),
                },
                "us.anthropic.claude-sonnet-4-20250514-v1:0": {
                    "input_cost": config.getfloat(
                        "cost_tracking", "claude_sonnet_4_input_cost", fallback=0.0
                    ),
                    "output_cost": config.getfloat(
                        "cost_tracking", "claude_sonnet_4_output_cost", fallback=0.0
                    ),
                },
                "us.anthropic.claude-opus-4-1-20250805-v1:0": {
                    "input_cost": config.getfloat(
                        "cost_tracking", "claude_opus_4_1_input_cost", fallback=0.0
                    ),
                    "output_cost": config.getfloat(
                        "cost_tracking", "claude_opus_4_1_output_cost", fallback=0.0
                    ),
                },
            }

    # Return zero costs if config not found - don't hide missing data
    return {
        "us.anthropic.claude-3-7-sonnet-20250219-v1:0": {
            "input_cost": 0.0,
            "output_cost": 0.0,
        },
        "us.anthropic.claude-sonnet-4-20250514-v1:0": {
            "input_cost": 0.0,
            "output_cost": 0.0,
        },
        "us.anthropic.claude-opus-4-1-20250805-v1:0": {
            "input_cost": 0.0,
            "output_cost": 0.0,
        },
    }


COST_CONFIG = load_cost_configuration()


def calculate_execution_cost(
    model_id: str, input_tokens: int, output_tokens: int, task_id: Optional[str] = None
) -> float:
    """Calculate cost for a task based on token usage."""
    if model_id not in COST_CONFIG:
        log_warning_message(
            "Unknown model " + str(model_id) + " for cost calculation", task_id
        )
        return 0.0

    config = COST_CONFIG[model_id]
    input_cost = (input_tokens / 1000) * config["input_cost"]
    output_cost = (output_tokens / 1000) * config["output_cost"]
    total_cost = input_cost + output_cost

    log_info_message("Task cost breakdown:", task_id)
    log_info_message("  Model: " + str(model_id), task_id)
    log_info_message(
        "  Input tokens: "
        + str(input_tokens)
        + " ("
        + str(round(input_cost, 4))
        + " USD)",
        task_id,
    )
    log_info_message(
        "  Output tokens: "
        + str(output_tokens)
        + " ("
        + str(round(output_cost, 4))
        + " USD)",
        task_id,
    )
    log_info_message("  Total cost: " + str(round(total_cost, 4)) + " USD", task_id)

    # Send cost update via pipe if available
    if task_id:
        send_cost_to_pipe(task_id, model_id, input_tokens, output_tokens, total_cost)

    return total_cost


def update_task_execution_status(task_id: str, status: str, message: str = "") -> None:
    """Send real-time task status update via named pipe."""
    try:
        pipe_writer.send_task_status_update(task_id, status, message)
        log_info_message(
            "Sent status update via pipe: task "
            + str(task_id[:8])
            + " -> "
            + str(status)
        )
    except Exception as e:
        print(
            f"FATAL: Failed to send status update via pipe for task {task_id[:8]}: {e}"
        )
        sys.exit(1)


def send_log_to_pipe(level: str, message: str, task_id: Optional[str] = None) -> None:
    """Send log message via pipe."""
    try:
        pipe_writer.send_log_to_pipe(level, message, task_id)
    except Exception as e:
        print(f"FATAL: Failed to send log message via pipe: {e}")
        sys.exit(1)


def send_task_progress_to_pipe(task_id: str, progress: float, step: str = "") -> None:
    """Send progress update via pipe."""
    try:
        pipe_writer.send_task_progress_update(task_id, progress, step)
    except Exception as e:
        print(f"FATAL: Failed to send progress update via pipe: {e}")
        sys.exit(1)


def send_error_to_pipe(
    task_id: str,
    error_type: str,
    error_message: str,
    traceback_info: Optional[str] = None,
) -> None:
    """Send error report via pipe."""
    try:
        pipe_writer.send_error_to_pipe(
            task_id, error_type, error_message, traceback_info
        )
    except Exception as e:
        print(f"FATAL: Failed to send error report via pipe: {e}")
        sys.exit(1)


def send_cost_to_pipe(
    task_id: str, model_id: str, input_tokens: int, output_tokens: int, cost: float
) -> None:
    """Send cost update via pipe."""
    try:
        pipe_writer.send_cost_to_pipe(
            task_id, model_id, input_tokens, output_tokens, cost
        )
    except Exception as e:
        print(f"FATAL: Failed to send cost update via pipe: {e}")
        sys.exit(1)


def send_completion_to_pipe(
    task_id: str, status: str, result: str, execution_time: float
) -> None:
    """Send task completion via pipe."""
    try:
        pipe_writer.send_completion_to_pipe(task_id, status, result, execution_time)
    except Exception as e:
        print(f"FATAL: Failed to send task completion via pipe: {e}")
        sys.exit(1)


def select_model_by_complexity(complexity: str) -> str:
    """Get appropriate model based on task complexity."""
    complexity_models = {
        "low": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "medium": "us.anthropic.claude-sonnet-4-20250514-v1:0",
        "high": "us.anthropic.claude-opus-4-1-20250805-v1:0",
    }
    return complexity_models.get(
        complexity.lower(), "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    )


def create_agent_for_task(task_id: str, task_info: Dict[str, Any]) -> Agent:
    """Create an agent for a specific task with complexity-based model selection."""
    model_id = select_model_by_complexity(task_info.get("complexity", "medium"))

    # Build comprehensive system prompt with all available context
    system_prompt_parts = [
        "You are an autonomous agent with a critical mission: complete the "
        "assigned task with absolute precision and full compliance.",
        "",
        "MISSION: " + str(task_info["title"]),
        "OBJECTIVE: " + str(task_info["objective"]),
        "",
    ]

    # Add mandatory steps with strong language
    steps = task_info.get("steps", [])
    if steps:
        system_prompt_parts.append(
            "MANDATORY EXECUTION STEPS - You MUST complete ALL steps in exact order:"
        )
        for i, step in enumerate(steps, 1):
            system_prompt_parts.append(str(i) + ". " + str(step))
        system_prompt_parts.append("")

    # Add success criteria with compliance emphasis
    success_criteria = task_info.get("success_criteria", [])
    if success_criteria:
        system_prompt_parts.append(
            "ACCEPTANCE CRITERIA - You MUST satisfy EVERY criterion without exception:"
        )
        for criterion in success_criteria:
            system_prompt_parts.append("✓ " + str(criterion))
        system_prompt_parts.append("")

    # Add compliance requirements
    system_prompt_parts.extend(
        [
            "COMPLIANCE REQUIREMENTS:",
            "• You MUST make actual modifications, not just claim compliance",
            "• You MUST verify your work by re-reading files after changes",
            "• You MUST continue until ALL criteria are satisfied",
            "• FAILURE to meet any criterion is unacceptable",
            "",
        ]
    )

    system_prompt_parts.append("Execute with precision. Compliance is mandatory.")

    system_prompt = "\\n\\n".join(system_prompt_parts)

    # Debug: Print the exact system prompt being sent to agent
    log_debug_message("Creating agent for task " + str(task_id[:8]), task_id)
    log_debug_message("System prompt:", task_id)
    log_debug_message("=" * 80, task_id)
    log_debug_message(system_prompt, task_id)
    log_debug_message("=" * 80, task_id)

    log_debug_message(
        "Creating BedrockModel for "
        + str(task_id[:8])
        + " with model_id: "
        + str(model_id),
        task_id,
    )
    try:
        model = BedrockModel(
            model_id=model_id,
            max_tokens=4096,  # Increase output token limit for file operations
            streaming=False,  # Disable streaming for autonomous execution
            boto_session=session,
        )
        log_debug_message(
            "BedrockModel created successfully for " + str(task_id[:8]), task_id
        )
    except Exception as e:
        log_error_message(
            "BedrockModel creation failed for " + str(task_id[:8]) + ": " + str(e),
            task_id,
        )
        raise

    log_debug_message("Creating Agent for " + str(task_id[:8]) + "...", task_id)
    try:
        agent = Agent(
            name="task_" + str(task_id[:8]),
            system_prompt=system_prompt,
            model=model,
            tools=[file_read, editor],  # Use editor exclusively for precision
        )
        log_debug_message("Agent created successfully for " + str(task_id[:8]), task_id)
        return agent
    except Exception as e:
        log_error_message(
            "Agent creation failed for " + str(task_id[:8]) + ": " + str(e), task_id
        )
        raise


def build_execution_graph() -> Any:
    """Build the Strands Graph from task mapping and dependencies."""
    log_info_message("Starting graph build with " + str(len(task_mapping)) + " tasks")
    builder = GraphBuilder()

    # Hardcoded node creation for easy review and debugging
    __HARDCODED_NODES__  # noqa: F821

    log_info_message("All agents created, adding edges...")
    # Hardcoded edge creation for easy review and debugging
    __HARDCODED_EDGES__  # noqa: F821

    log_info_message("Building final graph...")
    # Entry points are auto-detected by GraphBuilder
    try:
        graph = builder.build()
        log_info_message("Graph build completed successfully")
        return graph
    except Exception as e:
        log_error_message("Graph build failed: " + str(e))
        raise


# Execute the graph
if __name__ == "__main__":
    log_info_message("Starting execution script...")
    log_info_message("Building Strands Graph...")
    try:
        graph = build_execution_graph()
        log_info_message("Graph built successfully")
    except Exception as e:
        log_error_message("Graph build failed: " + str(e))
        import traceback

        log_error_message(traceback.format_exc())
        sys.exit(1)

    log_info_message("Executing Graph with task-specific prompts...")
    # Use task-specific prompt instead of generic one
    if len(task_mapping) == 1:
        # Single task - use specific task context
        task_info = list(task_mapping.values())[0]
        execution_prompt = (
            "Execute this task: "
            + str(task_info["title"])
            + ". "
            + str(task_info["objective"])
        )
    else:
        # Multiple tasks - use project-level prompt
        execution_prompt = "Execute all project tasks with proper dependency resolution"

    log_info_message(
        "Starting graph execution with prompt: " + str(execution_prompt[:100]) + "..."
    )

    # Send in_progress status for all tasks before execution starts
    for task_id, task_info in task_mapping.items():
        task_title = task_info.get("title", "Unknown Task")
        update_task_execution_status(
            task_id=task_id,
            status="in_progress",
            message=f"Task '{task_title}' started",
        )

    try:
        result = graph(execution_prompt)
        log_info_message("Graph execution returned with status: " + str(result.status))

        # Send real-time status updates for each completed task
        for node_id, node_result in result.results.items():
            task_status = "done" if node_result.status.name == "COMPLETED" else "failed"
            task_info = task_mapping.get(node_id, {})
            task_title = task_info.get("title", "Unknown Task")

            # Send status update via pipe
            update_task_execution_status(
                task_id=node_id,
                status=task_status,
                message="Task '" + str(task_title) + "' " + str(task_status),
            )

            # Send task completion with result
            if hasattr(node_result, "result") and node_result.result:
                execution_time = getattr(node_result, "execution_time", 0)
                send_completion_to_pipe(
                    task_id=node_id,
                    status=task_status,
                    result=str(node_result.result),
                    execution_time=execution_time,
                )

        # Calculate and log total cost
        total_input_tokens = 0
        total_output_tokens = 0
        total_cost = 0.0

        for node_id, node_result in result.results.items():
            if hasattr(node_result, "result") and hasattr(
                node_result.result, "metrics"
            ):
                metrics = node_result.result.metrics
                if hasattr(metrics, "accumulated_usage") and metrics.accumulated_usage:
                    usage = metrics.accumulated_usage

                    input_tokens = usage.get("inputTokens", 0) or 0
                    output_tokens = usage.get("outputTokens", 0) or 0

                    if input_tokens > 0 or output_tokens > 0:
                        total_input_tokens += input_tokens
                        total_output_tokens += output_tokens

                        # Get model for this task
                        task_info = task_mapping.get(node_id, {})
                        model_id = select_model_by_complexity(
                            task_info.get("complexity", "medium")
                        )
                        task_cost = calculate_execution_cost(
                            model_id, input_tokens, output_tokens, node_id
                        )
                        total_cost += task_cost

        if total_cost > 0:
            log_info_message("EXECUTION SUMMARY:")
            log_info_message("  Total input tokens: " + str(total_input_tokens))
            log_info_message("  Total output tokens: " + str(total_output_tokens))
            log_info_message(
                "  Total estimated cost: $" + str(round(total_cost, 4)) + " USD"
            )

    except Exception as e:
        log_error_message("Graph execution failed: " + str(e))
        import traceback

        log_error_message(traceback.format_exc())
        sys.exit(1)

    log_info_message("Graph execution completed with status: " + str(result.status))

    # Convert GraphResult to Lackey format - agents return results,
    # executor manages state
    lackey_results = {
        "status": "done" if result.status.name == "COMPLETED" else "failed",
        "node_results": {},
    }

    # Process each node result - just pass through agent results
    for node_id, node_result in result.results.items():
        lackey_results["node_results"][node_id] = {
            "status": ("done" if node_result.status.name == "COMPLETED" else "failed"),
            "result": str(node_result.result) if node_result.result else "",
            "output": str(node_result.result) if node_result.result else "",
            "execution_time": getattr(node_result, "execution_time", 0),
        }

    print("LACKEY_RESULTS: " + json.dumps(lackey_results))

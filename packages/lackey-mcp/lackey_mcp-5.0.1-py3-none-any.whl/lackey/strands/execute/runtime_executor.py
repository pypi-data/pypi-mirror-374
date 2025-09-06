"""Simplified runtime execution engine using Strands Graph pattern."""

import json
import logging
import os
import subprocess  # nosec B404 - Required for runtime execution, used safely

# with shell=False and input validation
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..execute.pipe_communication import (
    MessageType,
    PipeMessage,
    PipeReader,
    create_pipe_communication,
)

# Security Note: subprocess is used with strict input validation, shell=False,
# and argument sanitization. All subprocess calls go through _secure_subprocess_run()
# which validates inputs and prevents shell injection

logger = logging.getLogger(__name__)


def _validate_command_args(cmd: List[str]) -> bool:
    """
    Validate command arguments for security against shell injection and other attacks.

    This function prevents B603 violations by ensuring:
    - All arguments are strings
    - No shell metacharacters are present (except in pip package version specs)
    - No null bytes or control characters
    - Reasonable length limits
    """
    logger.debug(f"_validate_command_args: Starting validation for command: {cmd}")
    if not cmd or not isinstance(cmd, list):
        logger.debug(
            f"_validate_command_args: Failed - command is not a non-empty list: "
            f"cmd={cmd}, type={type(cmd)}"
        )
        return False

    # Check that all arguments are strings
    if not all(isinstance(arg, str) for arg in cmd):
        non_strings = [
            f"arg[{i}]={arg} (type: {type(arg)})"
            for i, arg in enumerate(cmd)
            if not isinstance(arg, str)
        ]
        logger.debug(
            f"_validate_command_args: Failed - non-string arguments found: "
            f"{non_strings}"
        )
        return False

    # Check for dangerous shell metacharacters
    dangerous_chars = [
        ";",
        "&",
        "|",
        "`",
        "$",
        "(",
        ")",
        "{",
        "}",
        "*",
        "?",
        "[",
        "]",
        "~",
    ]

    # Special handling for pip install commands - allow < > in version specs
    is_pip_install = len(cmd) >= 2 and cmd[0].endswith("/pip") and cmd[1] == "install"

    for i, arg in enumerate(cmd):
        logger.debug(
            f"_validate_command_args: Checking argument {i}: '{arg}' "
            f"(length: {len(arg)})"
        )

        # Check for null bytes and control characters
        if "\x00" in arg:
            logger.debug(
                f"_validate_command_args: Failed - null byte found in argument "
                f"{i}: '{arg}'"
            )
            return False
        control_chars = [c for c in arg if ord(c) < 32 and c not in ["\t", "\n", "\r"]]
        if control_chars:
            control_hex = [f"\\x{ord(c):02x}" for c in control_chars]
            logger.debug(
                f"_validate_command_args: Failed - control characters found in "
                f"argument {i}: {control_hex}"
            )
            return False

        # Check for dangerous characters
        chars_to_check = dangerous_chars.copy()

        # For pip install commands, allow < > in package arguments
        if is_pip_install and i >= 2:
            # Remove < > from dangerous chars for package version specs
            chars_to_check = [c for c in chars_to_check if c not in ["<", ">"]]
            logger.debug(
                f"_validate_command_args: Allowing < > in pip package " f"argument {i}"
            )

        found_dangerous = [char for char in chars_to_check if char in arg]
        if found_dangerous:
            logger.debug(
                f"_validate_command_args: Failed - dangerous characters found "
                f"in argument {i}: {found_dangerous}"
            )
            return False

        # Reasonable length limit to prevent buffer overflow attacks
        if len(arg) > 4096:
            logger.debug(
                f"_validate_command_args: Failed - argument {i} too long: "
                f"{len(arg)} > 4096"
            )
            return False

    # Limit total number of arguments
    if len(cmd) > 100:
        logger.debug(
            f"_validate_command_args: Failed - too many arguments: {len(cmd)} > 100"
        )
        return False

    logger.debug(f"_validate_command_args: Passed - command is valid: {cmd}")
    return True


def _secure_subprocess_run(
    cmd: List[str], **kwargs: Any
) -> subprocess.CompletedProcess[bytes]:
    """Securely execute subprocess with input validation."""
    logger.debug(f"_secure_subprocess_run: Received command: {cmd}")
    logger.debug(f"_secure_subprocess_run: Command type: {type(cmd)}")
    logger.debug(
        f"_secure_subprocess_run: Command length: "
        f"{len(cmd) if isinstance(cmd, list) else 'N/A'}"
    )

    # Validate command arguments
    if not _validate_command_args(cmd):
        logger.error(f"_secure_subprocess_run: Validation failed for command: {cmd}")
        raise ValueError("Invalid or unsafe command arguments")
    logger.debug(f"_secure_subprocess_run: Validation passed for command: {cmd}")

    # Ensure shell=False for security (addressing B603)
    kwargs["shell"] = False  # This explicitly prevents shell injection attacks

    # Log the secure execution
    logger.debug(f"Executing secure subprocess: {' '.join(cmd)}")

    # Execute with validation - safe because shell=False is enforced above
    return subprocess.run(
        cmd, **kwargs
    )  # nosec B603 - Safe: shell=False enforced, cmd validated, no user input


# Exception classes
class DependencyError(Exception):
    """Raised when there are dependency-related issues."""

    pass


class ExecutionError(Exception):
    """Raised when execution fails."""

    pass


class NodeExecutionError(Exception):
    """Raised when a specific node execution fails."""

    pass


class ResourceLimitError(Exception):
    """Raised when resource limits are exceeded."""

    pass


# Data classes
class ExecutionContext:
    """Context for execution."""

    def __init__(self, execution_id: str, **kwargs: Any) -> None:
        """Initialize execution context.

        Args:
            execution_id: Unique identifier for this execution.
            **kwargs: Additional context parameters.
        """
        self.execution_id = execution_id
        self.kwargs = kwargs


class NodeExecutionResult:
    """Result of node execution."""

    def __init__(self, node_id: str, status: str, result: Any = None):
        """Initialize a node execution result.

        Args:
            node_id: The ID of the executed node.
            status: The status of the execution.
            result: Optional result data.
        """
        self.node_id = node_id
        self.status = status
        self.result = result


class GraphExecutionService:
    """Simplified runtime executor using Strands Graph for dependency management."""

    def __init__(self, storage: Any, lackey_dir: Path):
        """Initialize the simplified runtime executor.

        Args:
            storage: Storage backend for tasks and projects.
            lackey_dir: Path to the lackey directory.
        """
        self.storage = storage
        self.lackey_dir = lackey_dir
        self.execution_id: Optional[str] = None
        self.pipe_reader: Optional[PipeReader] = None
        self.pipe_path: Optional[str] = None
        self.executor_logger: Optional[logging.Logger] = None

        # Execution tracking for history
        self.execution_start_time: Optional[datetime] = None
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.model_id: Optional[str] = None
        self.task_count = 0
        self.completed_tasks = 0

        logger.debug(
            f"StrandsGraphRuntimeExecutor initialized with lackey_dir={lackey_dir}"
        )

    def _setup_executor_logger(self, execution_id: str) -> Path:
        """Set up dedicated logger for this executor instance."""
        # Create logs directory
        logs_dir = self.lackey_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        # Create log file path
        log_file = logs_dir / f"executor_{execution_id}.log"

        # Create dedicated logger for this execution
        logger_name = f"executor_{execution_id}"
        self.executor_logger = logging.getLogger(logger_name)
        self.executor_logger.setLevel(logging.DEBUG)

        # Clear any existing handlers
        self.executor_logger.handlers.clear()

        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"
        )
        file_handler.setFormatter(formatter)

        # Add handler to logger
        self.executor_logger.addHandler(file_handler)

        # Prevent propagation to root logger
        self.executor_logger.propagate = False

        logger.info(f"Created executor log file: {log_file}")
        self.executor_logger.info(
            f"Executor logging initialized for execution {execution_id}"
        )

        return log_file

    def execute_graph_template(
        self, template_path: str, execution_id: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute strand template using Strands Graph pattern."""
        self.execution_id = execution_id
        # Store template path for dependency order lookup in result processing
        self._current_template_path = template_path

        # Initialize execution tracking
        self.execution_start_time = datetime.utcnow()
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.model_id = None
        self.task_count = 0
        self.completed_tasks = 0

        logger.debug(
            f"Starting strand template execution: "
            f"execution_id={execution_id}, template_path={template_path}"
        )
        logger.info(f"GRAPH_EXECUTOR: Starting execution {execution_id}")
        logger.info(f"GRAPH_EXECUTOR: Template path: {template_path}")

        # Set up dedicated executor logger - fail if this doesn't work
        log_file = self._setup_executor_logger(execution_id)
        logger.info(f"Executor logging setup complete: {log_file}")

        # Create pipe communication for real-time updates
        try:
            self.pipe_reader, self.pipe_path = create_pipe_communication(execution_id)
            logger.info(f"Created pipe communication: {self.pipe_path}")

            # Register message handlers
            self._register_message_handlers()

            # Start monitoring
            self.pipe_reader.start_monitoring()
            logger.info(f"Started pipe monitoring for execution {execution_id}")

        except Exception as e:
            logger.error(f"Failed to setup pipe communication: {e}")
            # Continue without real-time updates
            self.pipe_reader = None
            self.pipe_path = None

        try:
            # Execute the Strands Graph template
            logger.debug(f"About to execute template, pipe_path = {self.pipe_path}")
            result = self._execute_graph_template(template_path)
            logger.debug(f"Template execution completed, pipe_path = {self.pipe_path}")

            # Process results and update Lackey tasks (for any remaining updates)
            logger.debug(f"Processing graph results for execution {execution_id}")
            self._process_graph_results(result)

            final_result = {
                "execution_id": execution_id,
                "status": (
                    "completed" if result.get("status") == "completed" else "failed"
                ),
                "node_results": result.get("node_results", {}),
                "execution_time": result.get("execution_time", 0),
            }

            logger.debug(
                f"execute_graph_template: Strand template execution completed "
                f"successfully: {final_result}"
            )
            return final_result

        except Exception as e:
            logger.error(f"GRAPH_EXECUTOR: Execution failed: {e}")
            logger.debug("Strand template execution exception details", exc_info=True)
            return {
                "execution_id": execution_id,
                "status": "failed",
                "error": str(e),
                "node_results": {},
            }
        finally:
            # Clean up pipe communication
            self._cleanup_pipe_communication()

    def _execute_graph_template(self, template_path: str) -> Dict[str, Any]:
        """Execute the Strands Graph template and capture results."""
        logger.debug(
            f"Starting graph template execution: "
            f"template_path={template_path}, pipe_path={self.pipe_path}"
        )
        logger.info(f"GRAPH_EXECUTOR: Executing template at {template_path}")

        try:
            # Convert to absolute path - handle both relative and absolute paths
            path_obj = Path(template_path)
            if not path_obj.is_absolute():
                # If relative, it's relative to lackey_dir
                absolute_path = self.lackey_dir / template_path
            else:
                absolute_path = path_obj

            logger.debug(f"Template path resolved: {template_path} -> {absolute_path}")
            logger.info(f"GRAPH_EXECUTOR: Converted to absolute path: {absolute_path}")

            # Ensure the file exists
            if not absolute_path.exists():
                logger.error(f"Template file not found: {absolute_path}")
                raise FileNotFoundError(f"Template file not found: {absolute_path}")

            logger.debug("Template file exists, proceeding with execution")
            logger.info("GRAPH_EXECUTOR: File exists, proceeding with execution")

            # Create/use dedicated .venv for Strands execution
            logger.debug("Setting up Strands virtual environment")
            logger.info("GRAPH_EXECUTOR: Creating/checking Strands .venv")
            strands_venv_path = self._ensure_strands_venv()
            python_executable = strands_venv_path / "bin" / "python"
            absolute_python_path = str(python_executable.absolute())
            logger.debug(f"Python executable resolved: {absolute_python_path}")
            logger.info(
                f"GRAPH_EXECUTOR: Using Python executable: {absolute_python_path}"
            )

            # Execute the Python template with Strands .venv
            cmd = [absolute_python_path, str(absolute_path)]

            logger.debug(f"Executing command: {' '.join(cmd)}")
            logger.info(f"GRAPH_EXECUTOR: Running command: {' '.join(cmd)}")

            # Set working directory to project root (parent of .lackey)
            # so agent sees files from user's perspective
            project_root = self.lackey_dir.parent
            logger.debug(f"Setting working directory to project root: {project_root}")

            # Add pipe path as command line argument if available
            if self.pipe_path:
                cmd.extend(["--status-pipe", self.pipe_path])
                logger.debug(f"Added pipe argument: --status-pipe {self.pipe_path}")

            # Set up environment with lackey source path for pipe communication
            env = os.environ.copy()
            lackey_src_path = str(
                Path(__file__).parent.parent.parent.parent
            )  # Points to src directory
            logger.debug(f"Current file: {__file__}")
            logger.debug(f"Calculated lackey source path: {lackey_src_path}")
            logger.debug(
                f"Lackey source path exists: {os.path.exists(lackey_src_path)}"
            )

            if "PYTHONPATH" in env:
                old_pythonpath = env["PYTHONPATH"]
                env["PYTHONPATH"] = f"{lackey_src_path}:{env['PYTHONPATH']}"
                logger.debug(
                    f"Updated PYTHONPATH from '{old_pythonpath}' "
                    f"to '{env['PYTHONPATH']}'"
                )
            else:
                env["PYTHONPATH"] = lackey_src_path
                logger.debug(f"Set PYTHONPATH to: {env['PYTHONPATH']}")

            # Verify the lackey module can be found at this path
            lackey_module_path = os.path.join(lackey_src_path, "lackey")
            logger.debug(f"Lackey module path: {lackey_module_path}")
            logger.debug(f"Lackey module exists: {os.path.exists(lackey_module_path)}")

            # Run and capture output
            process = _secure_subprocess_run(
                cmd,
                capture_output=True,
                text=True,
                cwd=project_root,
                env=env,
            )

            logger.info(
                f"GRAPH_EXECUTOR: Process completed with return code: "
                f"{process.returncode}"
            )

            if process.stdout:
                logger.info(f"GRAPH_EXECUTOR: STDOUT: {process.stdout!r}")
            if process.stderr:
                logger.info(f"GRAPH_EXECUTOR: STDERR: {process.stderr!r}")

            # Parse LACKEY_RESULTS from output (strings due to text=True)
            stdout_str = str(process.stdout or "")
            stderr_str = str(process.stderr or "")
            return self._parse_lackey_results(stdout_str, stderr_str)

        except subprocess.TimeoutExpired as e:
            logger.error("GRAPH_EXECUTOR: Template execution timed out")
            # Try to parse any partial results (strings due to text=True)
            stdout_str = str(e.stdout or "")
            stderr_str = str(e.stderr or "")
            return self._parse_lackey_results(stdout_str, stderr_str)

        except Exception as e:
            logger.error(f"GRAPH_EXECUTOR: Template execution failed: {e}")
            return {"status": "failed", "error": str(e), "node_results": {}}

    def _ensure_strands_venv(self) -> Path:
        """Ensure Strands execution .venv exists with required packages."""
        venv_path = self.lackey_dir / "strands" / ".venv"

        if not venv_path.exists():
            logger.info(f"GRAPH_EXECUTOR: Creating Strands .venv at {venv_path}")

            # Create virtual environment
            _secure_subprocess_run(
                [sys.executable, "-m", "venv", str(venv_path)], check=True
            )

            # Install strands-agents package and precommit tools
            pip_executable = venv_path / "bin" / "pip"

            # Core strands packages
            core_packages = [
                "strands-agents",
                "strands-agents-tools",
                "boto3",
                "networkx",  # Required for lackey pipe communication
                "PyYAML",  # Required for lackey module
                "jinja2>=3.1.0,<4.0",  # Required for lackey template system
            ]

            # Precommit and code quality tools
            precommit_packages = [
                "black>=24.3.0,<25.0",
                "flake8>=6.0,<7.0",
                "flake8-docstrings",  # Additional flake8 plugin used in config
                "mypy>=1.0,<2.0",
                "isort>=5.0,<6.0",
                "bandit>=1.7,<2.0",
                "pre-commit>=3.0,<4.0",
                # Type stubs needed for mypy
                "types-PyYAML>=6.0,<7.0",
                "types-click>=7.1,<8.0",
                "cryptography>=44.0.1,<46.0.0",  # For type checking
            ]

            all_packages = core_packages + precommit_packages

            _secure_subprocess_run(
                [str(pip_executable), "install"] + all_packages,
                check=True,
            )

            logger.info("GRAPH_EXECUTOR: Strands .venv created with precommit tools")

        return venv_path

    def _register_message_handlers(self) -> None:
        """Register handlers for different message types."""
        if not self.pipe_reader:
            return

        # Register handlers for each message type
        self.pipe_reader.register_handler(
            MessageType.STATUS_UPDATE, self._process_status_update_message
        )
        self.pipe_reader.register_handler(
            MessageType.LOG_MESSAGE, self._process_log_message
        )
        self.pipe_reader.register_handler(
            MessageType.PROGRESS_UPDATE, self._process_progress_update_message
        )
        self.pipe_reader.register_handler(
            MessageType.ERROR_REPORT, self._process_error_report_message
        )
        self.pipe_reader.register_handler(
            MessageType.COST_UPDATE, self._process_cost_update_message
        )
        self.pipe_reader.register_handler(
            MessageType.TASK_COMPLETION, self._process_task_completion_message
        )
        self.pipe_reader.register_handler(
            MessageType.EXECUTION_METADATA, self._process_execution_metadata_message
        )

        logger.info("Registered all message handlers for pipe communication")

    def _process_status_update_message(self, message: PipeMessage) -> None:
        """Handle status update messages."""
        try:
            task_id = message.task_id
            data = message.data
            status = data.get("status")
            status_message = data.get("message", "")

            if not task_id or not status:
                logger.warning(f"Invalid status update format: {message.data}")
                return

            task_display = task_id[:8] if task_id else "UNKNOWN"

            if status_message:
                log_msg = (
                    f"Status update: task {task_display} -> {status} ({status_message})"
                )
            else:
                log_msg = f"Status update: task {task_display} -> {status}"

            # Log to executor log at INFO level
            if self.executor_logger:
                self.executor_logger.info(log_msg)

            logger.info(f"Real-time status update: task {task_id[:8]} -> {status}")

            # Update task status immediately
            self._update_task_status_with_core(task_id, status, status_message)

        except Exception as e:
            logger.error(f"Error handling status update: {e}")

    def _process_log_message(self, message: PipeMessage) -> None:
        """Handle log messages from subprocess and write to executor log."""
        try:
            data = message.data
            level = data.get("level", "INFO")
            log_message = data.get("message", "")
            task_id = message.task_id

            task_display = task_id[:8] if task_id else "SYSTEM"

            # Format message with task context
            formatted_message = f"[{task_display}] {log_message}"

            # Write to executor log at appropriate level
            if self.executor_logger:
                if level == "DEBUG":
                    self.executor_logger.debug(formatted_message)
                elif level == "INFO":
                    self.executor_logger.info(formatted_message)
                elif level == "WARNING":
                    self.executor_logger.warning(formatted_message)
                elif level == "ERROR":
                    self.executor_logger.error(formatted_message)
                else:
                    # Unknown level, default to info
                    self.executor_logger.info(f"[{level}] {formatted_message}")

            # Also log to main logger for immediate visibility
            logger.info(f"SUBPROCESS[{task_display}] {level}: {log_message}")

        except Exception as e:
            logger.error(f"Error handling log message: {e}")

    def _process_progress_update_message(self, message: PipeMessage) -> None:
        """Handle progress update messages."""
        try:
            task_id = message.task_id
            data = message.data
            progress = data.get("progress_percent", 0)
            step = data.get("current_step", "")

            task_display = task_id[:8] if task_id else "UNKNOWN"

            if step:
                log_msg = (
                    f"Progress update: task {task_display} -> {progress}% ({step})"
                )
            else:
                log_msg = f"Progress update: task {task_display} -> {progress}%"

            # Log to executor log at INFO level
            if self.executor_logger:
                self.executor_logger.info(log_msg)

            logger.info(log_msg)

        except Exception as e:
            logger.error(f"Error handling progress update: {e}")

    def _process_error_report_message(self, message: PipeMessage) -> None:
        """Handle error report messages."""
        try:
            task_id = message.task_id
            data = message.data
            error_type = data.get("error_type", "Unknown")
            error_message = data.get("error_message", "")
            traceback_info = data.get("traceback")

            task_display = task_id[:8] if task_id else "UNKNOWN"

            error_log = (
                f"Error report from task {task_display}: {error_type} - {error_message}"
            )

            # Log to executor log at ERROR level
            if self.executor_logger:
                self.executor_logger.error(error_log)
                if traceback_info:
                    self.executor_logger.error(
                        f"Traceback for task {task_display}:\n{traceback_info}"
                    )

            logger.error(error_log)
            if traceback_info:
                logger.debug(f"Traceback for task {task_display}:\n{traceback_info}")

        except Exception as e:
            logger.error(f"Error handling error report: {e}")

    def _process_cost_update_message(self, message: PipeMessage) -> None:
        """Handle cost update messages."""
        try:
            task_id = message.task_id
            data = message.data
            model_id = data.get("model_id", "unknown")
            input_tokens = data.get("input_tokens", 0)
            output_tokens = data.get("output_tokens", 0)
            cost = data.get("cost", 0.0)

            task_display = task_id[:8] if task_id else "UNKNOWN"

            cost_log = (
                f"Cost update for task {task_display}: ${cost:.4f} "
                f"({model_id}, {input_tokens}+{output_tokens} tokens)"
            )

            # Log to executor log at INFO level
            if self.executor_logger:
                self.executor_logger.info(cost_log)

            logger.info(cost_log)

            # Accumulate execution data for history tracking
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            self.total_cost += cost
            if not self.model_id:  # Use first model encountered
                self.model_id = model_id

        except Exception as e:
            logger.error(f"Error handling cost update: {e}")

    def _record_execution_history(
        self,
        execution_id: str,
        project_id: str,
        project_name: str,
        template_id: str,
        status: str,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
        input_token_cost: float,
        output_token_cost: float,
        total_cost: float,
        execution_time_ms: int,
        task_count: int,
        completed_tasks: int,
        timestamp: Optional[str] = None,
    ) -> None:
        """Record execution details to global execution history YAML file."""
        try:
            # Use lackey_dir to get to analytics directory
            history_file = self.lackey_dir / "analytics" / "execution_history.yaml"

            # Ensure analytics directory exists
            history_file.parent.mkdir(parents=True, exist_ok=True)

            # Create execution record
            execution_record = {
                "execution_id": execution_id,
                "project_id": project_id,
                "project_name": project_name,
                "template_id": template_id,
                "timestamp": timestamp or datetime.utcnow().isoformat() + "Z",
                "status": status,
                "model_id": model_id,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "input_token_cost": round(input_token_cost, 4),
                "output_token_cost": round(output_token_cost, 4),
                "total_cost": round(total_cost, 4),
                "execution_time_ms": execution_time_ms,
                "task_count": task_count,
                "completed_tasks": completed_tasks,
            }

            # Load existing history or create new structure
            if history_file.exists():
                with open(history_file, "r") as f:
                    history_data = yaml.safe_load(f) or {}
            else:
                history_data = {}

            # Ensure executions list exists
            if "executions" not in history_data:
                history_data["executions"] = []

            # Add new execution record
            history_data["executions"].append(execution_record)

            # Write back to file
            with open(history_file, "w") as f:
                yaml.safe_dump(
                    history_data, f, default_flow_style=False, sort_keys=False
                )

            logger.info(
                f"Recorded execution history for {execution_id[:8]} to {history_file}"
            )

        except Exception as e:
            logger.error(f"Failed to record execution history: {e}")

    def _process_task_completion_message(self, message: PipeMessage) -> None:
        """Handle task completion messages."""
        try:
            task_id = message.task_id
            data = message.data
            status = data.get("status", "unknown")
            result = data.get("result", "")
            execution_time = data.get("execution_time", 0)

            task_display = task_id[:8] if task_id else "UNKNOWN"

            completion_log = (
                f"Task completion: {task_display} -> {status} "
                f"(took {execution_time:.2f}ms)"
            )
            if result:
                completion_log += f"\nResult preview: {result[:200]}..."

            # Log to executor log at INFO level
            if self.executor_logger:
                self.executor_logger.info(completion_log)

            logger.info(
                f"Task completion: {task_display} -> {status} "
                f"(took {execution_time:.2f}ms)"
            )

            # Track completed tasks for history
            if status == "done":
                self.completed_tasks += 1

        except Exception as e:
            logger.error(f"Error handling task completion: {e}")

    def _process_execution_metadata_message(self, message: PipeMessage) -> None:
        """Handle execution metadata messages."""
        try:
            data = message.data

            metadata_log = f"Execution metadata: {data}"

            # Log to executor log at INFO level
            if self.executor_logger:
                self.executor_logger.info(metadata_log)

            logger.info(metadata_log)

        except Exception as e:
            logger.error(f"Error handling execution metadata: {e}")

    def _cleanup_pipe_communication(self) -> None:
        """Clean up pipe communication and executor logger."""
        # Record execution history before cleanup
        try:
            logger.info(
                "_cleanup_pipe_communication: Starting execution history " "recording"
            )

            if self.execution_id and self.execution_start_time:
                # Calculate execution time in milliseconds
                execution_time_ms = int(
                    (datetime.utcnow() - self.execution_start_time).total_seconds()
                    * 1000
                )
                logger.info(
                    f"_cleanup_pipe_communication: Calculated execution time: "
                    f"{execution_time_ms}ms"
                )

                # Get project information
                project_id = (
                    self.execution_id
                )  # Using execution_id as project_id for now
                project_name = "unknown"
                try:
                    # Try to get project info from storage
                    project_info = self.storage.get_project(project_id)
                    if project_info:
                        project_name = project_info.get(
                            "friendly_name", project_info.get("name", "unknown")
                        )
                    logger.info(
                        f"_cleanup_pipe_communication: Project info - "
                        f"ID: {project_id}, Name: {project_name}"
                    )
                except Exception as e:
                    logger.warning(
                        f"_cleanup_pipe_communication: Could not get project info: {e}"
                    )

                # Calculate token costs (rough estimate)
                input_token_cost = 0.0
                output_token_cost = 0.0
                if self.total_cost > 0 and (
                    self.total_input_tokens > 0 or self.total_output_tokens > 0
                ):
                    total_tokens = self.total_input_tokens + self.total_output_tokens
                    if total_tokens > 0:
                        # Rough cost breakdown estimate
                        input_token_cost = (
                            self.total_cost
                            * (self.total_input_tokens / total_tokens)
                            * 0.7
                        )
                        output_token_cost = (
                            self.total_cost
                            * (self.total_output_tokens / total_tokens)
                            * 1.3
                        )

                logger.info(
                    f"_cleanup_pipe_communication: Token data - Input: "
                    f"{self.total_input_tokens}, Output: {self.total_output_tokens}, "
                    f"Total cost: ${self.total_cost}"
                )
                logger.info(
                    f"_cleanup_pipe_communication: Task data - Count: "
                    f"{self.task_count}, Completed: {self.completed_tasks}"
                )

                # Determine execution status (default to completed if we got this far)
                execution_status = "completed"

                self._record_execution_history(
                    execution_id=self.execution_id,
                    project_id=project_id,
                    project_name=project_name,
                    # Using execution_id as template_id for now
                    template_id=self.execution_id,
                    status=execution_status,
                    model_id=self.model_id or "unknown",
                    input_tokens=self.total_input_tokens,
                    output_tokens=self.total_output_tokens,
                    input_token_cost=input_token_cost,
                    output_token_cost=output_token_cost,
                    total_cost=self.total_cost,
                    execution_time_ms=execution_time_ms,
                    task_count=self.task_count,
                    completed_tasks=self.completed_tasks,
                    timestamp=self.execution_start_time.isoformat() + "Z",
                )
                logger.info(
                    "_cleanup_pipe_communication: Execution history recording completed"
                )
            else:
                logger.warning(
                    "_cleanup_pipe_communication: Missing execution_id or "
                    "start_time, skipping history recording"
                )

        except Exception as e:
            logger.error(
                f"_cleanup_pipe_communication: Failed to record execution history: {e}"
            )
            import traceback

            logger.error(
                f"_cleanup_pipe_communication: Traceback: " f"{traceback.format_exc()}"
            )

        # Continue with normal cleanup
        if self.pipe_reader:
            self.pipe_reader.stop_monitoring()
            self.pipe_reader = None
        self.pipe_path = None

        # Clean up executor logger
        if self.executor_logger:
            self.executor_logger.info(
                f"Executor logging completed for execution {self.execution_id}"
            )
            # Close all handlers
            for handler in self.executor_logger.handlers[:]:
                handler.close()
                self.executor_logger.removeHandler(handler)
            self.executor_logger = None

        logger.info(
            "_cleanup_pipe_communication: Cleaned up pipe communication "
            "and executor logging"
        )

    def _parse_lackey_results(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse LACKEY_RESULTS from template output."""
        try:
            # Debug logging for type checking
            logger.debug(
                f"_parse_lackey_results called with stdout type: {type(stdout)}, "
                f"stderr type: {type(stderr)}"
            )
            logger.debug(
                f"stdout content preview: {repr(stdout[:200]) if stdout else 'None'}"
            )

            # Look for LACKEY_RESULTS in stdout - handle multi-line JSON
            lackey_start = stdout.find("LACKEY_RESULTS:")
            if lackey_start != -1:
                # Extract everything after LACKEY_RESULTS: marker
                results_json = stdout[lackey_start + len("LACKEY_RESULTS:") :].strip()

                # Find the end of the JSON by looking for the closing brace
                # This handles multi-line JSON with newlines in the content
                brace_count = 0
                json_end = 0
                for i, char in enumerate(results_json):
                    if char == "{":
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break

                if json_end > 0:
                    results_json = results_json[:json_end]
                    parsed_result = json.loads(results_json)
                    if isinstance(parsed_result, dict):
                        return parsed_result
                    else:
                        logger.warning(
                            f"LACKEY_RESULTS is not a dict: {type(parsed_result)}"
                        )
                        return {
                            "status": "error",
                            "error": "Invalid LACKEY_RESULTS format",
                        }

            # If no LACKEY_RESULTS found, return basic structure
            logger.warning("GRAPH_EXECUTOR: No LACKEY_RESULTS found in output")
            return {
                "status": "completed",
                "node_results": {},
                "stdout": stdout,
                "stderr": stderr,
            }

        except json.JSONDecodeError as e:
            logger.error(f"GRAPH_EXECUTOR: Failed to parse LACKEY_RESULTS: {e}")
            return {
                "status": "failed",
                "error": f"JSON parse error: {e}",
                "node_results": {},
                "stdout": stdout,
                "stderr": stderr,
            }

    def _load_dependency_order(self, template_path: str) -> List[str]:
        """Load dependency order from JSON spec file."""
        try:
            # Derive JSON spec path from template path
            # template_path: .../generated/project_id.py
            # spec_path: .../graphs/project_id.json
            template_dir = Path(template_path).parent
            project_dir = template_dir.parent
            graphs_dir = project_dir / "graphs"

            # Find the JSON spec file
            json_files = list(graphs_dir.glob("*.json"))
            if not json_files:
                logger.warning("No JSON spec file found, using arbitrary order")
                return []

            spec_path = json_files[0]  # Should be only one
            logger.debug(f"Loading dependency order from: {spec_path}")

            with open(spec_path, "r") as f:
                spec = json.load(f)

            # Extract nodes and their dependencies
            nodes = spec.get("nodes", [])
            dependencies: Dict[str, List[str]] = {}
            for node in nodes:
                task_id = node.get("task_id") or node.get("id")
                deps = node.get("dependencies", [])
                dependencies[task_id] = deps

            # Perform topological sort
            def topological_sort(deps: Dict[str, List[str]]) -> List[str]:
                in_degree = {task: 0 for task in deps}
                for task, task_deps in deps.items():
                    for dep in task_deps:
                        if dep in in_degree:
                            in_degree[task] += 1

                queue = [task for task, degree in in_degree.items() if degree == 0]
                result_order = []

                while queue:
                    task = queue.pop(0)
                    result_order.append(task)

                    for other_task, other_deps in deps.items():
                        if task in other_deps:
                            in_degree[other_task] -= 1
                            if in_degree[other_task] == 0:
                                queue.append(other_task)

                return result_order

            execution_order = topological_sort(dependencies)
            logger.info(f"GRAPH_EXECUTOR: Dependency order: {execution_order}")
            return execution_order

        except Exception as e:
            logger.error(f"Failed to load dependency order: {e}")
            return []

    def _process_graph_results(self, result: Dict[str, Any]) -> None:
        """Process graph results and update Lackey task statuses in order."""
        node_results = result.get("node_results", {})
        logger.debug(
            f"Processing graph results: {len(node_results)} node results to process"
        )
        logger.info(f"GRAPH_EXECUTOR: Processing results for {len(node_results)} nodes")

        # Get dependency-ordered execution sequence
        template_path = getattr(self, "_current_template_path", "")
        execution_order = self._load_dependency_order(template_path)

        # If we have dependency order, process in that order; otherwise arbitrary
        if execution_order:
            task_ids = [
                task_id for task_id in execution_order if task_id in node_results
            ]
            logger.info(
                f"GRAPH_EXECUTOR: Processing {len(task_ids)} tasks in "
                f"dependency order"
            )
        else:
            task_ids = list(node_results.keys())
            logger.warning(
                "GRAPH_EXECUTOR: Processing tasks in arbitrary order "
                "(no dependency info)"
            )

        for task_id in task_ids:
            node_result = node_results[task_id]
            logger.debug(
                f"Processing result for task {task_id}: "
                f"status={node_result.get('status')}"
            )
            try:
                # Get the task and check current status
                task = self.storage.get_task(task_id)
                if not task:
                    logger.warning(f"Task not found in storage: {task_id}")
                    logger.warning(
                        f"GRAPH_EXECUTOR: Task {task_id} not found in storage"
                    )
                    continue

                logger.debug(f"Task found: {task.title}, current status: {task.status}")

                # Skip if task is already DONE - don't change completed tasks
                if task.status.value == "done":
                    logger.info(
                        f"GRAPH_EXECUTOR: Skipping task {task_id} - already DONE"
                    )
                    # Still add agent response as note for completed tasks
                    agent_response = node_result.get("result", "") or node_result.get(
                        "output", ""
                    )
                    if agent_response:
                        execution_time = node_result.get("execution_time", 0)
                        self._add_agent_response_note(
                            task_id, agent_response, execution_time
                        )
                        logger.info(
                            f"GRAPH_EXECUTOR: Added agent response note to "
                            f"already-done task {task_id}"
                        )
                    continue

                # Determine new status based on node result
                node_status = node_result.get("status", "failed")
                if node_status == "done":
                    new_status = "done"
                elif node_status == "completed":
                    new_status = "done"
                else:
                    new_status = "todo"  # Reset to todo for retry

                logger.debug(
                    f"Status transition for task {task_id}: "
                    f"{task.status} -> {new_status}"
                )

                # Capture agent response if available
                agent_response = node_result.get("result", "") or node_result.get(
                    "output", ""
                )
                logger.debug(
                    f"Agent response captured: {len(agent_response)} characters"
                )
                logger.info(
                    f"GRAPH_EXECUTOR: Extracted response length: "
                    f"{len(agent_response)} characters"
                )
                logger.info(
                    f"GRAPH_EXECUTOR: Response preview: {agent_response[:200]}..."
                )

                # Actually update the task status using core to trigger cascades
                from lackey.core import LackeyCore
                from lackey.models import TaskStatus

                core = LackeyCore(str(self.lackey_dir))

                # Update task status - this will trigger dependency cascades
                core.update_task_status(
                    task_id=task_id,
                    new_status=getattr(TaskStatus, new_status.upper()),
                    note="Task completed via Strands execution",
                )

                logger.info(
                    f"GRAPH_EXECUTOR: Updated task {task_id} to {new_status} "
                    f"using core.update_task_status"
                )

                # Add agent response as note
                if agent_response:
                    execution_time = node_result.get("execution_time", 0)
                    self._add_agent_response_note(
                        task_id, agent_response, execution_time
                    )

            except Exception as e:
                logger.error(f"GRAPH_EXECUTOR: Failed to update task {task_id}: {e}")

    def _add_agent_response_note(
        self, task_id: str, response: str, execution_time: int = 0
    ) -> None:
        """Add agent response as a task note."""
        try:
            from lackey.core import LackeyCore
            from lackey.models import NoteType

            # Create core instance
            core = LackeyCore(str(self.lackey_dir))

            # Find project ID for this task
            project_id = self.storage.find_project_id_by_task_id(task_id)
            if not project_id:
                logger.error(
                    f"GRAPH_EXECUTOR: Could not find project for task {task_id}"
                )
                return

            # Debug: Log response length and first/last parts
            logger.info(
                f"GRAPH_EXECUTOR: Agent response length: {len(response)} characters"
            )
            logger.info(f"GRAPH_EXECUTOR: Response start: {response[:100]}...")
            logger.info(f"GRAPH_EXECUTOR: Response end: ...{response[-100:]}")

            # Format the note with execution metadata
            note_content = (
                f"Agent Response (execution time: {execution_time}ms):\n\n{response}"
            )

            # Debug: Log note content length
            logger.info(
                f"GRAPH_EXECUTOR: Note content length: "
                f"{len(note_content)} characters"
            )

            # Add the note using core's method
            core.add_task_note(task_id, note_content, note_type=NoteType.SYSTEM)

            logger.info(f"GRAPH_EXECUTOR: Added agent response note to task {task_id}")

        except Exception as e:
            logger.error(
                f"GRAPH_EXECUTOR: Failed to add agent response note to "
                f"task {task_id}: {e}"
            )

    def _update_task_status_with_core(
        self, task_id: str, new_status: str, note: Optional[str] = None
    ) -> None:
        """Update task status using core's method to trigger dependency resolution."""
        try:
            from lackey.core import LackeyCore
            from lackey.models import TaskStatus

            # Create core instance
            core = LackeyCore(str(self.lackey_dir))

            # Find project ID for this task
            project_id = self.storage.find_project_id_by_task_id(task_id)
            if not project_id:
                logger.error(
                    f"GRAPH_EXECUTOR: Could not find project for task {task_id}"
                )
                return

            # Convert string status to TaskStatus enum
            status_map = {
                "todo": TaskStatus.TODO,
                "in_progress": TaskStatus.IN_PROGRESS,
                "done": TaskStatus.DONE,
                "blocked": TaskStatus.BLOCKED,
            }

            task_status = status_map.get(new_status, TaskStatus.TODO)

            # Use core's method to trigger dependency resolution
            core.update_task_status(task_id, task_status, note)
            logger.info(
                f"GRAPH_EXECUTOR: Used core.update_task_status for task {task_id}"
            )

        except Exception as e:
            logger.error(f"GRAPH_EXECUTOR: Failed to use core update_task_status: {e}")
            # Fallback to direct update
            try:
                task = self.storage.get_task(task_id)
                if task:
                    from lackey.models import TaskStatus

                    status_map = {
                        "todo": TaskStatus.TODO,
                        "in_progress": TaskStatus.IN_PROGRESS,
                        "done": TaskStatus.DONE,
                        "blocked": TaskStatus.BLOCKED,
                    }
                    task_status = status_map.get(new_status, TaskStatus.TODO)
                    task.update_status(task_status, note)
                    self.storage.update_task(task)
            except Exception as fallback_error:
                logger.error(
                    f"GRAPH_EXECUTOR: Fallback update also failed: " f"{fallback_error}"
                )

    def execute_task_with_rules(self, task_info: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task using enhanced agent with rules injection."""
        try:
            from lackey.strands.execute.rules_injection import (
                create_rules_enhanced_agent,
            )

            # Create enhanced agent
            agent = create_rules_enhanced_agent(task_info, self.lackey_dir)

            # Create execution prompt with think tool guidance
            execution_prompt = f"""
Use the think tool to analyze this complex task and break it into manageable phases:

TASK: {task_info.get('title', 'Unknown Task')}
OBJECTIVE: {task_info.get('objective', 'Complete the task')}

APPROACH:
1. Use think tool with 3-4 cycles to analyze requirements
2. Break down into implementation phases
3. Implement the first phase completely
4. Document progress and next steps

CONTEXT: {task_info.get('context', 'No additional context')}

Begin by using the think tool to analyze and plan the implementation.
"""

            logger.info(f"Executing task: {task_info.get('title', 'Unknown')}")

            # Execute with enhanced agent
            result = agent(execution_prompt)

            # Extract response
            response_text = str(result)

            return {
                "status": "success",
                "task_id": task_info.get("id", "unknown"),
                "response": response_text,
                "metrics": {
                    "total_tokens": (
                        getattr(result.metrics, "total_tokens", 0)
                        if hasattr(result, "metrics")
                        else 0
                    ),
                    "cycles": (
                        getattr(result.metrics, "total_cycles", 0)
                        if hasattr(result, "metrics")
                        else 0
                    ),
                },
            }

        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            return {
                "status": "error",
                "task_id": task_info.get("id", "unknown"),
                "error": str(e),
                "error_type": type(e).__name__,
            }

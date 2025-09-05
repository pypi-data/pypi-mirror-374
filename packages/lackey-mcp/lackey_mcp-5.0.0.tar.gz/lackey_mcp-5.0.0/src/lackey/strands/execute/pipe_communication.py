"""
Named pipe communication system for strands execution.

This module implements robust named pipe communication between the main Lackey process
and strands execution subprocesses, with proper message categorization and error
handling.
"""

import json
import logging
import os
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages that can be sent through the pipe."""

    STATUS_UPDATE = "status_update"
    LOG_MESSAGE = "log_message"
    PROGRESS_UPDATE = "progress_update"
    ERROR_REPORT = "error_report"
    COST_UPDATE = "cost_update"
    TASK_COMPLETION = "task_completion"
    EXECUTION_METADATA = "execution_metadata"


@dataclass
class PipeMessage:
    """Structured message for pipe communication."""

    message_type: MessageType
    task_id: Optional[str]
    execution_id: str
    timestamp: float
    data: Dict[str, Any]
    python_executable: Optional[str] = None

    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps(
            {
                "message_type": self.message_type.value,
                "task_id": self.task_id,
                "execution_id": self.execution_id,
                "timestamp": self.timestamp,
                "data": self.data,
                "python_executable": self.python_executable,
            }
        )

    @classmethod
    def from_json(cls, json_str: str) -> "PipeMessage":
        """Create message from JSON string."""
        try:
            data = json.loads(json_str)
            return cls(
                message_type=MessageType(data["message_type"]),
                task_id=data.get("task_id"),
                execution_id=data["execution_id"],
                timestamp=data["timestamp"],
                data=data["data"],
                python_executable=data.get("python_executable"),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse pipe message JSON: {e}")
            logger.debug(f"Invalid JSON content: {json_str[:200]}...")
            raise


class PipeReader:
    """
    Named pipe reader for the main Lackey process.

    Implements the ONE READER pattern from our lessons learned.
    """

    def __init__(self, execution_id: str):
        """
        Initialize the PipeReader for a specific execution.

        Args:
            execution_id: Unique identifier for the execution
        """
        self.execution_id = execution_id
        self.pipe_path: Optional[str] = None
        self.reader_thread: Optional[threading.Thread] = None
        self.stop_reading = False
        self.message_handlers: Dict[
            MessageType, List[Callable[[PipeMessage], None]]
        ] = {}
        self.messages_received = 0
        self.is_active = False

        logger.debug(f"Initialized PipeReader for execution {execution_id}")

    def create_pipe(self) -> str:
        """Create a named pipe for this execution."""
        pipe_name = f"lackey_execution_{self.execution_id}"
        self.pipe_path = os.path.join(tempfile.gettempdir(), pipe_name)

        # Remove existing pipe if it exists
        if os.path.exists(self.pipe_path):
            logger.debug(f"Removing existing pipe: {self.pipe_path}")
            try:
                os.unlink(self.pipe_path)
            except OSError as e:
                logger.warning(f"Failed to remove existing pipe {self.pipe_path}: {e}")

        # Create named pipe
        try:
            os.mkfifo(self.pipe_path)
            logger.info(f"Created execution pipe: {self.pipe_path}")
            return self.pipe_path
        except OSError as e:
            logger.error(f"Failed to create named pipe {self.pipe_path}: {e}")
            raise

    def register_handler(
        self, message_type: MessageType, handler: Callable[[PipeMessage], None]
    ) -> None:
        """Register a handler for a specific message type."""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
        logger.debug(
            f"Registered handler for {message_type.value} "
            f"(total handlers: {len(self.message_handlers[message_type])})"
        )

    def start_monitoring(self) -> None:
        """Start monitoring the pipe in a background thread."""
        if not self.pipe_path:
            logger.error(
                "Cannot start monitoring: pipe not created. Call create_pipe() first."
            )
            raise ValueError("Pipe not created. Call create_pipe() first.")

        if self.is_active:
            logger.warning(
                f"Pipe monitoring already active for execution {self.execution_id}"
            )
            return

        self.stop_reading = False
        self.is_active = True
        self.reader_thread = threading.Thread(
            target=self._monitor_pipe,
            daemon=True,
            name=f"PipeReader-{self.execution_id}",
        )
        self.reader_thread.start()
        logger.info(f"Started pipe monitoring thread for execution {self.execution_id}")

    def _monitor_pipe(self) -> None:
        """Monitor the pipe for incoming messages."""
        if not self.pipe_path:
            logger.error("Cannot monitor pipe: pipe_path is None")
            return

        logger.debug(f"Pipe monitor thread starting for {self.pipe_path}")

        try:
            with open(self.pipe_path, "r") as pipe:
                logger.debug(f"Pipe opened for reading: {self.pipe_path}")

                while not self.stop_reading:
                    try:
                        line = pipe.readline()
                        if not line:
                            # No data available, short sleep to prevent busy waiting
                            time.sleep(0.01)
                            continue

                        line = line.strip()
                        if not line:
                            continue

                        # Parse and handle message
                        try:
                            message = PipeMessage.from_json(line)
                            self._handle_message(message)
                            self.messages_received += 1
                            logger.debug(
                                f"Successfully processed message "
                                f"#{self.messages_received}"
                            )

                        except json.JSONDecodeError as e:
                            logger.warning(
                                f"Invalid JSON in pipe message: {line[:100]}..., "
                                f"error: {e}"
                            )
                        except Exception as e:
                            logger.error(f"Error processing pipe message: {e}")
                            logger.debug(
                                f"Problematic message content: {line[:200]}..."
                            )

                    except Exception as e:
                        if not self.stop_reading:
                            logger.error(f"Error reading from pipe: {e}")
                        break

        except FileNotFoundError:
            logger.error(f"Pipe file not found: {self.pipe_path}")
        except PermissionError:
            logger.error(f"Permission denied accessing pipe: {self.pipe_path}")
        except Exception as e:
            logger.error(f"Failed to open pipe {self.pipe_path}: {e}")
        finally:
            self.is_active = False
            logger.debug(
                f"Pipe monitor thread ending for execution {self.execution_id}"
            )

    def _handle_message(self, message: PipeMessage) -> None:
        """Handle an incoming message by calling registered handlers."""
        task_display = message.task_id[:8] if message.task_id else "N/A"
        logger.debug(
            f"Processing {message.message_type.value} message for task {task_display}"
        )

        # Call handlers for this message type
        handlers = self.message_handlers.get(message.message_type, [])
        if not handlers:
            logger.debug(f"No handlers registered for {message.message_type.value}")
            return

        for i, handler in enumerate(handlers):
            try:
                logger.debug(
                    f"Calling handler {i+1}/{len(handlers)} "
                    f"for {message.message_type.value}"
                )
                handler(message)
            except Exception as e:
                logger.error(
                    f"Error in message handler {i+1} "
                    f"for {message.message_type.value}: {e}"
                )
                logger.debug("Handler error details", exc_info=True)

    def stop_monitoring(self) -> None:
        """Stop monitoring the pipe and clean up."""
        logger.info(f"Stopping pipe monitoring for execution {self.execution_id}")
        self.stop_reading = True

        # Wait for thread to finish
        if self.reader_thread and self.reader_thread.is_alive():
            logger.debug("Waiting for pipe monitor thread to finish...")
            self.reader_thread.join(timeout=2)
            if self.reader_thread.is_alive():
                logger.warning("Pipe monitor thread did not finish within timeout")

        # Clean up pipe file
        if self.pipe_path and os.path.exists(self.pipe_path):
            try:
                os.unlink(self.pipe_path)
                logger.debug(f"Cleaned up pipe file: {self.pipe_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up pipe file: {e}")

        self.pipe_path = None
        self.reader_thread = None
        self.is_active = False

        logger.info(
            f"Pipe monitoring stopped for execution {self.execution_id}, "
            f"processed {self.messages_received} messages"
        )


class PipeWriter:
    """
    Named pipe writer for strands execution subprocesses.

    Implements the ONE WRITER pattern from our lessons learned.
    """

    def __init__(self, pipe_path: str, execution_id: str):
        """
        Initialize the PipeWriter for a specific execution.

        Args:
            pipe_path: Path to the named pipe
            execution_id: Unique identifier for the execution
        """
        self.pipe_path = pipe_path
        self.execution_id = execution_id
        self.python_executable = os.path.abspath(sys.executable)
        self.messages_sent = 0

        logger.debug(
            f"Initialized PipeWriter for execution {execution_id}, "
            f"pipe: {pipe_path}"
        )

        # Verify pipe exists
        if not os.path.exists(pipe_path):
            logger.error(f"Pipe file does not exist: {pipe_path}")
            raise FileNotFoundError(f"Pipe file does not exist: {pipe_path}")

    def send_message(
        self,
        message_type: MessageType,
        task_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send a message through the pipe."""
        if data is None:
            data = {}

        message = PipeMessage(
            message_type=message_type,
            task_id=task_id,
            execution_id=self.execution_id,
            timestamp=time.time(),
            data=data,
            python_executable=self.python_executable,
        )

        task_display = task_id[:8] if task_id else "N/A"
        logger.debug(f"Sending {message_type.value} message for task {task_display}")

        try:
            with open(self.pipe_path, "w") as pipe:
                json_message = message.to_json()
                pipe.write(json_message + "\n")
                pipe.flush()

            self.messages_sent += 1
            logger.debug(
                f"Successfully sent {message_type.value} message #{self.messages_sent}"
            )

        except FileNotFoundError:
            logger.error(f"Pipe file not found when sending message: {self.pipe_path}")
            raise
        except PermissionError:
            logger.error(f"Permission denied writing to pipe: {self.pipe_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to send {message_type.value} message: {e}")
            logger.debug("Message send error details", exc_info=True)
            raise

    def send_task_status_update(
        self, task_id: str, status: str, message: str = ""
    ) -> None:
        """Send a task status update."""
        logger.debug(f"Sending status update: task {task_id[:8]} -> {status}")
        self.send_message(
            MessageType.STATUS_UPDATE,
            task_id=task_id,
            data={"status": status, "message": message},
        )

    def send_log_to_pipe(
        self, level: str, message: str, task_id: Optional[str] = None
    ) -> None:
        """Send a log message."""
        task_display = task_id[:8] if task_id else "N/A"
        logger.debug(
            f"Sending log message ({level}) for task {task_display}: "
            f"{message[:50]}..."
        )
        self.send_message(
            MessageType.LOG_MESSAGE,
            task_id=task_id,
            data={"level": level, "message": message},
        )

    def send_task_progress_update(
        self, task_id: str, progress_percent: float, current_step: str = ""
    ) -> None:
        """Send a progress update."""
        logger.debug(
            f"Sending progress update: task {task_id[:8]} -> {progress_percent}%"
        )
        self.send_message(
            MessageType.PROGRESS_UPDATE,
            task_id=task_id,
            data={"progress_percent": progress_percent, "current_step": current_step},
        )

    def send_error_to_pipe(
        self,
        task_id: str,
        error_type: str,
        error_message: str,
        traceback_info: Optional[str] = None,
    ) -> None:
        """Send an error report."""
        logger.info(f"Sending error report for task {task_id[:8]}: {error_type}")
        self.send_message(
            MessageType.ERROR_REPORT,
            task_id=task_id,
            data={
                "error_type": error_type,
                "error_message": error_message,
                "traceback": traceback_info,
            },
        )

    def send_cost_to_pipe(
        self,
        task_id: str,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
    ) -> None:
        """Send a cost update."""
        logger.info(
            f"Sending cost update for task {task_id[:8]}: "
            f"${cost:.4f} ({input_tokens}+{output_tokens} tokens)"
        )
        self.send_message(
            MessageType.COST_UPDATE,
            task_id=task_id,
            data={
                "model_id": model_id,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
            },
        )

    def send_completion_to_pipe(
        self, task_id: str, status: str, result: str, execution_time: float
    ) -> None:
        """Send task completion notification."""
        logger.info(
            f"Sending task completion: task {task_id[:8]} -> {status} "
            f"(took {execution_time:.2f}ms)"
        )
        self.send_message(
            MessageType.TASK_COMPLETION,
            task_id=task_id,
            data={"status": status, "result": result, "execution_time": execution_time},
        )

    def send_execution_metadata_update(self, metadata: Dict[str, Any]) -> None:
        """Send execution metadata."""
        logger.debug(f"Sending execution metadata: {list(metadata.keys())}")
        self.send_message(MessageType.EXECUTION_METADATA, data=metadata)


def create_pipe_communication(execution_id: str) -> Tuple[PipeReader, str]:
    """
    Create pipe communication setup for an execution.

    Returns:
        tuple: (PipeReader instance, pipe_path for subprocess)
    """
    logger.info(f"Creating pipe communication for execution {execution_id}")
    reader = PipeReader(execution_id)
    pipe_path = reader.create_pipe()
    logger.debug(f"Pipe communication created: reader={reader}, path={pipe_path}")
    return reader, pipe_path


def get_pipe_writer_from_args() -> Optional[PipeWriter]:
    """
    Get pipe writer from command line arguments.

    This function should be called by subprocess scripts to get the pipe writer.
    """
    logger.debug(f"Looking for pipe writer in command line args: {sys.argv}")

    # Look for --status-pipe argument
    if "--status-pipe" in sys.argv:
        try:
            pipe_index = sys.argv.index("--status-pipe")
            if pipe_index + 1 < len(sys.argv):
                pipe_path = sys.argv[pipe_index + 1]
                logger.debug(f"Found pipe path in args: {pipe_path}")

                # Extract execution_id from pipe path
                pipe_name = os.path.basename(pipe_path)
                if pipe_name.startswith("lackey_execution_"):
                    execution_id = pipe_name[len("lackey_execution_") :]
                    logger.info(f"Creating pipe writer for execution {execution_id}")
                    return PipeWriter(pipe_path, execution_id)
                else:
                    logger.warning(
                        f"Pipe name does not match expected format: {pipe_name}"
                    )

        except (ValueError, IndexError) as e:
            logger.error(f"Error parsing --status-pipe argument: {e}")
    else:
        logger.debug("No --status-pipe argument found in command line")

    return None

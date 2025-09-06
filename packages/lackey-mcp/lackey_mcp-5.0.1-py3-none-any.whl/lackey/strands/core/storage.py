"""Storage extension for strand executor system."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...file_ops import atomic_write, ensure_directory, read_text_file, safe_delete_file
from ...storage import LackeyStorage, StorageError
from ..core.models import ExecutionGraphSpec, ExecutionRecord, ExecutorConfiguration

logger = logging.getLogger(__name__)


class StrandStorageError(StorageError):
    """Raised when strand storage operations fail."""

    pass


class StrandGraphNotFoundError(StrandStorageError):
    """Raised when a strand graph cannot be found."""

    pass


class StrandExecutionNotFoundError(StrandStorageError):
    """Raised when a strand execution cannot be found."""

    pass


class ExecutionStorageService:
    """Storage extension for strand executor system."""

    def __init__(self, lackey_storage: LackeyStorage, project_id: Optional[str] = None):
        """Initialize strand storage with base Lackey storage."""
        self.lackey_storage = lackey_storage
        self.base_path = Path(lackey_storage.lackey_dir)

        if project_id:
            # Store strands files under project directory
            self.strands_dir = self.base_path / "projects" / project_id / "strands"
        else:
            # Global strands directory (for backward compatibility)
            self.strands_dir = self.base_path / "strands"

        self.graphs_dir = self.strands_dir / "graphs"
        self.executions_dir = self.strands_dir / "executions"
        self.generated_dir = self.strands_dir / "generated"
        self.config_file = self.strands_dir / "config.json"

        # Ensure directories exist
        ensure_directory(str(self.strands_dir))
        ensure_directory(str(self.graphs_dir))
        ensure_directory(str(self.executions_dir))
        ensure_directory(str(self.generated_dir))

    def save_execution_graph(self, graph: ExecutionGraphSpec) -> None:
        """Save a strand graph specification."""
        try:
            graph_file = self.graphs_dir / f"{graph.id}.json"
            graph_data = graph.to_dict()

            with atomic_write(str(graph_file)) as op:
                op.write_content(json.dumps(graph_data, indent=2))
            logger.info(f"Saved strand graph {graph.id} to {graph_file}")

        except Exception as e:
            raise StrandStorageError(f"Failed to save strand graph {graph.id}: {e}")

    def get_execution_graph(self, graph_id: str) -> ExecutionGraphSpec:
        """Load a strand graph specification."""
        try:
            graph_file = self.graphs_dir / f"{graph_id}.json"

            if not graph_file.exists():
                raise StrandGraphNotFoundError(f"Strand graph {graph_id} not found")

            content = read_text_file(str(graph_file))
            graph_data = json.loads(content)

            return ExecutionGraphSpec.from_dict(graph_data)

        except StrandGraphNotFoundError:
            # Re-raise specific exceptions
            raise
        except json.JSONDecodeError as e:
            raise StrandStorageError(f"Invalid JSON in strand graph {graph_id}: {e}")
        except Exception as e:
            raise StrandStorageError(f"Failed to load strand graph {graph_id}: {e}")

    def list_execution_graphs(self) -> List[Dict[str, str]]:
        """List all strand graph specifications."""
        graphs = []

        try:
            for graph_file in self.graphs_dir.glob("*.json"):
                try:
                    content = read_text_file(str(graph_file))
                    graph_data = json.loads(content)

                    graphs.append(
                        {
                            "id": graph_data["id"],
                            "name": graph_data["name"],
                            "description": graph_data["description"],
                            "created": graph_data["created"],
                            "node_count": len(graph_data["nodes"]),
                        }
                    )

                except Exception as e:
                    logger.warning(f"Failed to read strand graph {graph_file}: {e}")
                    continue

            return sorted(graphs, key=lambda x: x["created"], reverse=True)

        except Exception as e:
            raise StrandStorageError(f"Failed to list strand graphs: {e}")

    def delete_execution_graph(self, graph_id: str) -> None:
        """Delete a strand graph specification."""
        try:
            graph_file = self.graphs_dir / f"{graph_id}.json"

            if not graph_file.exists():
                raise StrandGraphNotFoundError(f"Strand graph {graph_id} not found")

            safe_delete_file(str(graph_file))
            logger.info(f"Deleted strand graph {graph_id}")

        except StrandGraphNotFoundError:
            # Re-raise specific exceptions
            raise
        except Exception as e:
            raise StrandStorageError(f"Failed to delete strand graph {graph_id}: {e}")

    def save_execution_record(self, execution: ExecutionRecord) -> None:
        """Save a strand execution state."""
        try:
            execution_file = self.executions_dir / f"{execution.id}.json"
            execution_data: Dict[str, Any] = {
                "id": execution.id,
                "graph_id": execution.graph_spec_id,
                "status": execution.status.value,
                "started": execution.started_at.isoformat(),
                "completed": (
                    execution.completed_at.isoformat()
                    if execution.completed_at
                    else None
                ),
                "current_nodes": [],
                "completed_nodes": [],
                "failed_nodes": [],
                "execution_log": [],
                "metadata": execution.results,
            }

            with atomic_write(str(execution_file)) as op:
                op.write_content(json.dumps(execution_data, indent=2))
            logger.info(f"Saved strand execution {execution.id} to {execution_file}")

        except Exception as e:
            raise StrandStorageError(
                f"Failed to save strand execution {execution.id}: {e}"
            )

    def get_execution_record(self, execution_id: str) -> ExecutionRecord:
        """Load a strand execution state."""
        try:
            execution_file = self.executions_dir / f"{execution_id}.json"

            if not execution_file.exists():
                raise StrandExecutionNotFoundError(
                    f"Strand execution {execution_id} not found"
                )

            content = read_text_file(str(execution_file))
            execution_data = json.loads(content)

            from datetime import datetime

            from ..core.models import ExecutionStatus

            execution = ExecutionRecord(
                id=execution_data["id"],
                graph_spec_id=execution_data["graph_id"],
                status=ExecutionStatus(execution_data["status"]),
                started_at=datetime.fromisoformat(execution_data["started"]),
                completed_at=(
                    datetime.fromisoformat(execution_data["completed"])
                    if execution_data["completed"]
                    else None
                ),
                results=execution_data["metadata"],
            )

            return execution

        except StrandExecutionNotFoundError:
            # Re-raise specific exceptions
            raise
        except json.JSONDecodeError as e:
            raise StrandStorageError(
                f"Invalid JSON in strand execution {execution_id}: {e}"
            )
        except Exception as e:
            raise StrandStorageError(
                f"Failed to load strand execution {execution_id}: {e}"
            )

    def list_execution_records(
        self, graph_id: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """List strand executions, optionally filtered by graph ID."""
        executions = []

        try:
            for execution_file in self.executions_dir.glob("*.json"):
                try:
                    content = read_text_file(str(execution_file))
                    execution_data = json.loads(content)

                    # Filter by graph ID if specified
                    if graph_id and execution_data["graph_id"] != graph_id:
                        continue

                    executions.append(
                        {
                            "id": execution_data["id"],
                            "graph_id": execution_data["graph_id"],
                            "status": execution_data["status"],
                            "started": execution_data["started"],
                            "completed": execution_data.get("completed"),
                            "current_node_count": len(execution_data["current_nodes"]),
                            "completed_node_count": len(
                                execution_data["completed_nodes"]
                            ),
                            "failed_node_count": len(execution_data["failed_nodes"]),
                        }
                    )

                except Exception as e:
                    logger.warning(
                        f"Failed to read strand execution {execution_file}: {e}"
                    )
                    continue

            return sorted(executions, key=lambda x: x["started"], reverse=True)

        except Exception as e:
            raise StrandStorageError(f"Failed to list strand executions: {e}")

    def delete_execution_record(self, execution_id: str) -> None:
        """Delete a strand execution."""
        try:
            execution_file = self.executions_dir / f"{execution_id}.json"

            if not execution_file.exists():
                raise StrandExecutionNotFoundError(
                    f"Strand execution {execution_id} not found"
                )

            safe_delete_file(str(execution_file))
            logger.info(f"Deleted strand execution {execution_id}")

        except Exception as e:
            raise StrandStorageError(
                f"Failed to delete strand execution {execution_id}: {e}"
            )

    def save_executor_config(self, config: ExecutorConfiguration) -> None:
        """Save strand executor configuration."""
        try:
            from dataclasses import asdict

            config_data = asdict(config)
            with atomic_write(str(self.config_file)) as op:
                op.write_content(json.dumps(config_data, indent=2))
            logger.info(f"Saved strand executor config to {self.config_file}")

        except Exception as e:
            raise StrandStorageError(f"Failed to save strand executor config: {e}")

    def get_executor_config(self) -> ExecutorConfiguration:
        """Load strand executor configuration."""
        try:
            if not self.config_file.exists():
                # Return default config if none exists
                config = ExecutorConfiguration()
                self.save_executor_config(config)
                return config

            content = read_text_file(str(self.config_file))
            config_data = json.loads(content)

            return ExecutorConfiguration.from_dict(config_data)

        except json.JSONDecodeError as e:
            raise StrandStorageError(f"Invalid JSON in strand executor config: {e}")
        except Exception as e:
            raise StrandStorageError(f"Failed to load strand executor config: {e}")

    def cleanup_completed_executions(self, days_old: int = 30) -> int:
        """Clean up completed executions older than specified days."""
        from datetime import UTC, datetime, timedelta

        cutoff_date = datetime.now(UTC) - timedelta(days=days_old)
        cleaned_count = 0

        try:
            for execution_file in self.executions_dir.glob("*.json"):
                try:
                    content = read_text_file(str(execution_file))
                    execution_data = json.loads(content)

                    # Only clean up completed executions
                    if execution_data["status"] not in [
                        "completed",
                        "failed",
                        "cancelled",
                    ]:
                        continue

                    # Check if old enough
                    completed_str = execution_data.get("completed")
                    if not completed_str:
                        continue

                    completed_date = datetime.fromisoformat(completed_str)
                    if completed_date < cutoff_date:
                        safe_delete_file(str(execution_file))
                        cleaned_count += 1
                        logger.info(f"Cleaned up old execution {execution_data['id']}")

                except Exception as e:
                    logger.warning(
                        f"Failed to process execution file {execution_file}: {e}"
                    )
                    continue

            return cleaned_count

        except Exception as e:
            raise StrandStorageError(f"Failed to cleanup executions: {e}")

    def get_execution_stats(self) -> Dict[str, int]:
        """Get statistics about strand executions."""
        stats = {
            "total": 0,
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
        }

        try:
            for execution_file in self.executions_dir.glob("*.json"):
                try:
                    content = read_text_file(str(execution_file))
                    execution_data = json.loads(content)

                    status = execution_data["status"]
                    stats["total"] += 1
                    stats[status] = stats.get(status, 0) + 1

                except Exception as e:
                    logger.warning(
                        f"Failed to read execution stats from {execution_file}: {e}"
                    )
                    continue

            return stats

        except Exception as e:
            raise StrandStorageError(f"Failed to get execution stats: {e}")

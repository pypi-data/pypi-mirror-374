"""Core data models for strand executor system."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class NodeType(Enum):
    """Types of strand nodes."""

    AGENT = "agent"
    TOOL = "tool"
    CONDITION = "condition"


class ExecutionStatus(Enum):
    """Status of strand execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskComplexity(Enum):
    """Task complexity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ExecutionNode:
    """A node in the strand execution graph."""

    id: str
    name: str
    node_type: NodeType
    complexity: str = "medium"
    prompt: Optional[str] = None
    dependencies: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "task_id": self.id,
            "strand_type": (
                self.node_type.value
                if hasattr(self.node_type, "value")
                else str(self.node_type)
            ),
            "dependencies": list(self.dependencies),
            "conditions": None,
            "metadata": {
                "task_title": self.name,
                "task_complexity": self.complexity,
                "task_status": "todo",
                "depth_level": 0,
                "can_parallelize": False,
                "assigned_to": None,
                **self.metadata,
            },
        }


@dataclass
class ExecutionEdge:
    """An edge in the strand execution graph."""

    from_node: str
    to_node: str
    condition: Optional[str] = None


@dataclass
class ExecutionGraphSpec:
    """Specification for a strand execution graph."""

    id: str
    name: str
    nodes: List[ExecutionNode]
    edges: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        from datetime import UTC, datetime

        return {
            "id": self.id,
            "name": self.name,
            "description": f"Execution graph for project: {self.name}",
            "nodes": [
                {
                    "id": node.id,
                    "task_id": node.id,  # Use node.id as task_id for compatibility
                    "strand_type": (
                        node.node_type.value
                        if hasattr(node.node_type, "value")
                        else str(node.node_type)
                    ),
                    "dependencies": list(node.dependencies),
                    "conditions": None,
                    "metadata": {
                        "task_title": node.name,
                        "task_complexity": node.complexity,
                        "task_status": "todo",
                        "depth_level": 0,
                        "can_parallelize": False,
                        "assigned_to": None,
                        **node.metadata,
                    },
                }
                for node in self.nodes
            ],
            "edges": self.edges,
            "entry_points": [
                node.id
                for node in self.nodes
                if not any(edge.get("to_node") == node.id for edge in self.edges)
            ],
            "exit_points": [
                node.id
                for node in self.nodes
                if not any(edge.get("from_node") == node.id for edge in self.edges)
            ],
            "created": datetime.now(UTC).isoformat(),
            "updated": datetime.now(UTC).isoformat(),
            "version": "1.0",
            "metadata": {"source_project_id": self.id, **self.metadata},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionGraphSpec":
        """Create from dictionary (JSON deserialization)."""
        nodes = []
        for node_data in data.get("nodes", []):
            # Handle strand_type conversion safely
            strand_type_str = node_data["strand_type"]
            if strand_type_str == "agent":
                node_type = NodeType.AGENT
            elif strand_type_str == "tool":
                node_type = NodeType.TOOL
            elif strand_type_str == "condition":
                node_type = NodeType.CONDITION
            else:
                node_type = NodeType.AGENT  # Default fallback

            node = ExecutionNode(
                id=node_data["id"],
                name=node_data.get("metadata", {}).get("task_title", node_data["id"]),
                node_type=node_type,
                complexity=node_data.get("metadata", {}).get(
                    "task_complexity", "medium"
                ),
                dependencies=set(node_data.get("dependencies", [])),
                metadata=node_data.get("metadata", {}),
            )
            nodes.append(node)

        return cls(
            id=data["id"],
            name=data["name"],
            nodes=nodes,
            edges=data.get("edges", []),
            metadata=data.get("metadata", {}),
        )

    def validate_dag(self) -> bool:
        """Validate that the graph is a valid DAG (no cycles)."""
        # Simple cycle detection using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(node_id: str) -> bool:
            if node_id in rec_stack:
                return True
            if node_id in visited:
                return False

            visited.add(node_id)
            rec_stack.add(node_id)

            # Check all nodes this node points to
            for edge in self.edges:
                if edge.get("from_node") == node_id:
                    to_node = edge.get("to_node")
                    if to_node and has_cycle(to_node):
                        return True

            rec_stack.remove(node_id)
            return False

        # Check each node for cycles
        for node in self.nodes:
            if node.id not in visited:
                if has_cycle(node.id):
                    return False

        return True


@dataclass
class ExecutionRecord:
    """Runtime execution state of a strand graph."""

    id: str
    graph_spec_id: str
    status: ExecutionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutorConfiguration:
    """Configuration for strand executor system."""

    max_parallel_nodes: int = 5
    execution_timeout_seconds: int = 3600
    retry_failed_nodes: bool = True
    max_retries: int = 3
    log_execution_details: bool = True
    auto_cleanup_completed: bool = False
    cleanup_after_days: int = 30

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutorConfiguration":
        """Create from dictionary (JSON deserialization)."""
        return cls(
            max_parallel_nodes=data.get("max_parallel_nodes", 5),
            execution_timeout_seconds=data.get("execution_timeout_seconds", 3600),
            retry_failed_nodes=data.get("retry_failed_nodes", True),
            max_retries=data.get("max_retries", 3),
            log_execution_details=data.get("log_execution_details", True),
            auto_cleanup_completed=data.get("auto_cleanup_completed", False),
            cleanup_after_days=data.get("cleanup_after_days", 30),
        )

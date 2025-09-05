"""DAG analysis and conversion logic for Lackey projects."""

from __future__ import annotations

import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

import networkx as nx

from .models import Project, Task
from .strands.strand_executor import StrandGraphSpec, StrandNode, StrandType

logger = logging.getLogger(__name__)


@dataclass
class DAGAnalysisResult:
    """Result of DAG analysis on a project."""

    project_id: str
    is_valid_dag: bool
    node_count: int
    edge_count: int
    cycles: List[List[str]] = field(default_factory=list)
    entry_points: Set[str] = field(default_factory=set)
    exit_points: Set[str] = field(default_factory=set)
    longest_path: List[str] = field(default_factory=list)
    parallel_chains: List[List[str]] = field(default_factory=list)
    complexity_distribution: Dict[str, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class TaskDependencyMapping:
    """Mapping of task dependencies for conversion."""

    task_id: str
    dependencies: Set[str]
    dependents: Set[str]
    depth_level: int
    can_parallelize: bool


class DAGAnalyzer:
    """Analyzes Lackey project DAGs and converts them to strand graphs."""

    def __init__(self) -> None:
        """Initialize the DAG analyzer."""
        self.graph: Optional[nx.DiGraph] = None
        self.task_mapping: Dict[str, Task] = {}

    def analyze_project(self, project: Project, tasks: List[Task]) -> DAGAnalysisResult:
        """Analyze a project's task dependencies as a DAG."""
        logger.info(f"Analyzing DAG for project {project.id}")

        # Build the dependency graph
        self.graph = self._build_dependency_graph(tasks)
        self.task_mapping = {task.id: task for task in tasks}

        result = DAGAnalysisResult(
            project_id=project.id,
            is_valid_dag=True,
            node_count=len(tasks),
            edge_count=0,
        )

        try:
            # Check for cycles
            cycles = list(nx.simple_cycles(self.graph))
            result.cycles = cycles
            result.is_valid_dag = len(cycles) == 0

            if not result.is_valid_dag:
                result.errors.append(f"Found {len(cycles)} cycles in dependency graph")
                logger.warning(f"Project {project.id} has cycles: {cycles}")

            # Calculate basic metrics
            result.edge_count = self.graph.number_of_edges()

            # Find entry and exit points
            result.entry_points = self._find_entry_points()
            result.exit_points = self._find_exit_points()

            # Find longest path (critical path)
            if result.is_valid_dag:
                result.longest_path = self._find_longest_path()
                result.parallel_chains = self._identify_parallel_chains()

            # Analyze complexity distribution
            result.complexity_distribution = self._analyze_complexity_distribution(
                tasks
            )

            logger.info(
                f"DAG analysis complete: {result.node_count} nodes, "
                f"{result.edge_count} edges, valid={result.is_valid_dag}"
            )

        except Exception as e:
            result.errors.append(f"Analysis failed: {str(e)}")
            result.is_valid_dag = False
            logger.error(f"DAG analysis failed for project {project.id}: {e}")

        return result

    def create_dependency_mappings(
        self, tasks: List[Task]
    ) -> List[TaskDependencyMapping]:
        """Create detailed dependency mappings for tasks."""
        if not self.graph:
            self.graph = self._build_dependency_graph(tasks)

        # Ensure task mapping is set up
        self.task_mapping = {task.id: task for task in tasks}

        mappings = []

        # Calculate depth levels using topological sort
        try:
            topo_order = list(nx.topological_sort(self.graph))
            depth_levels = self._calculate_depth_levels(topo_order)
        except nx.NetworkXError:
            # Graph has cycles, assign default depths
            depth_levels = {task.id: 0 for task in tasks}

        for task in tasks:
            # Get direct dependencies and dependents
            dependencies = set(self.graph.predecessors(task.id))
            dependents = set(self.graph.successors(task.id))

            # Determine if task can be parallelized
            can_parallelize = self._can_parallelize_task(
                task.id, dependencies, dependents
            )

            mapping = TaskDependencyMapping(
                task_id=task.id,
                dependencies=dependencies,
                dependents=dependents,
                depth_level=depth_levels.get(task.id, 0),
                can_parallelize=can_parallelize,
            )
            mappings.append(mapping)

        return mappings

    def convert_to_strand_graph(
        self,
        project: Project,
        tasks: List[Task],
        analysis_result: Optional[DAGAnalysisResult] = None,
    ) -> StrandGraphSpec:
        """Convert project tasks to a strand graph specification."""
        logger.info(f"Converting project {project.id} to strand graph")

        if not analysis_result:
            analysis_result = self.analyze_project(project, tasks)

        if not analysis_result.is_valid_dag:
            raise ValueError(
                f"Cannot convert project with cycles: {analysis_result.cycles}"
            )

        # Create dependency mappings
        mappings = self.create_dependency_mappings(tasks)
        mapping_dict = {m.task_id: m for m in mappings}

        # Create strand nodes
        nodes = []
        for task in tasks:
            mapping = mapping_dict[task.id]

            # Determine strand type based on parallelization potential
            strand_type = (
                StrandType.AGENT if mapping.can_parallelize else StrandType.TOOL
            )

            # Special handling for conditional tasks (based on tags or complexity)
            if "conditional" in task.tags or (
                task.context and "condition" in task.context.lower()
            ):
                strand_type = StrandType.CONDITION

            node = StrandNode(
                id=f"node_{task.id}",
                name=task.title,
                node_type=strand_type,
                complexity=task.complexity.value,
                dependencies={f"node_{dep_id}" for dep_id in mapping.dependencies},
                metadata={
                    "task_id": task.id,
                    "task_title": task.title,
                    "task_complexity": task.complexity.value,
                    "task_status": task.status.value,
                    "depth_level": mapping.depth_level,
                    "can_parallelize": mapping.can_parallelize,
                    "assigned_to": task.assigned_to,
                },
            )
            nodes.append(node)

        # Determine entry and exit points for strand graph
        entry_points = {f"node_{task_id}" for task_id in analysis_result.entry_points}
        exit_points = {f"node_{task_id}" for task_id in analysis_result.exit_points}

        # Create strand graph specification
        graph_spec = StrandGraphSpec(
            id=str(uuid.uuid4()),
            name=f"{project.friendly_name}_execution_graph",
            nodes=nodes,
            metadata={
                "source_project_id": project.id,
                "source_project_name": project.name,
                "task_count": len(tasks),
                "complexity_distribution": analysis_result.complexity_distribution,
                "longest_path_length": len(analysis_result.longest_path),
                "parallel_chain_count": len(analysis_result.parallel_chains),
                "description": f"Execution graph for project: {project.description}",
                "entry_points": entry_points,
                "exit_points": exit_points,
            },
        )

        logger.info(
            f"Created strand graph with {len(nodes)} nodes, "
            f"{len(entry_points)} entry points, {len(exit_points)} exit points"
        )
        return graph_spec

    def _build_dependency_graph(self, tasks: List[Task]) -> nx.DiGraph:
        """Build a NetworkX directed graph from task dependencies."""
        graph = nx.DiGraph()

        # Add all tasks as nodes
        for task in tasks:
            graph.add_node(task.id, task=task)

        # Add dependency edges
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id in graph:
                    graph.add_edge(dep_id, task.id)
                else:
                    logger.warning(
                        f"Task {task.id} depends on non-existent task {dep_id}"
                    )

        return graph

    def _find_entry_points(self) -> Set[str]:
        """Find tasks with no dependencies (entry points)."""
        if not self.graph:
            return set()

        return {node for node in self.graph.nodes() if self.graph.in_degree(node) == 0}

    def _find_exit_points(self) -> Set[str]:
        """Find tasks with no dependents (exit points)."""
        if not self.graph:
            return set()

        return {node for node in self.graph.nodes() if self.graph.out_degree(node) == 0}

    def _find_longest_path(self) -> List[str]:
        """Find the longest path in the DAG (critical path)."""
        if not self.graph or not nx.is_directed_acyclic_graph(self.graph):
            return []

        try:
            # Use NetworkX to find longest path
            longest_path = nx.dag_longest_path(self.graph)
            assert isinstance(longest_path, list)  # nosec B101 - type checking assert
            return longest_path
        except nx.NetworkXError:
            return []

    def _identify_parallel_chains(self) -> List[List[str]]:
        """Identify chains of tasks that can run in parallel."""
        if not self.graph:
            return []

        parallel_chains = []

        try:
            # Group tasks by depth level
            topo_order = list(nx.topological_sort(self.graph))
            depth_levels = self._calculate_depth_levels(topo_order)

            # Group by depth level
            level_groups = defaultdict(list)
            for task_id, level in depth_levels.items():
                level_groups[level].append(task_id)

            # Find parallel chains within each level
            for level, tasks_at_level in level_groups.items():
                if len(tasks_at_level) > 1:
                    # Check if tasks can actually run in parallel (no interdependencies)
                    independent_tasks = self._find_independent_tasks(tasks_at_level)
                    if len(independent_tasks) > 1:
                        parallel_chains.append(independent_tasks)

        except nx.NetworkXError:
            pass

        return parallel_chains

    def _calculate_depth_levels(self, topo_order: List[str]) -> Dict[str, int]:
        """Calculate depth level for each task in topological order."""
        if not self.graph:
            return {}

        depth_levels = {}

        for task_id in topo_order:
            # Depth is max depth of predecessors + 1
            predecessors = list(self.graph.predecessors(task_id))
            if not predecessors:
                depth_levels[task_id] = 0
            else:
                max_pred_depth = max(depth_levels.get(pred, 0) for pred in predecessors)
                depth_levels[task_id] = max_pred_depth + 1

        return depth_levels

    def _find_independent_tasks(self, task_ids: List[str]) -> List[str]:
        """Find tasks that have no dependencies on each other."""
        if not self.graph:
            return task_ids

        independent = []

        for task_id in task_ids:
            # Check if this task depends on or is depended on by other tasks in the list
            has_internal_deps = False

            for other_id in task_ids:
                if other_id != task_id:
                    if self.graph.has_edge(other_id, task_id) or self.graph.has_edge(
                        task_id, other_id
                    ):
                        has_internal_deps = True
                        break

            if not has_internal_deps:
                independent.append(task_id)

        return independent

    def _can_parallelize_task(
        self, task_id: str, dependencies: Set[str], dependents: Set[str]
    ) -> bool:
        """Determine if a task can be parallelized with others."""
        # Task can be parallelized if:
        # 1. It has siblings at the same depth level
        # 2. It doesn't have complex interdependencies
        # 3. It's not marked as sequential-only

        task = self.task_mapping.get(task_id)
        if not task:
            return False

        # Check for sequential-only tags
        if "sequential" in task.tags or "no-parallel" in task.tags:
            return False

        # Check if task has siblings (other tasks with same dependencies)
        siblings = []
        for other_task_id, other_task in self.task_mapping.items():
            if (
                other_task_id != task_id
                and other_task.dependencies == task.dependencies
            ):
                siblings.append(other_task_id)

        return len(siblings) > 0

    def _analyze_complexity_distribution(self, tasks: List[Task]) -> Dict[str, int]:
        """Analyze the distribution of task complexities."""
        distribution = {"low": 0, "medium": 0, "high": 0}

        for task in tasks:
            distribution[task.complexity.value] += 1

        return distribution

    def validate_dag_integrity(self, tasks: List[Task]) -> Tuple[bool, List[str]]:
        """Validate the integrity of the task DAG."""
        errors = []

        # Build graph
        graph = self._build_dependency_graph(tasks)

        # Check for cycles
        try:
            cycles = list(nx.simple_cycles(graph))
            if cycles:
                errors.append(
                    f"Found {len(cycles)} cycles in dependency graph: {cycles}"
                )
        except Exception as e:
            errors.append(f"Failed to check for cycles: {e}")

        # Check for orphaned dependencies
        task_ids = {task.id for task in tasks}
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    errors.append(
                        f"Task {task.id} depends on non-existent task {dep_id}"
                    )

        # Check for self-dependencies
        for task in tasks:
            if task.id in task.dependencies:
                errors.append(f"Task {task.id} has self-dependency")

        # Check for disconnected components
        if graph.number_of_nodes() > 0:
            undirected = graph.to_undirected()
            components = list(nx.connected_components(undirected))
            if len(components) > 1:
                errors.append(f"Graph has {len(components)} disconnected components")

        return len(errors) == 0, errors

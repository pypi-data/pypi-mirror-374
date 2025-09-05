"""DAG analysis and validation for strand graphs."""

from typing import List

import networkx as nx

from ..core.models import ExecutionGraphSpec


class GraphAnalysisService:
    """Analyzes and validates DAG structures."""

    def validate_graph_structure(self, spec: ExecutionGraphSpec) -> bool:
        """Check if the graph specification represents a valid DAG."""
        if not spec.edges:
            return True

        # Build NetworkX graph
        G = nx.DiGraph()

        # Add nodes
        for node in spec.nodes:
            G.add_node(node.id)

        # Add edges
        for edge in spec.edges:
            G.add_edge(edge["from_node"], edge["to_node"])

        # Check for cycles
        result = nx.is_directed_acyclic_graph(G)
        assert isinstance(result, bool)  # nosec B101 - type checking assert
        return result

    def validate_dependencies(self, spec: ExecutionGraphSpec) -> bool:
        """Alias for validate_graph_structure for API compatibility."""
        return self.validate_graph_structure(spec)

    def find_dependency_cycles(self, spec: ExecutionGraphSpec) -> List[List[str]]:
        """Find all cycles in the graph."""
        G = nx.DiGraph()

        for node in spec.nodes:
            G.add_node(node.id)

        for edge in spec.edges:
            G.add_edge(edge["from_node"], edge["to_node"])

        try:
            cycles = list(nx.simple_cycles(G))
            return cycles
        except nx.NetworkXNoCycle:
            return []

    def detect_cycles(self, spec: ExecutionGraphSpec) -> bool:
        """Check if the graph has cycles. Returns True if cycles exist."""
        cycles = self.find_dependency_cycles(spec)
        return len(cycles) > 0

    def get_execution_order(self, spec: ExecutionGraphSpec) -> List[str]:
        """Get topological execution order for nodes."""
        if not self.validate_graph_structure(spec):
            raise ValueError("Cannot determine execution order for cyclic graph")

        G = nx.DiGraph()

        for node in spec.nodes:
            G.add_node(node.id)

        for edge in spec.edges:
            G.add_edge(edge["from_node"], edge["to_node"])

        return list(nx.topological_sort(G))

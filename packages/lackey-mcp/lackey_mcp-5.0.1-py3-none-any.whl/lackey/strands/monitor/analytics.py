"""
Strand Performance Analytics and Optimization System.

This module provides execution analytics, performance tracking, and optimization
recommendations for strand executor performance monitoring.
"""

import json
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class MetricType(Enum):
    """Types of performance metrics."""

    EXECUTION_TIME = "execution_time"
    NODE_COUNT = "node_count"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    RESOURCE_USAGE = "resource_usage"


@dataclass
class PerformanceMetric:
    """Performance metric measurement."""

    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    execution_id: str
    template_id: str
    project_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionReport:
    """Comprehensive execution performance report."""

    execution_id: str
    template_id: str
    project_id: str
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[timedelta]
    status: str
    metrics: List[PerformanceMetric]
    node_performance: Dict[str, Dict[str, Any]]
    recommendations: List[str]
    bottlenecks: List[str]


class ExecutionMetricsService:
    """Collects and analyzes strand execution performance data."""

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize analytics collector."""
        self.storage_path = storage_path or Path.home() / ".lackey" / "analytics"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._active_executions: Dict[str, Dict[str, Any]] = {}
        self._metrics_cache: Dict[str, List[PerformanceMetric]] = {}

    async def record_execution_start_time(
        self,
        execution_id: str,
        template_id: str,
        project_id: str,
        config: Dict[str, Any],
    ) -> None:
        """Record execution start."""
        execution_data = {
            "execution_id": execution_id,
            "template_id": template_id,
            "project_id": project_id,
            "config": config,
            "start_time": datetime.now(),
            "node_timings": {},
            "resource_usage": {},
        }

        self._active_executions[execution_id] = execution_data

        # Record start metric
        metric = PerformanceMetric(
            metric_type=MetricType.EXECUTION_TIME,
            value=0.0,
            unit="seconds",
            timestamp=datetime.now(),
            execution_id=execution_id,
            template_id=template_id,
            project_id=project_id,
            metadata={"event": "start"},
        )

        await self._store_metric(metric)

    async def record_execution_end_time(
        self, execution_id: str, status: str, progress: float = 1.0
    ) -> None:
        """Record execution completion."""
        if execution_id not in self._active_executions:
            return

        execution_data = self._active_executions[execution_id]
        end_time = datetime.now()
        duration = end_time - execution_data["start_time"]

        # Update execution data
        execution_data.update(
            {
                "end_time": end_time,
                "duration": duration,
                "status": status,
                "progress": progress,
            }
        )

        # Record duration metric
        duration_metric = PerformanceMetric(
            metric_type=MetricType.EXECUTION_TIME,
            value=duration.total_seconds(),
            unit="seconds",
            timestamp=end_time,
            execution_id=execution_id,
            template_id=execution_data["template_id"],
            project_id=execution_data["project_id"],
            metadata={"event": "end", "status": status},
        )

        await self._store_metric(duration_metric)

        # Record success/error metric
        success_metric = PerformanceMetric(
            metric_type=(
                MetricType.SUCCESS_RATE
                if status == "completed"
                else MetricType.ERROR_RATE
            ),
            value=1.0,
            unit="count",
            timestamp=end_time,
            execution_id=execution_id,
            template_id=execution_data["template_id"],
            project_id=execution_data["project_id"],
            metadata={"status": status},
        )

        await self._store_metric(success_metric)

        # Store execution data
        await self._store_execution_data(execution_id, execution_data)

    async def record_node_execution_metrics(
        self, execution_id: str, node_id: str, performance_data: Dict[str, Any]
    ) -> None:
        """Record node performance data."""
        if execution_id in self._active_executions:
            self._active_executions[execution_id]["node_timings"][
                node_id
            ] = performance_data

        # Create node metric
        if "duration" in performance_data:
            execution_data = self._active_executions.get(execution_id, {})
            metric = PerformanceMetric(
                metric_type=MetricType.EXECUTION_TIME,
                value=performance_data["duration"],
                unit="seconds",
                timestamp=datetime.now(),
                execution_id=execution_id,
                template_id=execution_data.get("template_id", "unknown"),
                project_id=execution_data.get("project_id", "unknown"),
                metadata={"node_id": node_id, **performance_data},
            )

            await self._store_metric(metric)

    async def generate_report(self, execution_id: str) -> ExecutionReport:
        """Generate performance report."""
        execution_data = await self._load_execution_data(execution_id)
        if not execution_data:
            raise ValueError(f"Execution {execution_id} not found")

        metrics = await self._load_metrics(execution_id)
        bottlenecks = await self._identify_bottlenecks(execution_data, metrics)
        recommendations = await self._generate_recommendations(execution_data, metrics)

        return ExecutionReport(
            execution_id=execution_id,
            template_id=execution_data["template_id"],
            project_id=execution_data["project_id"],
            start_time=execution_data["start_time"],
            end_time=execution_data.get("end_time"),
            duration=execution_data.get("duration"),
            status=execution_data.get("status", "unknown"),
            metrics=metrics,
            node_performance=execution_data.get("node_timings", {}),
            recommendations=recommendations,
            bottlenecks=bottlenecks,
        )

    async def _store_metric(self, metric: PerformanceMetric) -> None:
        """Store performance metric."""
        # Cache metric
        if metric.execution_id not in self._metrics_cache:
            self._metrics_cache[metric.execution_id] = []
        self._metrics_cache[metric.execution_id].append(metric)

        # Store to file
        metrics_file = self.storage_path / f"metrics_{metric.execution_id}.json"
        metrics_data = []

        if metrics_file.exists():
            with open(metrics_file, "r") as f:
                metrics_data = json.load(f)

        metrics_data.append(
            {
                "metric_type": metric.metric_type.value,
                "value": metric.value,
                "unit": metric.unit,
                "timestamp": metric.timestamp.isoformat(),
                "execution_id": metric.execution_id,
                "template_id": metric.template_id,
                "project_id": metric.project_id,
                "metadata": metric.metadata,
            }
        )

        with open(metrics_file, "w") as f:
            json.dump(metrics_data, f, indent=2)

    async def _store_execution_data(
        self, execution_id: str, data: Dict[str, Any]
    ) -> None:
        """Store execution data."""
        execution_file = self.storage_path / f"execution_{execution_id}.json"

        # Convert datetime objects for JSON serialization
        serializable_data = data.copy()
        for key, value in serializable_data.items():
            if isinstance(value, datetime):
                serializable_data[key] = value.isoformat()
            elif isinstance(value, timedelta):
                serializable_data[key] = value.total_seconds()

        with open(execution_file, "w") as f:
            json.dump(serializable_data, f, indent=2)

    async def _load_execution_data(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Load execution data."""
        execution_file = self.storage_path / f"execution_{execution_id}.json"

        if not execution_file.exists():
            result = self._active_executions.get(execution_id)
            return result if isinstance(result, dict) else None

        with open(execution_file, "r") as f:
            data = json.load(f)
            assert isinstance(data, dict)  # nosec B101 - type checking assert

        # Convert ISO strings back to datetime objects
        if "start_time" in data:
            data["start_time"] = datetime.fromisoformat(data["start_time"])
        if "end_time" in data:
            data["end_time"] = datetime.fromisoformat(data["end_time"])
        if "duration" in data:
            data["duration"] = timedelta(seconds=data["duration"])

        return data

    async def _load_metrics(self, execution_id: str) -> List[PerformanceMetric]:
        """Load metrics for execution."""
        # Check cache first
        if execution_id in self._metrics_cache:
            return self._metrics_cache[execution_id]

        metrics_file = self.storage_path / f"metrics_{execution_id}.json"
        if not metrics_file.exists():
            return []

        with open(metrics_file, "r") as f:
            metrics_data = json.load(f)

        metrics = []
        for data in metrics_data:
            metric = PerformanceMetric(
                metric_type=MetricType(data["metric_type"]),
                value=data["value"],
                unit=data["unit"],
                timestamp=datetime.fromisoformat(data["timestamp"]),
                execution_id=data["execution_id"],
                template_id=data["template_id"],
                project_id=data["project_id"],
                metadata=data["metadata"],
            )
            metrics.append(metric)

        return metrics

    async def _identify_bottlenecks(
        self, execution_data: Dict[str, Any], metrics: List[PerformanceMetric]
    ) -> List[str]:
        """Identify performance bottlenecks."""
        bottlenecks = []

        # Analyze node timings
        node_timings = execution_data.get("node_timings", {})
        if node_timings:
            durations = [
                (node_id, data.get("duration", 0))
                for node_id, data in node_timings.items()
            ]
            durations.sort(key=lambda x: x[1], reverse=True)

            if durations:
                slowest_node, slowest_time = durations[0]
                total_time = sum(d[1] for d in durations)

                if slowest_time > total_time * 0.3:  # >30% of total time
                    bottlenecks.append(
                        f"Node '{slowest_node}' is a bottleneck ({slowest_time:.2f}s)"
                    )

        # Analyze overall execution time
        duration = execution_data.get("duration")
        if duration and duration.total_seconds() > 300:  # >5 minutes
            bottlenecks.append(f"Long execution time ({duration.total_seconds():.1f}s)")

        return bottlenecks

    async def _generate_recommendations(
        self, execution_data: Dict[str, Any], metrics: List[PerformanceMetric]
    ) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []

        # Analyze execution patterns
        node_count = len(execution_data.get("node_timings", {}))
        if node_count > 20:
            recommendations.append(
                "Consider breaking large templates into smaller, parallel sub-templates"
            )

        # Analyze error patterns
        error_metrics = [m for m in metrics if m.metric_type == MetricType.ERROR_RATE]
        if error_metrics:
            recommendations.append(
                "Add error handling and retry logic to improve reliability"
            )

        # Analyze performance
        duration = execution_data.get("duration")
        if duration and duration.total_seconds() > 60:
            recommendations.append(
                "Optimize slow operations or add parallel processing"
            )

        return recommendations


class OptimizationEngine:
    """Engine for generating optimization recommendations."""

    def __init__(self, analytics_collector: ExecutionMetricsService):
        """Initialize optimization engine."""
        self.analytics = analytics_collector

    async def analyze_template_performance(self, template_id: str) -> Dict[str, Any]:
        """Analyze performance across all executions of a template."""
        # Get all execution files for this template
        execution_files = list(self.analytics.storage_path.glob("execution_*.json"))
        template_executions = []

        for file in execution_files:
            with open(file, "r") as f:
                data = json.load(f)
                if data.get("template_id") == template_id:
                    template_executions.append(data)

        if not template_executions:
            return {"error": f"No executions found for template {template_id}"}

        # Calculate aggregate metrics
        durations = [
            exec_data.get("duration", 0)
            for exec_data in template_executions
            if exec_data.get("duration")
        ]
        success_count = sum(
            1
            for exec_data in template_executions
            if exec_data.get("status") == "completed"
        )

        recommendations: List[str] = []
        analysis: Dict[str, Any] = {
            "template_id": template_id,
            "total_executions": len(template_executions),
            "success_rate": (
                success_count / len(template_executions) if template_executions else 0
            ),
            "avg_duration": statistics.mean(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "recommendations": recommendations,
        }

        # Generate template-specific recommendations
        if analysis["success_rate"] < 0.8:
            recommendations.append("Low success rate - improve error handling")

        if analysis["avg_duration"] > 300:  # >5 minutes
            recommendations.append("High average duration - optimize performance")

        return analysis

    async def get_project_analytics(self, project_id: str) -> Dict[str, Any]:
        """Get analytics for all executions in a project."""
        execution_files = list(self.analytics.storage_path.glob("execution_*.json"))
        project_executions = []

        for file in execution_files:
            with open(file, "r") as f:
                data = json.load(f)
                if data.get("project_id") == project_id:
                    project_executions.append(data)

        if not project_executions:
            return {"error": f"No executions found for project {project_id}"}

        # Group by template
        templates: Dict[str, List[Dict[str, Any]]] = {}
        for exec_data in project_executions:
            template_id = exec_data.get("template_id", "unknown")
            if template_id not in templates:
                templates[template_id] = []
            templates[template_id].append(exec_data)

        # Calculate project-level metrics
        total_executions = len(project_executions)
        successful_executions = sum(
            1
            for exec_data in project_executions
            if exec_data.get("status") == "completed"
        )

        return {
            "project_id": project_id,
            "total_executions": total_executions,
            "success_rate": (
                successful_executions / total_executions if total_executions else 0
            ),
            "templates": list(templates.keys()),
            "template_counts": {tid: len(execs) for tid, execs in templates.items()},
            "recent_executions": sorted(
                project_executions, key=lambda x: x.get("start_time", ""), reverse=True
            )[:10],
        }


# Integration with existing Lackey core
async def integrate_analytics_with_lackey_core(
    lackey_core: Any, analytics_collector: ExecutionMetricsService
) -> ExecutionMetricsService:
    """Integrate analytics collector with LackeyCore execution methods."""
    # Store original methods
    original_execute = getattr(lackey_core, "execute_graph_template", None)

    if original_execute:

        async def enhanced_execute(*args: Any, **kwargs: Any) -> Any:
            result = await original_execute(*args, **kwargs)

            # Extract execution details for analytics
            if isinstance(result, dict) and "execution_id" in result:
                await analytics_collector.record_execution_start_time(
                    execution_id=result["execution_id"],
                    template_id=kwargs.get("template_id", "unknown"),
                    project_id=kwargs.get("project_id", "unknown"),
                    config=kwargs.get("execution_config", {}),
                )

            return result

        # Replace method
        lackey_core.execute_graph_template = enhanced_execute

    return analytics_collector

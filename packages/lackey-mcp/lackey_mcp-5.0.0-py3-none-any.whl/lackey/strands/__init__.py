"""Strands system - Domain-organized task execution framework."""

# Core domain - Interface to Lackey
from .core.bridge import ExecutionService, TemplateService
from .core.models import (
    ExecutionEdge,
    ExecutionGraphSpec,
    ExecutionNode,
    ExecutionRecord,
    ExecutionStatus,
    ExecutorConfiguration,
    NodeType,
    TaskComplexity,
)
from .core.storage import ExecutionStorageService
from .core.validation import StrandsProfileError
from .execute.pipe_communication import MessageType, PipeMessage, PipeReader, PipeWriter

# Execute domain - Runs and passes messages, updates states
from .execute.runtime_executor import GraphExecutionService

# Generate domain - Makes JSON spec and Python code
from .generate.dag_analyzer import GraphAnalysisService
from .generate.template_generator import PythonCodeGenerator, generate_template
from .generate.template_storage import StrandTemplateStorage

# Monitor domain - Allows to get status of execution
from .monitor.analytics import ExecutionMetricsService

__all__ = [
    # Core domain
    "ExecutionService",
    "TemplateService",
    "ExecutionGraphSpec",
    "ExecutionNode",
    "ExecutionEdge",
    "NodeType",
    "TaskComplexity",
    "ExecutionStatus",
    "ExecutionRecord",
    "ExecutorConfiguration",
    "ExecutionStorageService",
    "StrandsProfileError",
    # Generate domain
    "GraphAnalysisService",
    "PythonCodeGenerator",
    "generate_template",
    "StrandTemplateStorage",
    # Execute domain
    "GraphExecutionService",
    "MessageType",
    "PipeMessage",
    "PipeReader",
    "PipeWriter",
    # Monitor domain
    "ExecutionMetricsService",
]

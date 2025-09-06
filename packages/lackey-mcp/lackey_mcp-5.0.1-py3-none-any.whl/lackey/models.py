"""Core data models for Lackey task management system."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

if TYPE_CHECKING:
    from .storage import LackeyStorage

from .notes import Note, NoteManager, NoteType

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status enumeration."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"


class Complexity(Enum):
    """Task complexity enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ProjectStatus(Enum):
    """Project status enumeration."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class Task:
    """
    Core task model representing a single unit of work.

    Tasks are stored as markdown files with YAML frontmatter and support
    rich documentation, dependency tracking, and progress monitoring.
    """

    id: str
    title: str
    objective: str
    steps: List[str]
    success_criteria: List[str]
    status: TaskStatus
    complexity: Complexity
    created: datetime
    updated: datetime
    context: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    blocks: Set[str] = field(default_factory=set)
    completed_steps: List[int] = field(default_factory=list)
    note_manager: NoteManager = field(default_factory=NoteManager)
    results: Optional[str] = None
    status_history: List[Dict[str, Any]] = field(default_factory=list)
    project_id: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate task data after initialization."""
        if not self.id:
            self.id = str(uuid.uuid4())

    @classmethod
    def create_new(
        cls,
        title: str,
        objective: str,
        steps: List[str],
        success_criteria: List[str],
        complexity: Complexity,
        context: Optional[str] = None,
        assigned_to: Optional[str] = None,
        tags: Optional[List[str]] = None,
        dependencies: Optional[Set[str]] = None,
    ) -> Task:
        """Create a new task with generated ID and timestamps."""
        now = datetime.now(UTC)

        return cls(
            id=str(uuid.uuid4()),
            title=title,
            objective=objective,
            steps=steps,
            success_criteria=success_criteria,
            status=TaskStatus.TODO,
            complexity=complexity,
            created=now,
            updated=now,
            context=context,
            assigned_to=assigned_to,
            tags=tags or [],
            dependencies=dependencies or set(),
        )

    def update_status(self, new_status: TaskStatus, note: Optional[str] = None) -> None:
        """Update task status and timestamp with history tracking."""
        import logging

        logger = logging.getLogger(__name__)

        logger.debug(f"TASK_UPDATE_DEBUG: Task {self.id} update_status called")
        logger.debug(f"TASK_UPDATE_DEBUG: Current status: {self.status}")
        logger.debug(f"TASK_UPDATE_DEBUG: New status: {new_status}")
        logger.debug(f"TASK_UPDATE_DEBUG: Note: {note}")

        old_status = self.status
        self.status = new_status
        self.updated = datetime.now(UTC)

        logger.debug(
            f"TASK_UPDATE_DEBUG: Status updated from {old_status} to {self.status}"
        )

        # Track status change in history
        if old_status != new_status:
            history_entry = {
                "timestamp": self.updated.isoformat(),
                "from_status": old_status.value,
                "to_status": new_status.value,
                "note": note,
            }
            logger.debug(f"TASK_UPDATE_DEBUG: Adding history entry: {history_entry}")
            self.status_history.append(history_entry)
        else:
            logger.debug(f"TASK_UPDATE_DEBUG: No status change, both are {new_status}")

    def add_dependency(self, task_id: str) -> None:
        """Add a dependency to this task."""
        self.dependencies.add(task_id)
        self.updated = datetime.now(UTC)

    def remove_dependency(self, task_id: str) -> None:
        """Remove a dependency from this task."""
        self.dependencies.discard(task_id)
        self.updated = datetime.now(UTC)

    def add_note(
        self,
        content: str,
        note_type: NoteType = NoteType.USER,
        author: Optional[str] = None,
        tags: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Note:
        """Add a rich note to the task."""
        note = self.note_manager.add_note(
            content=content,
            note_type=note_type,
            author=author,
            tags=tags,
            metadata=metadata,
        )
        self.updated = datetime.now(UTC)
        return note

    def add_simple_note(self, note: str) -> Note:
        """Add a simple text note (for backward compatibility)."""
        return self.add_note(note, NoteType.USER)

    def complete_step(self, step_index: int) -> None:
        """Mark a step as completed."""
        if 0 <= step_index < len(self.steps):
            if step_index not in self.completed_steps:
                self.completed_steps.append(step_index)
                self.completed_steps.sort()
                self.updated = datetime.now(UTC)

    def uncomplete_step(self, step_index: int) -> None:
        """Mark a step as incomplete."""
        if step_index in self.completed_steps:
            self.completed_steps.remove(step_index)
            self.updated = datetime.now(UTC)

    def is_ready(self, completed_tasks: Set[str]) -> bool:
        """Check if task is ready to start (all dependencies completed)."""
        return self.status == TaskStatus.TODO and self.dependencies.issubset(
            completed_tasks
        )

    def is_blocked(self, completed_tasks: Set[str]) -> bool:
        """Check if task is blocked by incomplete dependencies."""
        return self.status in (
            TaskStatus.TODO,
            TaskStatus.IN_PROGRESS,
            TaskStatus.BLOCKED,
        ) and not self.dependencies.issubset(completed_tasks)

    def progress_percentage(self) -> float:
        """Calculate completion percentage based on completed steps."""
        if not self.steps:
            return 100.0 if self.status == TaskStatus.DONE else 0.0

        return (len(self.completed_steps) / len(self.steps)) * 100.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "objective": self.objective,
            "steps": self.steps,
            "success_criteria": self.success_criteria,
            "status": self.status.value,
            "complexity": self.complexity.value,
            "created": self.created.isoformat(),
            "updated": self.updated.isoformat(),
            "context": self.context,
            "assigned_to": self.assigned_to,
            "tags": self.tags,
            "dependencies": list(self.dependencies),
            "blocks": list(self.blocks),
            "completed_steps": self.completed_steps,
            "note_manager": self.note_manager.to_dict_list(),
            "results": self.results,
            "status_history": self.status_history,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Task:
        """Create task from dictionary."""
        # Create deferred initialization NoteManager (will be set up by storage layer)
        note_manager = NoteManager()  # No parameters = deferred init mode

        return cls(
            id=data["id"],
            title=data["title"],
            objective=data["objective"],
            steps=data["steps"],
            success_criteria=data["success_criteria"],
            status=TaskStatus(data["status"]),
            complexity=Complexity(data["complexity"]),
            created=datetime.fromisoformat(data["created"]),
            updated=datetime.fromisoformat(data["updated"]),
            context=data.get("context"),
            assigned_to=data.get("assigned_to"),
            tags=data.get("tags", []),
            dependencies=set(data.get("dependencies", [])),
            blocks=set(data.get("blocks", [])),
            completed_steps=data.get("completed_steps", []),
            note_manager=note_manager,
            results=data.get("results"),
            status_history=data.get("status_history", []),
        )


@dataclass
class Project:
    """
    Core project model representing a collection of related tasks.

    Projects provide organizational structure and context for task chains,
    including objectives, metadata, and agent configurations.
    """

    id: str
    name: str  # URL-safe name
    friendly_name: str
    description: str
    status: ProjectStatus
    created: datetime
    objectives: List[str]
    tags: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    tasks: List["Task"] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate project data after initialization."""
        if not self.id:
            self.id = str(uuid.uuid4())

    @classmethod
    def create_new(
        cls,
        friendly_name: str,
        description: str,
        objectives: List[str],
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Project:
        """Create a new project with generated ID and timestamps."""
        # Generate URL-safe name from friendly name
        name = friendly_name.lower().replace(" ", "-").replace("_", "-")
        # Remove non-alphanumeric characters except hyphens
        name = "".join(c for c in name if c.isalnum() or c == "-")
        # Remove consecutive hyphens
        while "--" in name:
            name = name.replace("--", "-")
        name = name.strip("-")

        return cls(
            id=str(uuid.uuid4()),
            name=name,
            friendly_name=friendly_name,
            description=description,
            status=ProjectStatus.ACTIVE,
            created=datetime.now(UTC),
            objectives=objectives,
            tags=tags or [],
            metadata=metadata or {},
        )

    def update_status(self, new_status: ProjectStatus) -> None:
        """Update project status."""
        self.status = new_status
        self.metadata["last_modified"] = datetime.now(UTC).isoformat()

    def add_objective(self, objective: str) -> None:
        """Add an objective to the project."""
        if objective not in self.objectives:
            self.objectives.append(objective)
            self.metadata["last_modified"] = datetime.now(UTC).isoformat()

    def remove_objective(self, objective: str) -> None:
        """Remove an objective from the project."""
        if objective in self.objectives:
            self.objectives.remove(objective)
            self.metadata["last_modified"] = datetime.now(UTC).isoformat()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the project."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.metadata["last_modified"] = datetime.now(UTC).isoformat()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the project."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.metadata["last_modified"] = datetime.now(UTC).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "friendly_name": self.friendly_name,
            "description": self.description,
            "status": self.status.value,
            "created": self.created.isoformat(),
            "objectives": self.objectives,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Project:
        """Create project from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            friendly_name=data["friendly_name"],
            description=data["description"],
            status=ProjectStatus(data["status"]),
            created=datetime.fromisoformat(data["created"]),
            objectives=data["objectives"],
            tags=data["tags"],
            metadata=data.get("metadata", {}),
        )


@dataclass
class ProjectIndex:
    """
    Index of all projects in the repository.

    Provides quick lookup and summary statistics for project management.
    """

    version: str = "1.0"
    projects: List[Dict[str, Any]] = field(
        default_factory=list
    )  # Project metadata and counts
    task_to_project: Dict[str, str] = field(
        default_factory=dict
    )  # task_id -> project_id
    execution_to_project: Dict[str, str] = field(
        default_factory=dict
    )  # execution_id -> project_id
    template_to_project: Dict[str, str] = field(
        default_factory=dict
    )  # template_id -> project_id

    def add_project(
        self, project: Project, task_count: int = 0, completed_count: int = 0
    ) -> None:
        """Add a project to the index."""
        project_entry = {
            "id": project.id,
            "name": project.name,
            "friendly_name": project.friendly_name,
            "created": project.created.isoformat(),
            "status": project.status.value,
            "task_count": task_count,
            "completed_count": completed_count,
        }

        # Remove existing entry if present
        self.projects = [p for p in self.projects if p["id"] != project.id]
        self.projects.append(project_entry)

    def remove_project(self, project_id: str) -> None:
        """Remove a project from the index."""
        self.projects = [p for p in self.projects if p["id"] != project_id]

        # Remove all tasks for this project
        tasks_to_remove = [
            task_id
            for task_id, pid in self.task_to_project.items()
            if pid == project_id
        ]
        for task_id in tasks_to_remove:
            self.task_to_project.pop(task_id, None)

        # Remove all executions for this project
        executions_to_remove = [
            execution_id
            for execution_id, pid in self.execution_to_project.items()
            if pid == project_id
        ]
        for execution_id in executions_to_remove:
            self.execution_to_project.pop(execution_id, None)

        # Remove all templates for this project
        templates_to_remove = [
            template_id
            for template_id, pid in self.template_to_project.items()
            if pid == project_id
        ]
        for template_id in templates_to_remove:
            self.template_to_project.pop(template_id, None)

    def add_task_mapping(self, task_id: str, project_id: str) -> None:
        """Add task-to-project mapping."""
        self.task_to_project[task_id] = project_id

    def remove_task_mapping(self, task_id: str) -> None:
        """Remove task mapping."""
        self.task_to_project.pop(task_id, None)

    def get_task_project(self, task_id: str) -> str | None:
        """Get project ID for a task."""
        return self.task_to_project.get(task_id)

    def add_execution_mapping(self, execution_id: str, project_id: str) -> None:
        """Add execution-to-project mapping."""
        self.execution_to_project[execution_id] = project_id

    def remove_execution_mapping(self, execution_id: str) -> None:
        """Remove execution mapping."""
        self.execution_to_project.pop(execution_id, None)

    def get_execution_mapping(self, execution_id: str) -> str | None:
        """Get project ID for an execution."""
        result = self.execution_to_project.get(execution_id)
        logger.debug(
            f"get_execution_mapping: Looking up execution_id={execution_id}, "
            f"found project_id={result}"
        )
        logger.debug(
            f"get_execution_mapping: Current execution mappings count: "
            f"{len(self.execution_to_project)}"
        )
        return result

    def add_template_mapping(self, template_id: str, project_id: str) -> None:
        """Add template-to-project mapping."""
        self.template_to_project[template_id] = project_id

    def remove_template_mapping(self, template_id: str) -> None:
        """Remove template mapping."""
        self.template_to_project.pop(template_id, None)

    def get_template_mapping(self, template_id: str) -> str | None:
        """Get project ID for a template."""
        return self.template_to_project.get(template_id)

    def rebuild_from_filesystem(self, storage: "LackeyStorage") -> None:
        """Rebuild task and execution mappings from filesystem when index is stale."""
        import logging

        logger = logging.getLogger(__name__)

        logger.debug("rebuild_from_filesystem: Starting index rebuild from filesystem")
        self.task_to_project.clear()
        self.execution_to_project.clear()
        self.template_to_project.clear()

        for project_dict in storage.list_projects():
            project_id = project_dict["id"]
            logger.debug(
                f"rebuild_from_filesystem: Rebuilding mappings for project {project_id}"
            )

            tasks = storage.list_project_tasks(project_id)
            for task in tasks:
                self.add_task_mapping(task.id, project_id)
            logger.debug(
                f"rebuild_from_filesystem: Added {len(tasks)} task mappings "
                f"for project {project_id}"
            )

            # Rebuild execution mappings
            executions = storage.list_project_executions(project_id)
            for execution in executions:
                self.add_execution_mapping(execution["id"], project_id)
            logger.debug(
                f"rebuild_from_filesystem: Added {len(executions)} execution mappings "
                f"for project {project_id}"
            )

            # Rebuild template mappings
            templates = storage.list_project_templates(project_id)
            for template in templates:
                self.add_template_mapping(template["id"], project_id)
            logger.debug(
                f"rebuild_from_filesystem: Added {len(templates)} template "
                f"mappings for project {project_id}"
            )

    def rebuild_full_index_from_filesystem(self, storage: "LackeyStorage") -> None:
        """Rebuild entire index from filesystem on startup.

        Rebuilds projects, tasks, and executions index.
        """
        # Clear all cached data
        self.projects.clear()
        self.task_to_project.clear()
        self.execution_to_project.clear()
        self.template_to_project.clear()

        # Scan filesystem for actual projects
        projects_dir = storage.projects_dir
        if not projects_dir.exists():
            return

        for project_dir in projects_dir.iterdir():
            if not project_dir.is_dir():
                continue

            project_yaml = project_dir / "project.yaml"
            if not project_yaml.exists():
                continue

            try:
                # Load project from filesystem
                project = storage.get_project(project_dir.name)

                # Count tasks
                task_count, completed_count = storage._get_project_task_counts(
                    project_dir.name
                )

                # Add to index
                self.add_project(project, task_count, completed_count)

                # Add task mappings
                tasks = storage.list_project_tasks(project_dir.name)
                for task in tasks:
                    self.add_task_mapping(task.id, project_dir.name)

                # Add execution mappings
                executions = storage.list_project_executions(project_dir.name)
                for execution in executions:
                    self.add_execution_mapping(execution["id"], project_dir.name)

                # Add template mappings
                templates = storage.list_project_templates(project_dir.name)
                for template in templates:
                    self.add_template_mapping(template["id"], project_dir.name)

            except Exception as e:
                # Skip corrupted projects but log the issue
                import logging

                logging.getLogger(__name__).warning(
                    f"Skipping corrupted project {project_dir.name}: {e}"
                )
                continue

    def get_project_entry(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project entry by ID."""
        for project in self.projects:
            if project["id"] == project_id:
                return project
        return None

    def update_task_counts(
        self, project_id: str, task_count: int, completed_count: int
    ) -> None:
        """Update task counts for a project."""
        for project in self.projects:
            if project["id"] == project_id:
                project["task_count"] = task_count
                project["completed_count"] = completed_count
                break

    def to_dict(self) -> Dict[str, Any]:
        """Convert index to dictionary for serialization."""
        return {
            "version": self.version,
            "projects": self.projects,
            "task_to_project": self.task_to_project,
            "execution_to_project": self.execution_to_project,
            "template_to_project": self.template_to_project,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProjectIndex:
        """Create index from dictionary."""
        return cls(
            version=data.get("version", "1.0"),
            projects=data.get("projects", []),
            task_to_project=data.get("task_to_project", {}),
            execution_to_project=data.get("execution_to_project", {}),
            template_to_project=data.get("template_to_project", {}),
        )


@dataclass
class LackeyConfig:
    """
    Configuration settings for Lackey workspace.

    Controls validation rules, agent settings, and operational parameters.
    """

    version: str = "1.0"
    created: datetime = field(default_factory=lambda: datetime.now(UTC))
    workspace: Dict[str, Any] = field(
        default_factory=lambda: {
            "auto_validate_dag": True,
            "archive_completed_chains": True,
            "preserve_archive_days": 90,
            "max_task_file_size_kb": 100,
        }
    )
    ai_agents: Dict[str, Any] = field(
        default_factory=lambda: {
            "max_chain_depth": 10,
            "warn_on_circular_deps": True,
            "complexity_thresholds": {
                "low_max_steps": 5,
                "medium_max_steps": 10,
                "high_min_steps": 8,
            },
        }
    )
    validation: Dict[str, Any] = field(
        default_factory=lambda: {
            "require_objectives": True,
            "require_success_criteria": True,
            "require_complexity_rating": True,
            "max_title_length": 200,
            "max_dependencies": 20,
        }
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for serialization."""
        return {
            "version": self.version,
            "created": self.created.isoformat(),
            "workspace": self.workspace,
            "ai_agents": self.ai_agents,
            "validation": self.validation,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LackeyConfig:
        """Create config from dictionary."""
        return cls(
            version=data.get("version", "1.0"),
            created=(
                datetime.fromisoformat(data["created"])
                if "created" in data
                else datetime.now(UTC)
            ),
            workspace=data.get("workspace", {}),
            ai_agents=data.get("ai_agents", {}),
            validation=data.get("validation", {}),
        )

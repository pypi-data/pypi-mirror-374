"""File-based storage system for Lackey tasks and projects."""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .file_ops import (
    FileOperationError,
    atomic_write,
    ensure_directory,
    read_text_file,
    read_yaml_file,
)
from .models import LackeyConfig, Project, ProjectIndex, Task, TaskStatus

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Raised when storage operations fail."""

    pass


class TaskNotFoundError(StorageError):
    """Raised when a task cannot be found."""

    pass


class ProjectNotFoundError(StorageError):
    """Raised when a project cannot be found."""

    pass


class LackeyStorage:
    """
    File-based storage system for Lackey.

    Manages the .lackey directory structure and provides CRUD operations
    for tasks, projects, and configuration data.
    """

    def __init__(self, lackey_dir_path: str = ".lackey"):
        """Initialize storage with Lackey directory path.

        Args:
            lackey_dir_path: Path to the .lackey directory where files are stored
        """
        self.lackey_dir = Path(lackey_dir_path).resolve()
        self.workspace_path = self.lackey_dir.parent
        self.projects_dir = self.lackey_dir / "projects"
        self.index_file = self.lackey_dir / "index.yaml"
        self.config_file = self.lackey_dir / "config.yaml"
        self._index_rebuilt = False  # Track if we've rebuilt on startup

        # Initialize directory structure
        self._ensure_directory_structure()

    def _ensure_directory_structure(self) -> None:
        """Ensure the .lackey directory structure exists."""
        try:
            ensure_directory(str(self.lackey_dir))
            ensure_directory(str(self.projects_dir))
        except FileOperationError as e:
            raise StorageError(f"Failed to create directory structure: {e}")

    # Project Operations

    def create_project(self, project: Project) -> None:
        """Create a new project with directory structure."""
        project_dir = self.projects_dir / project.id
        tasks_dir = project_dir / "tasks"
        archive_dir = project_dir / "archive"

        try:
            # Create project directories
            ensure_directory(str(project_dir))
            ensure_directory(str(tasks_dir))
            ensure_directory(str(archive_dir))

            # Write project configuration
            project_file = project_dir / "project.yaml"
            with atomic_write(str(project_file)) as op:
                op.write_yaml(project.to_dict())

            # Update project index
            self._update_project_index(project, 0, 0)

        except FileOperationError as e:
            raise StorageError(f"Failed to create project: {e}")

    def get_project(self, project_id: str) -> Project:
        """Get project by ID."""
        project_dir = self.projects_dir / project_id
        project_file = project_dir / "project.yaml"

        if not project_file.exists():
            raise ProjectNotFoundError(f"Project {project_id} not found")

        try:
            data = read_yaml_file(str(project_file))
            return Project.from_dict(data)
        except FileOperationError as e:
            raise StorageError(f"Failed to read project: {e}")

    def update_project(self, project: Project) -> None:
        """Update existing project."""
        project_dir = self.projects_dir / project.id
        project_file = project_dir / "project.yaml"

        if not project_dir.exists():
            raise ProjectNotFoundError(f"Project {project.id} not found")

        try:
            with atomic_write(str(project_file)) as op:
                op.write_yaml(project.to_dict())

            # Update index with current task counts
            task_count, completed_count = self._get_project_task_counts(project.id)
            self._update_project_index(project, task_count, completed_count)

        except FileOperationError as e:
            raise StorageError(f"Failed to update project: {e}")

    def delete_project(self, project_id: str) -> None:
        """Delete project and all its tasks."""
        project_dir = self.projects_dir / project_id

        if not project_dir.exists():
            raise ProjectNotFoundError(f"Project {project_id} not found")

        try:
            # Remove from index first
            self._remove_from_project_index(project_id)

            # Delete project directory
            import shutil

            shutil.rmtree(project_dir)

        except (FileOperationError, OSError) as e:
            raise StorageError(f"Failed to delete project: {e}")

    def list_projects(
        self, status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all projects with optional status filter."""
        try:
            index = self._get_project_index()
            projects = index.projects

            if status_filter:
                projects = [p for p in projects if p.get("status") == status_filter]

            return projects

        except FileOperationError as e:
            raise StorageError(f"Failed to list projects: {e}")

    def find_project_by_name(self, name: str) -> Optional[Project]:
        """Find project by name or friendly name."""
        try:
            index = self._get_project_index()

            for project_entry in index.projects:
                if (
                    project_entry.get("name") == name
                    or project_entry.get("friendly_name") == name
                ):
                    return self.get_project(project_entry["id"])

            return None

        except FileOperationError as e:
            raise StorageError(f"Failed to search projects: {e}")

    # Task Operations

    def create_task(self, project_id: str, task: Task) -> None:
        """Create a new task in the specified project."""
        project_dir = self.projects_dir / project_id
        tasks_dir = project_dir / "tasks"

        if not project_dir.exists():
            raise ProjectNotFoundError(f"Project {project_id} not found")

        task_file = tasks_dir / f"{task.id}.md"

        try:
            # Generate markdown content (without notes)
            content = self._task_to_markdown(task)

            with atomic_write(str(task_file)) as op:
                op.write_content(content)

            # Initialize NoteManager in filesystem mode
            task.note_manager.initialize_filesystem_mode(
                task_id=task.id, project_id=project_id, storage_path=self.lackey_dir
            )

            # Update project task counts
            self._update_project_task_counts(project_id)

            # Add task mapping to index
            index = self._get_project_index()
            index.add_task_mapping(task.id, project_id)
            self._save_project_index(index)

        except FileOperationError as e:
            raise StorageError(f"Failed to create task: {e}")

    def get_task(self, task_id: str) -> Task:
        """Get task by ID from any project."""
        for project_dir in self.projects_dir.iterdir():
            if not project_dir.is_dir():
                continue

            task_file = project_dir / "tasks" / f"{task_id}.md"
            if task_file.exists():
                try:
                    content = read_text_file(str(task_file))
                    task = self._markdown_to_task(content)
                    task.project_id = project_dir.name  # Add project context

                    # Initialize NoteManager in filesystem mode
                    task.note_manager.initialize_filesystem_mode(
                        task_id=task_id,
                        project_id=project_dir.name,
                        storage_path=self.lackey_dir,
                    )

                    return task
                except FileOperationError:
                    continue

        raise TaskNotFoundError(f"Task {task_id} not found")

    def find_project_id_by_task_id(self, task_id: str) -> str:
        """Find which project contains the given task ID."""
        for project_dir in self.projects_dir.iterdir():
            if not project_dir.is_dir():
                continue

            task_file = project_dir / "tasks" / f"{task_id}.md"
            if task_file.exists():
                return project_dir.name

        raise TaskNotFoundError(f"Task {task_id} not found in any project")

    def update_task(self, task: Task) -> None:
        """Update existing task."""
        # Get project from index
        index = self._get_project_index()
        project_id = index.get_task_project(task.id)

        # Rebuild index if task not found
        if not project_id:
            index.rebuild_from_filesystem(self)
            self._save_project_index(index)
            project_id = index.get_task_project(task.id)

        if not project_id:
            raise TaskNotFoundError(f"Task {task.id} not found")

        project_dir = self.projects_dir / project_id
        task_file = project_dir / "tasks" / f"{task.id}.md"

        if not task_file.exists():
            raise TaskNotFoundError(f"Task {task.id} not found in project {project_id}")

        try:
            content = self._task_to_markdown(task)

            with atomic_write(str(task_file)) as op:
                op.write_content(content)

            # Update project task counts if status changed
            self._update_project_task_counts(project_id)

        except FileOperationError as e:
            raise StorageError(f"Failed to update task: {e}")

    def delete_task(self, task_id: str) -> None:
        """Delete task."""
        logger.debug(f"storage.delete_task: Starting deletion of task {task_id}")

        # Get project and file path from index
        index = self._get_project_index()
        project_id = index.get_task_project(task_id)
        logger.debug(
            f"storage.delete_task: Found task {task_id} in project {project_id}"
        )

        # Rebuild index if task not found
        if not project_id:
            logger.debug(
                f"storage.delete_task: Task {task_id} not found in index, rebuilding"
            )
            index.rebuild_from_filesystem(self)
            self._save_project_index(index)
            project_id = index.get_task_project(task_id)

        if not project_id:
            raise TaskNotFoundError(f"Task {task_id} not found")

        # Construct task file path directly
        project_dir = self.projects_dir / project_id
        task_file = project_dir / "tasks" / f"{task_id}.md"
        logger.debug(f"storage.delete_task: Task file path: {task_file}")

        if not task_file.exists():
            raise TaskNotFoundError(f"Task {task_id} file not found")

        try:
            # Delete task file
            logger.debug(f"storage.delete_task: Deleting task file {task_file}")
            task_file.unlink()

            # Delete task directory (contains notes subdirectory)
            task_dir = task_file.parent / task_id
            if task_dir.exists():
                import shutil

                logger.debug(f"storage.delete_task: Deleting task directory {task_dir}")
                shutil.rmtree(task_dir)

            # Update project task counts
            logger.debug(
                f"storage.delete_task: Updating task counts for project {project_id}"
            )
            self._update_project_task_counts(project_id)

            # Remove task mapping from index
            logger.debug(f"storage.delete_task: Removing task mapping for {task_id}")
            index.remove_task_mapping(task_id)
            self._save_project_index(index)
            logger.debug(
                f"storage.delete_task: Successfully completed deletion of "
                f"task {task_id}"
            )

        except (FileOperationError, OSError) as e:
            logger.error(f"storage.delete_task: Failed to delete task {task_id}: {e}")
            raise StorageError(f"Failed to delete task: {e}")

    def list_all_tasks(self, status_filter: Optional[TaskStatus] = None) -> List[Task]:
        """List all tasks across all projects with optional status filter."""
        all_tasks = []

        try:
            # Iterate through all project directories
            for project_dir in self.projects_dir.glob("*"):
                if project_dir.is_dir():
                    project_id = project_dir.name
                    project_tasks = self.list_project_tasks(project_id, status_filter)
                    all_tasks.extend(project_tasks)
        except Exception as e:
            logger.error(f"Failed to list all tasks: {e}")
            raise StorageError(f"Failed to list all tasks: {e}")

        return all_tasks

    def list_project_tasks(
        self, project_id: str, status_filter: Optional[TaskStatus] = None
    ) -> List[Task]:
        """List all tasks in a project with optional status filter."""
        project_dir = self.projects_dir / project_id
        tasks_dir = project_dir / "tasks"

        if not tasks_dir.exists():
            return []

        tasks = []

        try:
            for task_file in tasks_dir.glob("*.md"):
                content = read_text_file(str(task_file))
                task = self._markdown_to_task(content)
                task.project_id = project_id

                # Initialize NoteManager in filesystem mode
                task.note_manager.initialize_filesystem_mode(
                    task_id=task.id, project_id=project_id, storage_path=self.lackey_dir
                )

                if status_filter is None or task.status == status_filter:
                    tasks.append(task)

            return tasks

        except FileOperationError as e:
            raise StorageError(f"Failed to list tasks: {e}")

    def list_project_executions(self, project_id: str) -> List[Dict[str, Any]]:
        """List all executions for a project."""
        logger.debug(
            f"list_project_executions: Listing executions for project {project_id}"
        )
        try:
            executions_dir = self.projects_dir / project_id / "strands" / "executions"
            executions = []

            if executions_dir.exists():
                logger.debug(
                    f"list_project_executions: Executions dir exists: {executions_dir}"
                )
                for execution_file in executions_dir.glob("*.json"):
                    logger.debug(
                        f"list_project_executions: Found exec file: {execution_file}"
                    )
                    execution_data = json.loads(execution_file.read_text())
                    executions.append(
                        {
                            "id": execution_file.stem,
                            "project_id": execution_data.get("project_id", project_id),
                            "status": execution_data.get("status", "unknown"),
                            "created": execution_data.get("created"),
                        }
                    )
            else:
                logger.debug(
                    f"list_project_executions: Executions dir does not exist: "
                    f"{executions_dir}"
                )

            logger.debug(
                f"list_project_executions: Found {len(executions)} executions "
                f"for proj {project_id}"
            )
            return executions
        except Exception as e:
            logger.error(
                f"list_project_executions: Failed to list executions for {project_id}: "
                f"{e}"
            )
            raise StorageError(f"Failed to list project executions: {e}")

    def list_project_templates(self, project_id: str) -> List[Dict[str, Any]]:
        """List all templates for a project."""
        logger.debug(
            f"list_project_templates: Listing templates for project {project_id}"
        )
        try:
            templates = []
            templates_dir = self.projects_dir / project_id / "strands" / "graphs"
            if templates_dir.exists():
                logger.debug(
                    f"list_project_templates: Templates dir exists: {templates_dir}"
                )
                for template_file in templates_dir.glob("*.json"):
                    logger.debug(
                        f"list_project_templates: Found template file: {template_file}"
                    )
                    try:
                        with open(template_file, "r") as f:
                            template_data = json.load(f)
                            templates.append(template_data)
                    except Exception as e:
                        logger.warning(f"Failed to load template {template_file}: {e}")
            else:
                logger.debug(
                    f"list_project_templates: Templates dir does not exist: "
                    f"{templates_dir}"
                )

            logger.debug(
                f"list_project_templates: Found {len(templates)} templates "
                f"for proj {project_id}"
            )
            return templates
        except Exception as e:
            logger.error(
                f"list_project_templates: Failed to list templates for {project_id}: "
                f"{e}"
            )
            return []

    def list_tasks(self, status_filter: Optional[TaskStatus] = None) -> List[Task]:
        """List all tasks across all projects with optional status filter."""
        try:
            index = self._get_project_index()
            all_tasks = []

            for project_entry in index.projects:
                project_id = project_entry["id"]
                tasks = self.list_project_tasks(project_id, status_filter)
                all_tasks.extend(tasks)

            return all_tasks

        except FileOperationError as e:
            raise StorageError(f"Failed to list all tasks: {e}")

    def search_tasks(
        self, query: str, project_id: Optional[str] = None
    ) -> List[Tuple[str, Task]]:
        """Search tasks by content across projects."""
        results = []
        query_lower = query.lower()

        logger.info(f"Storage search_tasks: query='{query}', project_id={project_id}")

        try:
            # Determine which projects to search
            if project_id:
                project_dirs = [self.projects_dir / project_id]
            else:
                project_dirs = [d for d in self.projects_dir.iterdir() if d.is_dir()]

            for proj_dir in project_dirs:
                tasks_dir = proj_dir / "tasks"
                if not tasks_dir.exists():
                    continue

                for task_file in tasks_dir.glob("*.md"):
                    try:
                        content = read_text_file(str(task_file))
                        task = self._markdown_to_task(content)

                        # Search in various fields
                        # Get notes content for search
                        notes_content = []
                        for note in task.note_manager.get_notes():
                            notes_content.append(note.content)

                        searchable_text = " ".join(
                            [
                                task.title,
                                task.objective,
                                task.context or "",
                                " ".join(task.steps),
                                " ".join(task.success_criteria),
                                " ".join(notes_content),
                                task.results or "",
                            ]
                        ).lower()

                        logger.info(
                            f"Task '{task.title}' searchable text: "
                            f"'{searchable_text[:100]}...'"
                        )

                        if query_lower in searchable_text:
                            logger.info(f"Match found in task: {task.title}")
                            results.append((proj_dir.name, task))

                    except FileOperationError:
                        continue  # Skip corrupted files

            return results

        except Exception as e:
            raise StorageError(f"Failed to search tasks: {e}")

    # Archive Operations

    def archive_task(self, project_id: str, task_id: str) -> None:
        """Move completed task to archive."""
        project_dir = self.projects_dir / project_id
        task_file = project_dir / "tasks" / f"{task_id}.md"
        archive_dir = project_dir / "archive"
        archive_file = archive_dir / f"{task_id}.md"

        if not task_file.exists():
            raise TaskNotFoundError(f"Task {task_id} not found")

        try:
            # Ensure archive directory exists
            ensure_directory(str(archive_dir))

            # Move file to archive
            import shutil

            shutil.move(str(task_file), str(archive_file))

            # Update project task counts
            self._update_project_task_counts(project_id)

        except (FileOperationError, OSError) as e:
            raise StorageError(f"Failed to archive task: {e}")

    def restore_task(self, project_id: str, task_id: str) -> None:
        """Restore task from archive."""
        project_dir = self.projects_dir / project_id
        archive_file = project_dir / "archive" / f"{task_id}.md"
        tasks_dir = project_dir / "tasks"
        task_file = tasks_dir / f"{task_id}.md"

        if not archive_file.exists():
            raise TaskNotFoundError(f"Archived task {task_id} not found")

        try:
            # Ensure tasks directory exists
            ensure_directory(str(tasks_dir))

            # Move file from archive
            import shutil

            shutil.move(str(archive_file), str(task_file))

            # Update project task counts
            self._update_project_task_counts(project_id)

        except (FileOperationError, OSError) as e:
            raise StorageError(f"Failed to restore task: {e}")

    # Configuration Operations

    def get_config(self) -> LackeyConfig:
        """Get Lackey configuration."""
        if not self.config_file.exists():
            # Create default configuration
            config = LackeyConfig()
            self.save_config(config)
            return config

        try:
            data = read_yaml_file(str(self.config_file))
            return LackeyConfig.from_dict(data)
        except FileOperationError as e:
            raise StorageError(f"Failed to read configuration: {e}")

    def save_config(self, config: LackeyConfig) -> None:
        """Save Lackey configuration."""
        try:
            with atomic_write(str(self.config_file)) as op:
                op.write_yaml(config.to_dict())
        except FileOperationError as e:
            raise StorageError(f"Failed to save configuration: {e}")

    # Private Helper Methods

    def _get_project_index(self) -> ProjectIndex:
        """Get project index, rebuilding from filesystem on first access."""
        logger.debug(
            f"_get_project_index: Called, _index_rebuilt={self._index_rebuilt}"
        )

        # Rebuild from filesystem on first access to ensure consistency
        if not self._index_rebuilt:
            logger.debug("_get_project_index: First access, rebuilding from filesystem")
            index = ProjectIndex()
            index.rebuild_full_index_from_filesystem(self)
            self._save_project_index(index)
            self._index_rebuilt = True
            logger.debug(
                "_get_project_index: Rebuilt and saved index, returning new index"
            )
            return index

        # Load existing index on subsequent calls
        if not self.index_file.exists():
            logger.debug(
                "_get_project_index: Index file does not exist, creating new index"
            )
            index = ProjectIndex()
            self._save_project_index(index)
            return index

        try:
            logger.debug(
                f"_get_project_index: Loading index from file: {self.index_file}"
            )
            data = read_yaml_file(str(self.index_file))
            index = ProjectIndex.from_dict(data)
            logger.debug(
                f"_get_project_index: Loaded index with {len(index.projects)} projects"
            )
            return index
        except FileOperationError as e:
            logger.error(f"_get_project_index: Failed to read project index: {e}")
            raise StorageError(f"Failed to read project index: {e}")

    def _save_project_index(self, index: ProjectIndex) -> None:
        """Save project index."""
        logger.debug(
            f"_save_project_index: Saving index with {len(index.projects)} "
            f"projects to {self.index_file}"
        )

        # Log project counts for debugging
        for project in index.projects:
            logger.debug(
                f"_save_project_index: Project {project['id']} "
                f"({project['name']}) - task_count: {project['task_count']}, "
                f"completed: {project['completed_count']}"
            )

        try:
            with atomic_write(str(self.index_file)) as op:
                op.write_yaml(index.to_dict())
            logger.debug("_save_project_index: Successfully saved index file")
        except FileOperationError as e:
            logger.error(f"_save_project_index: Failed to save project index: {e}")
            raise StorageError(f"Failed to save project index: {e}")

    def _update_project_index(
        self, project: Project, task_count: int, completed_count: int
    ) -> None:
        """Update project in index."""
        index = self._get_project_index()
        index.add_project(project, task_count, completed_count)
        self._save_project_index(index)

    def _remove_from_project_index(self, project_id: str) -> None:
        """Remove project from index."""
        index = self._get_project_index()
        index.remove_project(project_id)
        self._save_project_index(index)

    def _get_project_task_counts(self, project_id: str) -> Tuple[int, int]:
        """Get task counts for a project."""
        try:
            tasks = self.list_project_tasks(project_id)
            total_count = len(tasks)
            completed_count = len([t for t in tasks if t.status == TaskStatus.DONE])
            return total_count, completed_count
        except StorageError:
            return 0, 0

    def _update_project_task_counts(self, project_id: str) -> None:
        """Update task counts in project index."""
        logger.debug(
            f"_update_project_task_counts: Starting count update for "
            f"project {project_id}"
        )

        task_count, completed_count = self._get_project_task_counts(project_id)
        logger.debug(
            f"_update_project_task_counts: Calculated counts - "
            f"total: {task_count}, completed: {completed_count}"
        )

        index = self._get_project_index()
        logger.debug(
            f"_update_project_task_counts: Loaded index, updating counts "
            f"for project {project_id}"
        )

        index.update_task_counts(project_id, task_count, completed_count)
        self._save_project_index(index)
        logger.debug(
            f"_update_project_task_counts: Successfully updated and saved "
            f"index for project {project_id}"
        )

    def _task_to_markdown(self, task: Task) -> str:
        """Convert task to markdown format with YAML frontmatter (excluding notes)."""
        # Prepare frontmatter data
        frontmatter: Dict[str, Any] = {
            "id": task.id,
            "title": task.title,
            "status": task.status.value,
            "complexity": task.complexity.value,
            "created": task.created.isoformat(),
            "updated": task.updated.isoformat(),
        }

        # Add optional fields if they exist
        if task.assigned_to:
            frontmatter["assigned_to"] = task.assigned_to
        if task.tags:
            frontmatter["tags"] = list(task.tags)
        if task.dependencies:
            logger.debug(f"Serializing dependencies: {task.dependencies}")
            frontmatter["dependencies"] = list(task.dependencies)
        else:
            logger.debug("No dependencies to serialize")
        if task.blocks:
            frontmatter["blocks"] = list(task.blocks)
        if task.status_history:
            frontmatter["status_history"] = task.status_history

        # Build markdown content
        lines = ["---"]

        # Add frontmatter
        import yaml

        yaml_content = yaml.dump(frontmatter, default_flow_style=False)
        lines.extend(yaml_content.strip().split("\n"))
        lines.append("---")
        lines.append("")

        # Add title
        lines.append(f"# {task.title}")
        lines.append("")

        # Add objective
        lines.append("## Objective")
        lines.append(task.objective)
        lines.append("")

        # Add context if present
        if task.context:
            lines.append("## Context")
            lines.append(task.context)
            lines.append("")

        # Add steps
        lines.append("## Steps")
        for i, step in enumerate(task.steps):
            checkbox = "[x]" if i in task.completed_steps else "[ ]"
            lines.append(f"- {checkbox} {step}")
        lines.append("")

        # Add success criteria
        lines.append("## Success Criteria")
        for criterion in task.success_criteria:
            lines.append(f"- {criterion}")
        lines.append("")

        # NOTE: No notes section - notes are stored separately

        # Add results if present
        if task.results:
            lines.append("## Results")
            lines.append(task.results)
            lines.append("")

        return "\n".join(lines)

    def _markdown_to_task(self, content: str) -> Task:
        """Parse markdown content to create Task object."""
        # Split frontmatter and content
        parts = content.split("---", 2)
        if len(parts) < 3:
            raise StorageError("Invalid task file format: missing frontmatter")

        # Parse frontmatter
        try:
            import yaml

            frontmatter = yaml.safe_load(parts[1])
        except yaml.YAMLError as e:
            raise StorageError(f"Invalid YAML frontmatter: {e}")

        # Parse markdown content
        markdown_content = parts[2].strip()

        # Extract sections from markdown
        sections = self._parse_markdown_sections(markdown_content)

        # Build task object (exclude notes - they're stored separately)
        task_data = {
            "id": frontmatter["id"],
            "title": frontmatter["title"],
            "status": frontmatter["status"],
            "complexity": frontmatter["complexity"],
            "created": frontmatter["created"],
            "updated": frontmatter["updated"],
            "assigned_to": frontmatter.get("assigned_to"),
            "tags": frontmatter.get("tags", []),
            "dependencies": set(frontmatter.get("dependencies", [])),
            "blocks": set(frontmatter.get("blocks", [])),
            "status_history": frontmatter.get("status_history", []),
            "objective": sections.get("Objective", ""),
            "context": sections.get("Context"),
            "steps": self._parse_steps(sections.get("Steps", "")),
            "success_criteria": self._parse_list_items(
                sections.get("Success Criteria", "")
            ),
            "results": sections.get("Results"),
        }

        # Extract completed steps
        steps_content = sections.get("Steps", "")
        completed_steps = []
        for i, line in enumerate(steps_content.split("\n")):
            if line.strip().startswith("- [x]"):
                completed_steps.append(i)

        task_data["completed_steps"] = completed_steps

        task = Task.from_dict(task_data)
        return task

    def _parse_markdown_sections(self, content: str) -> Dict[str, str]:
        """Parse markdown content into sections."""
        sections: Dict[str, str] = {}
        current_section: Optional[str] = None
        current_content: List[str] = []

        for line in content.split("\n"):
            if line.startswith("## "):
                # Save previous section if it exists
                if current_section is not None:
                    sections[current_section] = "\n".join(current_content).strip()

                # Start new section
                current_section = line[3:].strip()
                current_content = []
            else:
                current_content.append(line)

        # Save last section if it exists
        if current_section is not None:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def _parse_steps(self, steps_content: str) -> List[str]:
        """Parse steps from markdown list."""
        steps = []
        for line in steps_content.split("\n"):
            line = line.strip()
            if line.startswith("- ["):
                # Remove checkbox and extract step text
                step_text = re.sub(r"^- \[[x ]\] ", "", line)
                steps.append(step_text)
        return steps

    def _parse_list_items(self, content: str) -> List[str]:
        """Parse list items from markdown."""
        items = []
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("- "):
                items.append(line[2:])
        return items

    def _parse_notes(self, notes_content: str) -> List[Dict[str, Any]]:
        """Parse notes from structured markdown content."""
        if not notes_content.strip():
            return []

        notes_data = []
        lines = notes_content.strip().split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Look for note headers: ### Note {id} ({type}) - {timestamp} by {author}
            if line.startswith("### Note "):
                # Parse the header
                import re
                from datetime import UTC, datetime

                # Pattern: ### Note {id} ({type}) - {timestamp}[ by {author}][ #{tags}]
                pattern = (
                    r"### Note ([^\s]+) \(([^)]+)\) - ([^#]+?)"
                    r"(?:\s+by\s+([^#]+?))?(?:\s+(#.+))?$"
                )
                match = re.match(pattern, line)

                if match:
                    note_id, note_type, timestamp_str, author, tags_str = match.groups()

                    # Parse timestamp
                    try:
                        created = datetime.strptime(
                            timestamp_str.strip(), "%Y-%m-%d %H:%M:%S.%f"
                        )
                    except ValueError:
                        created = datetime.now(UTC)

                    # Parse tags
                    tags = []
                    if tags_str:
                        tags = [
                            tag.strip("#") for tag in tags_str.split("#") if tag.strip()
                        ]

                    # Get content between delimiters
                    i += 1
                    content_lines = []
                    metadata: Dict[str, Any] = {}

                    # Look for content start delimiter
                    while (
                        i < len(lines)
                        and lines[i].strip() != "---NOTE-CONTENT-START---"
                    ):
                        i += 1

                    if i < len(lines):
                        i += 1  # Skip the start delimiter

                        # Read content until end delimiter
                        while i < len(lines):
                            if lines[i].strip() == "---NOTE-CONTENT-END---":
                                break
                            content_lines.append(lines[i])
                            i += 1

                    # Create note data with properly trimmed content
                    content = "\n".join(
                        content_lines
                    ).rstrip()  # Remove trailing whitespace/newlines
                    notes_data.append(
                        {
                            "id": note_id,
                            "content": content,
                            "note_type": note_type,
                            "created": created.isoformat(),
                            "author": author.strip() if author else None,
                            "metadata": metadata,
                            "tags": tags,
                        }
                    )

                    # Don't increment i here since the while loop already did
                    continue

            i += 1

        return notes_data

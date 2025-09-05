"""Core task management service for Lackey."""

import logging
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .dependencies import DependencyError, dependency_validator
from .models import Complexity, Project, ProjectStatus, Task, TaskStatus
from .notes import NoteType
from .notifications import NotificationManager
from .storage import (
    LackeyStorage,
    ProjectNotFoundError,
    StorageError,
    TaskNotFoundError,
)
from .strands.core.validation import require_aws_profile
from .validation import ValidationError, validator
from .workflow import StatusTransitionError, StatusWorkflow

# Debug test to validate debug logging is working
logger = logging.getLogger(__name__)
logger.debug("CORE_MODULE_LOADED: Debug logging is active")


class LackeyCore:
    """
    Core task management service for Lackey.

    Orchestrates all task and project operations with validation,
    dependency checking, and error handling.
    """

    def __init__(self, lackey_dir_path: str = ".lackey"):
        """Initialize core service with storage backend.

        Args:
            lackey_dir_path: Path to the .lackey directory where files are stored
        """
        self.lackey_dir = Path(lackey_dir_path)
        self.storage = LackeyStorage(lackey_dir_path)
        self.config = self.storage.get_config()
        self.notifications = NotificationManager()

        # Initialize monitoring system
        from .monitoring import get_logger, initialize_monitoring

        self.monitor = initialize_monitoring(self.lackey_dir)
        self.logger = get_logger(__name__)

        # Initialize advanced search engine
        from .advanced_search import AdvancedSearchEngine

        self.search_engine = AdvancedSearchEngine(self.storage, lackey_dir_path)

        # Initialize advanced dependency analyzer
        from .dependency_analysis import AdvancedDependencyAnalyzer

        self.dependency_analyzer = AdvancedDependencyAnalyzer()

        # Log system initialization
        self.logger.info(
            "Lackey core system initialized",
            lackey_dir=lackey_dir_path,
            config_loaded=bool(self.config),
        )

    # Project Management

    def create_project(
        self,
        friendly_name: str,
        description: str,
        objectives: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Project:
        """
        Create a new project with validation.

        Args:
            friendly_name: Human-readable project name
            description: Project description and goals
            objectives: List of project objectives
            tags: Optional project tags
            metadata: Optional project metadata

        Returns:
            Created Project object

        Raises:
            ValidationError: If input validation fails
            StorageError: If project creation fails
        """
        # Validate input data
        project_data = {
            "friendly_name": friendly_name,
            "description": description,
            "objectives": objectives or [],
            "tags": tags or [],
        }

        validation_errors = validator.validate_project_data(project_data)
        if validation_errors:
            raise ValidationError(
                f"Project validation failed: {'; '.join(validation_errors)}"
            )

        # Create project
        project = Project.create_new(
            friendly_name=friendly_name,
            description=description,
            objectives=objectives or [],
            tags=tags,
            metadata=metadata or {},
        )

        try:
            self.storage.create_project(project)

            # Record successful operation
            self.monitor.record_project_operation("create", project.id, success=True)

            self.logger.info(
                "Created project successfully",
                project_id=project.id,
                friendly_name=project.friendly_name,
                objectives_count=len(objectives or []),
                tags_count=len(tags or []),
            )
            return project

        except StorageError as e:
            # Record failed operation
            self.monitor.record_project_operation("create", project.id, success=False)

            self.logger.error(
                "Failed to create project",
                error=e,
                friendly_name=friendly_name,
                project_id=project.id,
            )
            raise

    def get_project(self, project_id: str) -> Project:
        """Get project by ID or name with associated tasks."""
        try:
            # Try by ID first
            project = self.storage.get_project(project_id)
            if project is None:
                raise ProjectNotFoundError(f"Project {project_id} not found")
        except ProjectNotFoundError:
            # Try by name
            found_project = self.storage.find_project_by_name(project_id)
            if not found_project:
                raise ProjectNotFoundError(f"Project '{project_id}' not found")
            project = found_project

        # Load associated tasks
        try:
            project.tasks = self.storage.list_project_tasks(project.id)
        except StorageError as e:
            logger.warning(f"Failed to load tasks for project {project.id}: {e}")
            project.tasks = []

        return project

    def update_project(self, project_id: str, **updates: Any) -> Project:
        """Update project with validation."""
        project = self.get_project(project_id)

        # Apply updates
        if "friendly_name" in updates:
            project.friendly_name = updates["friendly_name"]
            # Also update the URL-safe name
            name = updates["friendly_name"].lower().replace(" ", "-").replace("_", "-")
            name = "".join(c for c in name if c.isalnum() or c == "-")
            project.name = name

        if "name" in updates:
            project.name = updates["name"]

        if "description" in updates:
            project.description = updates["description"]

        if "objectives" in updates:
            project.objectives = updates["objectives"]

        if "tags" in updates:
            project.tags = updates["tags"]

        if "status" in updates:
            status = ProjectStatus(updates["status"])
            project.update_status(status)

        # Validate updated data
        validation_errors = validator.validate_project_data(
            {
                "friendly_name": project.friendly_name,
                "description": project.description,
                "objectives": project.objectives,
                "tags": project.tags,
            }
        )

        if validation_errors:
            raise ValidationError(
                f"Project update validation failed: {'; '.join(validation_errors)}"
            )

        try:
            self.storage.update_project(project)
            logger.info(f"Updated project: {project.friendly_name}")
            return project

        except StorageError as e:
            logger.error(f"Failed to update project {project_id}: {e}")
            raise

    def delete_project(self, project_id: str) -> None:
        """Delete project only if it has no tasks."""
        project = self.storage.get_project(project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        # Check if project has tasks
        tasks = self.storage.list_project_tasks(project_id)
        if tasks:
            raise ValueError(
                f"Cannot delete project '{project.friendly_name}' - "
                f"it contains {len(tasks)} task(s). Delete all tasks first."
            )

        try:
            self.storage.delete_project(project.id)
            logger.info(f"Deleted project: {project.friendly_name}")

        except StorageError as e:
            logger.error(f"Failed to delete project {project_id}: {e}")
            raise

    def list_projects(
        self, status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all projects with optional status filter."""
        try:
            return self.storage.list_projects(status_filter)
        except StorageError as e:
            logger.error(f"Failed to list projects: {e}")
            raise

    def list_tasks(
        self, project_id: Optional[str] = None, status_filter: Optional[str] = None
    ) -> List[Task]:
        """List tasks with optional project and status filtering."""
        try:
            from .models import TaskStatus

            status_enum = TaskStatus(status_filter) if status_filter else None

            if project_id:
                # Get project to validate it exists
                project = self.get_project(project_id)
                return self.storage.list_project_tasks(project.id, status_enum)
            else:
                # List all tasks across all projects
                return self.storage.list_all_tasks(status_enum)
        except StorageError as e:
            logger.error(f"Failed to list tasks: {e}")
            raise

    # Task Management

    def create_task(
        self,
        project_id: str,
        title: str,
        objective: str,
        steps: List[str],
        success_criteria: List[str],
        complexity: str,
        context: Optional[str] = None,
        assigned_to: Optional[str] = None,
        tags: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
    ) -> Task:
        """
        Create a new task with validation and dependency checking.

        Args:
            project_id: Project ID or name
            title: Task title
            objective: Task objective
            steps: List of task steps
            success_criteria: List of success criteria
            complexity: Task complexity (low/medium/high)
            context: Optional task context
            assigned_to: Optional assignee
            tags: Optional task tags
            dependencies: Optional list of dependency task IDs

        Returns:
            Created Task object

        Raises:
            ValidationError: If input validation fails
            DependencyError: If dependency validation fails
            StorageError: If task creation fails
        """
        # Get project to ensure it exists
        project = self.get_project(project_id)

        # Validate input data
        task_data = {
            "title": title,
            "objective": objective,
            "steps": steps,
            "success_criteria": success_criteria,
            "complexity": complexity,
            "context": context,
            "assigned_to": assigned_to,
            "tags": tags or [],
            "dependencies": dependencies or [],
        }

        validation_errors = validator.validate_task_data(task_data)
        if validation_errors:
            raise ValidationError(
                f"Task validation failed: {'; '.join(validation_errors)}"
            )

        # Create task
        task = Task.create_new(
            title=title,
            objective=objective,
            steps=steps,
            success_criteria=success_criteria,
            complexity=Complexity(complexity),
            context=context,
            assigned_to=assigned_to,
            tags=tags,
            dependencies=set(dependencies or []),
        )

        # Validate dependencies if any
        if dependencies:
            self._validate_task_dependencies(project.id, task, dependencies)

            # Auto-block task if dependencies are not complete
            dependency_statuses = self._get_dependency_statuses(
                project.id, task.dependencies
            )
            if StatusWorkflow.should_auto_block(task, dependency_statuses):
                task.update_status(
                    TaskStatus.BLOCKED, "Auto-blocked due to incomplete dependencies"
                )

        try:
            self.storage.create_task(project.id, task)

            # Update search index
            self.search_engine.update_task_index(project.id, task)

            logger.info(
                f"Created task: {task.title} ({task.id}) in project "
                f"{project.friendly_name}"
            )
            return task

        except StorageError as e:
            logger.error(f"Failed to create task {title}: {e}")
            raise

    def get_task(self, task_id: str) -> Task:
        """Get task by ID from any project."""
        try:
            return self.storage.get_task(task_id)
        except TaskNotFoundError:
            logger.error(f"Task {task_id} not found")
            raise

    def update_task(self, project_id: str, task_id: str, **updates: Any) -> Task:
        """Update task with validation."""
        project = self.get_project(project_id)
        task = self.storage.get_task(task_id)

        # Apply updates
        if "title" in updates:
            task.title = updates["title"]

        if "objective" in updates:
            task.objective = updates["objective"]

        if "context" in updates:
            task.context = updates["context"]

        if "steps" in updates:
            task.steps = updates["steps"]

        if "success_criteria" in updates:
            task.success_criteria = updates["success_criteria"]

        if "complexity" in updates:
            task.complexity = Complexity(updates["complexity"])

        if "assigned_to" in updates:
            task.assigned_to = updates["assigned_to"]

        if "tags" in updates:
            task.tags = updates["tags"]

        if "status" in updates:
            status = TaskStatus(updates["status"])
            task.update_status(status)

        if "results" in updates:
            task.results = updates["results"]

        # Validate updated data
        task_data = {
            "title": task.title,
            "objective": task.objective,
            "steps": task.steps,
            "success_criteria": task.success_criteria,
            "complexity": task.complexity.value,
            "context": task.context,
            "assigned_to": task.assigned_to,
            "tags": task.tags,
            "dependencies": list(task.dependencies),
        }

        validation_errors = validator.validate_task_data(task_data)
        if validation_errors:
            raise ValidationError(
                f"Task update validation failed: {'; '.join(validation_errors)}"
            )

        try:
            self.storage.update_task(task)

            # Update search index
            self.search_engine.update_task_index(project.id, task)

            logger.info(f"Updated task: {task.title}")
            return task

        except StorageError as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            raise

    def update_task_progress(
        self,
        project_id: str,
        task_id: str,
        completed_steps: Optional[List[int]] = None,
        uncomplete_steps: Optional[List[int]] = None,
        add_note: Optional[str] = None,
        append_to_results: Optional[str] = None,
    ) -> Task:
        """Update task progress with completed steps and notes."""
        task = self.storage.get_task(task_id)

        # Update completed steps
        if completed_steps:
            for step_index in completed_steps:
                task.complete_step(step_index)

        if uncomplete_steps:
            for step_index in uncomplete_steps:
                task.uncomplete_step(step_index)

        # Add note
        if add_note:
            task.add_note(add_note)

        # Append to results
        if append_to_results:
            if task.results:
                task.results += f"\n\n{append_to_results}"
            else:
                task.results = append_to_results
            task.updated = datetime.now(UTC)

        try:
            self.storage.update_task(task)
            logger.info(f"Updated progress for task: {task.title}")
            return task

        except StorageError as e:
            logger.error(f"Failed to update task progress {task_id}: {e}")
            raise

    def delete_task(self, task_id: str) -> None:
        """Delete task with dependency validation."""
        logger.debug(f"delete_task: Starting deletion of task {task_id}")

        # Get the task and find its project
        task = self.storage.get_task(task_id)
        logger.debug(
            f"delete_task: Found task '{task.title}' in project {task.project_id}"
        )

        # Check if other tasks depend on this one across all projects
        all_projects = self.storage.list_projects()
        dependent_tasks = []

        for project in all_projects:
            project_tasks = self.storage.list_project_tasks(project["id"])
            dependent_tasks.extend(
                [t for t in project_tasks if task_id in t.dependencies]
            )

        if dependent_tasks:
            dependent_titles = [t.title for t in dependent_tasks]
            logger.debug(f"delete_task: Task {task_id} has dependencies, cannot delete")
            raise DependencyError(
                f"Cannot delete task '{task.title}' - it is required by: "
                f"{', '.join(dependent_titles)}"
            )

        try:
            logger.debug(f"delete_task: Calling storage.delete_task for {task_id}")
            self.storage.delete_task(task_id)
            logger.debug(
                f"delete_task: Successfully completed deletion of task {task_id}"
            )
            logger.info(f"Deleted task: {task.title}")

        except StorageError as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            raise

    def list_project_tasks(
        self, project_id: str, status_filter: Optional[str] = None
    ) -> List[Task]:
        """List all tasks in a project with optional status filter."""
        project = self.get_project(project_id)

        status_enum = TaskStatus(status_filter) if status_filter else None

        try:
            return self.storage.list_project_tasks(project.id, status_enum)
        except StorageError as e:
            logger.error(f"Failed to list tasks for project {project_id}: {e}")
            raise

    # Dependency Management

    def add_task_dependency(
        self, project_id: str, task_id: str, depends_on: str, validate: bool = True
    ) -> Task:
        """Add a dependency to a task with validation."""
        project = self.get_project(project_id)
        task = self.storage.get_task(task_id)

        # Validate dependency if requested
        if validate:
            all_tasks = self.storage.list_project_tasks(project.id)
            can_add, error_msg = dependency_validator.can_add_dependency(
                task_id, depends_on, all_tasks
            )

            if not can_add:
                raise DependencyError(f"Cannot add dependency: {error_msg}")

        # Add dependency
        task.add_dependency(depends_on)

        try:
            self.storage.update_task(task)
            logger.info(f"Added dependency {depends_on} to task {task.title}")
            return task

        except StorageError as e:
            logger.error(f"Failed to add dependency: {e}")
            raise

    def remove_task_dependency(
        self, project_id: str, task_id: str, dependency_id: str
    ) -> Task:
        """Remove a dependency from a task."""
        task = self.storage.get_task(task_id)

        if dependency_id not in task.dependencies:
            raise DependencyError(f"Task {task_id} does not depend on {dependency_id}")

        task.remove_dependency(dependency_id)

        try:
            self.storage.update_task(task)
            logger.info(f"Removed dependency {dependency_id} from task {task.title}")
            return task

        except StorageError as e:
            logger.error(f"Failed to remove dependency: {e}")
            raise

    def validate_project_dependencies(
        self, project_id: str, fix_cycles: bool = False
    ) -> Dict[str, Any]:
        """Validate all dependencies in a project."""
        project = self.get_project(project_id)
        tasks = self.storage.list_project_tasks(project.id)

        try:
            analysis = dependency_validator.validate_dag(tasks)

            # Fix cycles if requested and cycles exist
            if fix_cycles and analysis.cycles:
                suggestions = dependency_validator.suggest_dependency_removal(tasks)
                fixed_count = 0

                for task_id, dep_id, reason in suggestions:
                    try:
                        self.remove_task_dependency(project.id, task_id, dep_id)
                        fixed_count += 1
                        logger.info(f"Fixed cycle by removing dependency: {reason}")
                    except Exception as e:
                        logger.warning(f"Failed to fix cycle: {e}")

                # Re-validate after fixes
                if fixed_count > 0:
                    tasks = self.storage.list_project_tasks(project.id)
                    analysis = dependency_validator.validate_dag(tasks)
                    analysis.to_dict()["cycles_fixed"] = fixed_count

            return analysis.to_dict()

        except Exception as e:
            logger.error(f"Failed to validate dependencies: {e}")
            raise DependencyError(f"Dependency validation failed: {e}")

    # Task Chain Analysis

    def get_ready_tasks(
        self,
        project_id: str,
        complexity: Optional[str] = None,
        assigned_to: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> List[Task]:
        """Get tasks ready to start with optional filters."""
        project = self.get_project(project_id)
        tasks = self.storage.list_project_tasks(project.id)

        # Get completed task IDs
        completed_tasks = {t.id for t in tasks if t.status == TaskStatus.DONE}

        # Find ready tasks
        ready_tasks = []
        for task in tasks:
            if task.is_ready(completed_tasks):
                # Apply filters
                if complexity and task.complexity.value != complexity:
                    continue

                if assigned_to and task.assigned_to != assigned_to:
                    continue

                if tags:
                    if not any(tag in task.tags for tag in tags):
                        continue

                ready_tasks.append(task)

        # Apply limit
        if limit:
            ready_tasks = ready_tasks[:limit]

        return ready_tasks

    def get_blocked_tasks(
        self, project_id: str, include_blocking_tasks: bool = True
    ) -> Dict[str, Any]:
        """Get tasks blocked by incomplete dependencies."""
        project = self.get_project(project_id)
        tasks = self.storage.list_project_tasks(project.id)

        # Get completed task IDs
        completed_tasks = {t.id for t in tasks if t.status == TaskStatus.DONE}

        # Find blocked tasks
        blocked_info: List[Dict[str, Any]] = []
        for task in tasks:
            if task.is_blocked(completed_tasks):
                blocking_deps = task.dependencies - completed_tasks

                task_info: Dict[str, Any] = {
                    "task": task.to_dict(),
                    "blocking_dependencies": list(blocking_deps),
                }

                if include_blocking_tasks:
                    blocking_tasks: List[Dict[str, Any]] = []
                    for dep_id in blocking_deps:
                        try:
                            dep_task = self.storage.get_task(dep_id)
                            blocking_tasks.append(dep_task.to_dict())
                        except TaskNotFoundError:
                            # Dependency task not found - orphaned dependency
                            blocking_tasks.append(
                                {
                                    "id": dep_id,
                                    "title": "MISSING TASK",
                                    "status": "missing",
                                }
                            )

                    task_info["blocking_tasks"] = blocking_tasks

                blocked_info.append(task_info)

        return {"blocked_tasks": blocked_info, "total_blocked": len(blocked_info)}

    def get_task_chain(
        self,
        project_id: str,
        task_id: str,
        direction: str = "both",
        max_depth: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get task dependency chain information."""
        project = self.get_project(project_id)
        tasks = self.storage.list_project_tasks(project.id)

        try:
            chain_info = dependency_validator.get_task_chain_info(task_id, tasks)

            result: Dict[str, Any] = {
                "task_info": chain_info.to_dict(),
                "chain_details": {},
            }

            # Add detailed task information based on direction
            if direction in ("upstream", "both"):
                upstream_tasks = []
                for upstream_id in chain_info.upstream_tasks:
                    try:
                        upstream_task = self.storage.get_task(upstream_id)
                        upstream_tasks.append(upstream_task.to_dict())
                    except TaskNotFoundError:
                        upstream_tasks.append(
                            {
                                "id": upstream_id,
                                "title": "MISSING TASK",
                                "status": "missing",
                            }
                        )

                result["chain_details"]["upstream"] = upstream_tasks

            if direction in ("downstream", "both"):
                downstream_tasks = []
                for downstream_id in chain_info.downstream_tasks:
                    try:
                        downstream_task = self.storage.get_task(downstream_id)
                        downstream_tasks.append(downstream_task.to_dict())
                    except TaskNotFoundError:
                        downstream_tasks.append(
                            {
                                "id": downstream_id,
                                "title": "MISSING TASK",
                                "status": "missing",
                            }
                        )

                result["chain_details"]["downstream"] = downstream_tasks

            return result

        except DependencyError as e:
            logger.error(f"Failed to get task chain: {e}")
            raise

    def analyze_critical_path(
        self, project_id: str, weight_by: str = "complexity"
    ) -> Dict[str, Any]:
        """Analyze critical path through project tasks."""
        project = self.get_project(project_id)
        tasks = self.storage.list_project_tasks(project.id)

        try:
            analysis = dependency_validator.validate_dag(tasks)

            if not analysis.is_valid:
                raise DependencyError(
                    "Cannot analyze critical path with circular dependencies"
                )

            # Get detailed information about critical path tasks
            critical_path_details = []
            for task_id in analysis.critical_path:
                try:
                    task = self.storage.get_task(task_id)
                    critical_path_details.append(task.to_dict())
                except TaskNotFoundError:
                    critical_path_details.append(
                        {"id": task_id, "title": "MISSING TASK", "status": "missing"}
                    )

            return {
                "critical_path": analysis.critical_path,
                "critical_path_details": critical_path_details,
                "path_length": len(analysis.critical_path),
                "max_depth": analysis.max_depth,
                "weight_by": weight_by,
            }

        except Exception as e:
            logger.error(f"Failed to analyze critical path: {e}")
            raise DependencyError(f"Critical path analysis failed: {e}")

    # Search and Reporting

    def search_tasks(
        self,
        query: str,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        complexity: Optional[str] = None,
        tags: Optional[List[str]] = None,
        assigned_to: Optional[str] = None,
        has_dependencies: Optional[bool] = None,
        is_blocked: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Search tasks with comprehensive filtering."""
        try:
            # Debug logging
            logger.info(
                f"search_tasks called with: query='{query}', "
                f"project_id={project_id}, complexity={complexity}, "
                f"assigned_to={assigned_to}, tags={tags}, status={status}"
            )

            # If we have filtering criteria (but not just project_id), get all
            # project tasks and apply filters rather than doing text search
            has_filters = any(
                [status, complexity, tags, assigned_to, has_dependencies, is_blocked]
            )

            if has_filters and project_id:
                # Get all tasks from the project for filtering
                project_tasks = self.storage.list_project_tasks(project_id)
                results = [(project_id, task) for task in project_tasks]
            else:
                # Use text search (includes notes content)
                results = self.storage.search_tasks(query, project_id)

            # Apply additional filters
            filtered_results = []
            for proj_id, task in results:
                # Status filter
                if status and task.status.value != status:
                    continue

                # Complexity filter
                if complexity and task.complexity.value != complexity:
                    continue

                # Tags filter (ANY match)
                if tags:
                    tag_matches = [tag in task.tags for tag in tags]
                    if not any(tag_matches):
                        continue

                # Assigned to filter
                if assigned_to and task.assigned_to != assigned_to:
                    continue

                # Dependencies filter
                if has_dependencies is not None:
                    has_deps = len(task.dependencies) > 0
                    if has_dependencies != has_deps:
                        continue

                # Blocked filter
                if is_blocked is not None:
                    # Get project tasks to check blocking status
                    try:
                        project_tasks = self.storage.list_project_tasks(proj_id)
                        completed_tasks = {
                            t.id for t in project_tasks if t.status == TaskStatus.DONE
                        }
                        blocked = task.is_blocked(completed_tasks)

                        if is_blocked != blocked:
                            continue
                    except StorageError:
                        continue

                filtered_results.append({"project_id": proj_id, "task": task.to_dict()})

            return filtered_results

        except StorageError as e:
            logger.error(f"Failed to search tasks: {e}")
            raise

    def advanced_search(
        self,
        text_query: Optional[str] = None,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        complexity: Optional[str] = None,
        assigned_to: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_progress: Optional[int] = None,
        max_progress: Optional[int] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        limit: Optional[int] = None,
        offset: int = 0,
        include_archived: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute an advanced search with filtering, sorting, and faceted results.

        Args:
            text_query: Text to search for across all fields
            project_id: Filter by project ID
            status: Filter by task status
            complexity: Filter by task complexity
            assigned_to: Filter by assignee
            tags: Filter by tags (any match)
            min_progress: Minimum progress percentage
            max_progress: Maximum progress percentage
            created_after: Filter tasks created after this date (ISO format)
            created_before: Filter tasks created before this date (ISO format)
            sort_by: Field to sort by (title, created_at, progress, etc.)
            sort_order: Sort order (asc or desc)
            limit: Maximum number of results
            offset: Number of results to skip
            include_archived: Include archived tasks

        Returns:
            Dictionary with search results, facets, and metadata
        """
        from .advanced_search import SearchField, SortOrder

        try:
            # Build search query
            query_builder = self.search_engine.create_query_builder()

            # Add text query
            if text_query:
                query_builder.text(text_query)

            # Add filters
            if status:
                from .models import TaskStatus

                query_builder.filter_by_status(TaskStatus(status))

            if complexity:
                from .models import Complexity

                query_builder.filter_by_complexity(Complexity(complexity))

            if assigned_to:
                query_builder.filter_by_assignee(assigned_to)

            if tags:
                for tag in tags:
                    query_builder.filter_by_tag(tag)

            if min_progress is not None or max_progress is not None:
                query_builder.filter_by_progress(min_progress, max_progress)

            # Add date filters
            if created_after or created_before:
                start_date = (
                    datetime.fromisoformat(created_after) if created_after else None
                )
                end_date = (
                    datetime.fromisoformat(created_before) if created_before else None
                )
                query_builder.filter_by_date_range(
                    SearchField.CREATED_AT, start_date, end_date
                )

            # Add sorting
            if sort_by:
                sort_field_map = {
                    "title": SearchField.TITLE,
                    "created_at": SearchField.CREATED_AT,
                    "updated_at": SearchField.UPDATED_AT,
                    "progress": SearchField.PROGRESS,
                    "status": SearchField.STATUS,
                    "complexity": SearchField.COMPLEXITY,
                }
                if sort_by in sort_field_map:
                    sort_order_enum = (
                        SortOrder.DESC
                        if sort_order.lower() == "desc"
                        else SortOrder.ASC
                    )
                    query_builder.query.add_sort(
                        sort_field_map[sort_by], sort_order_enum
                    )

            # Add pagination
            if limit:
                query_builder.limit(limit)
            if offset:
                query_builder.offset(offset)

            # Include archived
            query_builder.include_archived(include_archived)

            # Execute search
            search_query = query_builder.build()
            result = self.search_engine.search(search_query, project_id)

            # Format response
            return {
                "tasks": [
                    {
                        "project_id": proj_id,
                        "task": task.to_dict(),
                    }
                    for proj_id, task in result.tasks
                ],
                "total_count": result.total_count,
                "execution_time_ms": result.execution_time_ms,
                "facets": result.facets,
                "query": {
                    "text": text_query,
                    "filters": {
                        "status": status,
                        "complexity": complexity,
                        "assigned_to": assigned_to,
                        "tags": tags,
                        "min_progress": min_progress,
                        "max_progress": max_progress,
                        "created_after": created_after,
                        "created_before": created_before,
                    },
                    "sort_by": sort_by,
                    "sort_order": sort_order,
                    "limit": limit,
                    "offset": offset,
                    "include_archived": include_archived,
                },
            }

        except Exception as e:
            logger.error(f"Advanced search failed: {e}")
            raise

    def get_search_suggestions(
        self, field: str, partial_value: str, limit: int = 10
    ) -> List[str]:
        """
        Get autocomplete suggestions for a search field.

        Args:
            field: Field name (status, complexity, assigned_to, tags)
            partial_value: Partial value to complete
            limit: Maximum suggestions to return

        Returns:
            List of suggested completions
        """
        from .advanced_search import SearchField

        try:
            field_map = {
                "status": SearchField.STATUS,
                "complexity": SearchField.COMPLEXITY,
                "assigned_to": SearchField.ASSIGNED_TO,
                "tags": SearchField.TAGS,
            }

            if field not in field_map:
                return []

            return self.search_engine.suggest_completions(
                field_map[field], partial_value, limit
            )

        except Exception as e:
            logger.error(f"Failed to get search suggestions: {e}")
            return []

    def get_search_stats(self) -> Dict[str, Any]:
        """
        Get search engine statistics.

        Returns:
            Dictionary of search statistics
        """
        try:
            return self.search_engine.get_search_stats()
        except Exception as e:
            logger.error(f"Failed to get search stats: {e}")
            return {}

    def get_system_health(self) -> Dict[str, Any]:
        """
        Get comprehensive system health status.

        Returns:
            Dictionary with system health information

        Raises:
            Exception: If system health cannot be retrieved
        """
        return self.monitor.get_system_health()

    def get_system_diagnostics(self) -> Dict[str, Any]:
        """
        Get comprehensive system diagnostics.

        Returns:
            Dictionary with diagnostic information

        Raises:
            Exception: If system diagnostics cannot be retrieved
        """
        return self.monitor.export_diagnostics()

    def get_performance_metrics(self, hours: int = 1) -> Dict[str, Any]:
        """
        Get performance metrics for the specified time period.

        Args:
            hours: Number of hours to look back

        Returns:
            Dictionary with performance metrics

        Raises:
            Exception: If performance metrics cannot be retrieved
        """
        since = datetime.now(UTC) - timedelta(hours=hours)
        return self.monitor.get_performance_summary(since=since)

    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get error summary for the specified time period.

        Args:
            hours: Number of hours to look back

        Returns:
            Dictionary with error summary

        Raises:
            Exception: If error summary cannot be retrieved
        """
        since = datetime.now(UTC) - timedelta(hours=hours)
        return self.monitor.get_error_summary(since=since)

    def get_system_logs(
        self,
        level: Optional[str] = None,
        logger_name: Optional[str] = None,
        hours: int = 1,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get system logs with filtering.

        Args:
            level: Optional log level filter (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            logger_name: Optional logger name filter
            hours: Number of hours to look back
            limit: Maximum number of log entries to return

        Returns:
            List of log entries
        """
        try:
            from .monitoring import LogLevel

            level_enum = None
            if level:
                try:
                    level_enum = LogLevel(level.upper())
                except ValueError:
                    self.logger.warning("Invalid log level", level=level)

            since = datetime.now(UTC) - timedelta(hours=hours)
            entries = self.monitor.get_logs(
                level=level_enum,
                logger_name=logger_name,
                since=since,
                limit=limit,
            )

            return [entry.to_dict() for entry in entries]
        except Exception as e:
            self.logger.error("Failed to get system logs", error=e)
            return []

    def cleanup_monitoring_data(self, days_to_keep: int = 7) -> Dict[str, Any]:
        """
        Clean up old monitoring data.

        Args:
            days_to_keep: Number of days of data to keep

        Returns:
            Cleanup statistics

        Raises:
            Exception: If cleanup cannot be performed
        """
        stats = self.monitor.cleanup_old_data(days_to_keep)
        self.logger.info(
            "Cleaned up monitoring data", days_to_keep=days_to_keep, **stats
        )
        return stats

    def rebuild_search_index(self) -> Dict[str, Any]:
        """
        Rebuild the search index from scratch.

        Returns:
            Dictionary with rebuild results

        Raises:
            Exception: If search index cannot be rebuilt
        """
        with self.monitor.timer("rebuild_search_index"):
            self.search_engine.rebuild_search_index()

        stats = self.search_engine.get_search_stats()

        result = {
            "success": True,
            "indexed_tasks": stats.get("indexed_tasks", 0),
            "indexed_projects": stats.get("indexed_projects", 0),
            "index_size_mb": stats.get("index_size_mb", 0),
        }

        self.logger.info("Search index rebuilt successfully", **result)
        return result

    def analyze_project_dependencies(
        self,
        project_id: str,
        analysis_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Perform advanced dependency analysis on a project.

        Args:
            project_id: Project ID or name
            analysis_types: Types of analysis to perform (all if None)

        Returns:
            Dictionary with comprehensive dependency analysis

        Raises:
            Exception: If dependency analysis cannot be performed
        """
        from .dependency_analysis import AnalysisType

        with self.monitor.timer("analyze_project_dependencies", project_id=project_id):
            project = self.get_project(project_id)
            tasks = self.storage.list_project_tasks(project.id)

            # Convert string analysis types to enum
            if analysis_types:
                try:
                    enum_types = [AnalysisType(t.upper()) for t in analysis_types]
                except ValueError as e:
                    raise ValidationError(f"Invalid analysis type: {e}")
            else:
                enum_types = None

            # Perform analysis
            analysis = self.dependency_analyzer.analyze_dependencies(tasks, enum_types)

            # Add project context
            analysis["project_info"] = {
                "project_id": project.id,
                "friendly_name": project.friendly_name,
                "total_tasks": len(tasks),
                "analysis_timestamp": datetime.now(UTC).isoformat(),
            }

            self.logger.info(
                "Completed dependency analysis",
                project_id=project.id,
                total_tasks=len(tasks),
                analysis_types=analysis_types or "all",
            )

            return analysis

    def analyze_task_impact(self, project_id: str, task_id: str) -> Dict[str, Any]:
        """
        Analyze the impact of delays or changes to a specific task.

        Args:
            project_id: Project ID or name
            task_id: Task ID to analyze

        Returns:
            Dictionary with impact analysis results

        Raises:
            Exception: If task impact analysis cannot be performed
        """
        with self.monitor.timer(
            "analyze_task_impact", project_id=project_id, task_id=task_id
        ):
            project = self.get_project(project_id)
            tasks = self.storage.list_project_tasks(project.id)

            # Perform impact analysis
            impact = self.dependency_analyzer.analyze_task_impact(task_id, tasks)

            # Add context
            result = impact.to_dict()
            result["project_info"] = {
                "project_id": project.id,
                "friendly_name": project.friendly_name,
                "analysis_timestamp": datetime.now(UTC).isoformat(),
            }

            self.logger.info(
                "Completed task impact analysis",
                project_id=project.id,
                task_id=task_id,
                total_impact_score=impact.total_impact_score,
                affected_tasks=len(impact.directly_affected)
                + len(impact.indirectly_affected),
            )

            return result

    def generate_dependency_visualization(
        self,
        project_id: str,
        format_type: str = "dot",
        highlight_critical_path: bool = True,
        highlight_bottlenecks: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate visualization of project dependency graph.

        Args:
            project_id: Project ID or name
            format_type: Visualization format (dot, mermaid, json_graph, adjacency_list)
            highlight_critical_path: Whether to highlight critical path
            highlight_bottlenecks: Whether to highlight bottlenecks

        Returns:
            Dictionary with visualization data

        Raises:
            Exception: If dependency visualization cannot be generated
        """
        from .dependency_analysis import VisualizationFormat

        with self.monitor.timer(
            "generate_dependency_visualization",
            project_id=project_id,
            format_type=format_type,
        ):
            project = self.get_project(project_id)
            tasks = self.storage.list_project_tasks(project.id)

            # Convert format type
            try:
                format_enum = VisualizationFormat(format_type.lower())
            except ValueError:
                # List available formats for better error message
                available_formats = [e.value for e in VisualizationFormat]
                raise ValidationError(
                    f"Invalid visualization format: {format_type}. "
                    f"Available formats: {', '.join(available_formats)}"
                )

            # Generate visualization
            visualization = self.dependency_analyzer.generate_visualization(
                tasks, format_enum, highlight_critical_path, highlight_bottlenecks
            )

            result = {
                "project_info": {
                    "project_id": project.id,
                    "friendly_name": project.friendly_name,
                    "total_tasks": len(tasks),
                },
                "visualization": {
                    "format": format_type,
                    "content": visualization,
                    "highlight_critical_path": highlight_critical_path,
                    "highlight_bottlenecks": highlight_bottlenecks,
                    "generated_at": datetime.now(UTC).isoformat(),
                },
            }

            self.logger.info(
                "Generated dependency visualization",
                project_id=project.id,
                format_type=format_type,
                total_tasks=len(tasks),
            )

            return result

    def get_critical_path_analysis(self, project_id: str) -> Dict[str, Any]:
        """
        Get critical path analysis for a project.

        Args:
            project_id: Project ID or name

        Returns:
            Dictionary with critical path analysis

        Raises:
            Exception: If critical path analysis cannot be performed
        """
        analysis = self.analyze_project_dependencies(
            project_id, analysis_types=["critical_path"]
        )

        # Extract just the critical path information
        critical_path_data = analysis.get("critical_path", {})

        return {
            "project_id": project_id,
            "critical_path": critical_path_data,
            "summary": {
                "path_length": len(critical_path_data.get("path", [])),
                "total_duration_hours": critical_path_data.get(
                    "total_duration_hours", 0
                ),
                "bottleneck_count": len(critical_path_data.get("bottleneck_tasks", [])),
                "completion_probability": critical_path_data.get(
                    "completion_probability", 0
                ),
                "risk_factor_count": len(critical_path_data.get("risk_factors", [])),
            },
        }

    def get_workload_analysis(self, project_id: str) -> Dict[str, Any]:
        """
        Get workload distribution analysis for a project.

        Args:
            project_id: Project ID or name

        Returns:
            Dictionary with workload analysis

        Raises:
            Exception: If workload analysis cannot be performed
        """
        analysis = self.analyze_project_dependencies(
            project_id, analysis_types=["workload_distribution"]
        )

        # Extract workload analysis
        workload_data = analysis.get("workload_analysis", {})

        return {
            "project_id": project_id,
            "workload_analysis": workload_data,
            "summary": {
                "total_assignees": len(workload_data.get("assignee_workloads", {})),
                "balance_score": workload_data.get("workload_balance_score", 0),
                "bottleneck_assignees": len(
                    workload_data.get("bottleneck_assignees", [])
                ),
                "total_workload_hours": sum(
                    workload_data.get("assignee_workloads", {}).values()
                ),
                "recommendation_count": len(workload_data.get("recommendations", [])),
            },
        }

    def get_bottleneck_analysis(self, project_id: str) -> Dict[str, Any]:
        """
        Get bottleneck analysis for a project.

        Args:
            project_id: Project ID or name

        Returns:
            Dictionary with bottleneck analysis

        Raises:
            Exception: If bottleneck analysis cannot be performed
        """
        analysis = self.analyze_project_dependencies(
            project_id, analysis_types=["bottleneck"]
        )

        # Extract bottleneck analysis
        bottleneck_data = analysis.get("bottlenecks", [])

        return {
            "project_id": project_id,
            "bottlenecks": bottleneck_data,
            "summary": {
                "total_bottlenecks": len(bottleneck_data),
                "high_impact_bottlenecks": len(
                    [b for b in bottleneck_data if b.get("bottleneck_score", 0) > 5]
                ),
                "unassigned_bottlenecks": len(
                    [b for b in bottleneck_data if not b.get("assigned_to")]
                ),
                "blocked_bottlenecks": len(
                    [b for b in bottleneck_data if b.get("status") == "blocked"]
                ),
            },
        }

    def get_project_stats(
        self,
        project_id: str,
        include_complexity_breakdown: bool = True,
        include_tag_summary: bool = True,
        include_assignee_summary: bool = True,
    ) -> Dict[str, Any]:
        """Get comprehensive project statistics."""
        project = self.get_project(project_id)
        tasks = self.storage.list_project_tasks(project.id)

        # Basic stats
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == TaskStatus.DONE])
        in_progress_tasks = len(
            [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
        )
        blocked_tasks = len([t for t in tasks if t.status == TaskStatus.BLOCKED])
        todo_tasks = len([t for t in tasks if t.status == TaskStatus.TODO])

        stats = {
            "project": project.to_dict(),
            "task_counts": {
                "total": total_tasks,
                "completed": completed_tasks,
                "in_progress": in_progress_tasks,
                "blocked": blocked_tasks,
                "todo": todo_tasks,
                "completion_percentage": (
                    (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                ),
            },
        }

        # Complexity breakdown
        if include_complexity_breakdown:
            complexity_counts = {"low": 0, "medium": 0, "high": 0}
            for task in tasks:
                complexity_counts[task.complexity.value] += 1

            stats["complexity_breakdown"] = complexity_counts

        # Tag summary
        if include_tag_summary:
            tag_counts: Dict[str, int] = {}
            for task in tasks:
                for tag in task.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

            stats["tag_summary"] = dict(
                sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            )

        # Assignee summary
        if include_assignee_summary:
            assignee_counts: Dict[str, int] = {}
            for task in tasks:
                assignee = task.assigned_to or "unassigned"
                assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1

            stats["assignee_summary"] = dict(
                sorted(assignee_counts.items(), key=lambda x: x[1], reverse=True)
            )

        return stats

    # Advanced Task Operations

    def update_task_status(
        self,
        task_id: str,
        new_status: TaskStatus,
        note: Optional[str] = None,
    ) -> Task:
        """
        Update task status with workflow validation and dependency resolution.

        Args:
            task_id: Task ID
            new_status: New task status
            note: Optional note about the status change

        Returns:
            Updated Task object

        Raises:
            TaskNotFoundError: If task not found
            StatusTransitionError: If status transition is invalid
            ValidationError: If validation fails
            StorageError: If update fails
        """
        task = self.storage.get_task(task_id)

        # Find project for this task
        project_id = self.storage.find_project_id_by_task_id(task_id)
        if not project_id:
            raise ValidationError(f"Could not find project for task {task_id}")

        project = self.get_project(project_id)

        # Validate status transition
        try:
            StatusWorkflow.validate_transition(task.status, new_status, task)
        except StatusTransitionError as e:
            logger.error(f"Invalid status transition for task {task_id}: {e}")
            raise ValidationError(str(e))

        # Check dependency constraints for certain transitions
        if new_status == TaskStatus.DONE and task.dependencies:
            dependency_statuses = self._get_dependency_statuses(
                project.id, task.dependencies
            )
            incomplete_deps = [
                dep_id
                for dep_id, status in dependency_statuses.items()
                if status != TaskStatus.DONE
            ]
            if incomplete_deps:
                raise ValidationError(
                    f"Cannot mark task as done: dependencies {incomplete_deps} "
                    f"are not complete"
                )

        # Auto-block if trying to start work on task with incomplete dependencies
        if new_status == TaskStatus.IN_PROGRESS and task.dependencies:
            dependency_statuses = self._get_dependency_statuses(
                project.id, task.dependencies
            )
            if StatusWorkflow.should_auto_block(task, dependency_statuses):
                new_status = TaskStatus.BLOCKED
                note = "Auto-blocked due to incomplete dependencies"

        # Update status with history tracking
        old_status = task.status
        logger.info(
            f"DEBUG_STATUS: Updating task {task_id} status from "
            f"{old_status.value} to {new_status.value}"
        )
        task.update_status(new_status, note)
        logger.info(
            f"DEBUG_STATUS: Task {task_id} status updated successfully "
            f"to {task.status.value}"
        )

        # Add note if provided
        if note:
            task.add_note(
                f"Status changed to {new_status.value}: {note}",
                note_type=NoteType.STATUS_CHANGE,
                author="system",
            )

        try:
            # Save the updated task
            logger.info(
                f"DEBUG_STATUS: Saving task {task_id} to storage "
                f"with status {task.status.value}"
            )
            self.storage.update_task(task)
            logger.info(f"DEBUG_STATUS: Task {task_id} saved successfully to storage")

            # Send status change notification
            dependent_task_ids = self._get_dependent_task_ids(project.id, task_id)
            logger.info(
                f"DEBUG_STATUS: Found {len(dependent_task_ids)} dependent tasks "
                f"for {task_id}: {dependent_task_ids}"
            )
            self.notifications.notify_status_change(
                task=task,
                project_id=project.id,
                old_status=old_status,
                new_status=new_status,
                note=note,
                dependent_tasks=dependent_task_ids,
            )

            # Trigger dependency resolution for affected tasks
            logger.info(
                f"DEBUG_STATUS: Triggering dependency resolution for task {task_id} "
                f"status change to {new_status.value}"
            )
            self._resolve_dependent_task_statuses(project.id, task_id, new_status)

            logger.info(
                f"Updated task status: {task.title} "
                f"({old_status.value} -> {new_status.value})"
            )
            return task

        except StorageError as e:
            logger.error(f"Failed to update task status {task_id}: {e}")
            raise

    def _get_dependency_statuses(
        self, project_id: str, dependency_ids: Set[str]
    ) -> Dict[str, TaskStatus]:
        """
        Get status of all dependency tasks.

        Args:
            project_id: Project ID
            dependency_ids: Set of dependency task IDs

        Returns:
            Map of dependency ID to status
        """
        statuses = {}
        for dep_id in dependency_ids:
            try:
                dep_task = self.storage.get_task(dep_id)
                statuses[dep_id] = dep_task.status
            except TaskNotFoundError:
                logger.warning(f"Dependency task {dep_id} not found")
                # Treat missing dependencies as incomplete
                statuses[dep_id] = TaskStatus.TODO
        return statuses

    def _get_dependent_task_ids(self, project_id: str, task_id: str) -> List[str]:
        """
        Get IDs of tasks that depend on the given task.

        Args:
            project_id: Project ID
            task_id: Task ID to find dependents for

        Returns:
            List of dependent task IDs
        """
        try:
            tasks = self.storage.list_project_tasks(project_id)
            return [task.id for task in tasks if task_id in task.dependencies]
        except Exception as e:
            logger.error(f"Error getting dependent task IDs: {e}")
            return []

    def _resolve_dependent_task_statuses(
        self, project_id: str, changed_task_id: str, new_status: TaskStatus
    ) -> None:
        """
        Resolve status of tasks that depend on the changed task.

        Args:
            project_id: Project ID
            changed_task_id: ID of task that changed status
            new_status: New status of the changed task
        """
        logger.info(
            f"DEBUG_DEPS: Starting dependency resolution for task {changed_task_id} "
            f"(new status: {new_status.value})"
        )
        try:
            # Get all tasks in the project
            tasks = self.storage.list_project_tasks(project_id)
            logger.info(f"DEBUG_DEPS: Found {len(tasks)} total tasks in project")

            # Find tasks that depend on the changed task
            dependent_tasks = [
                task for task in tasks if changed_task_id in task.dependencies
            ]
            logger.info(
                f"DEBUG_DEPS: Found {len(dependent_tasks)} tasks that depend "
                f"on {changed_task_id}"
            )

            for dependent_task in dependent_tasks:
                logger.info(
                    f"DEBUG_DEPS: Processing dependent task {dependent_task.id} "
                    f"(current status: {dependent_task.status.value})"
                )
                logger.info(
                    f"DEBUG_DEPS: Task {dependent_task.id} dependencies: "
                    f"{dependent_task.dependencies}"
                )

                # Get current dependency statuses
                dependency_statuses = self._get_dependency_statuses(
                    project_id, dependent_task.dependencies
                )
                logger.info(
                    f"DEBUG_DEPS: Dependency statuses for task {dependent_task.id}: "
                    f"{dependency_statuses}"
                )

                # Check if task should be auto-blocked or unblocked
                should_block = StatusWorkflow.should_auto_block(
                    dependent_task, dependency_statuses
                )
                should_unblock = StatusWorkflow.should_auto_unblock(
                    dependent_task, dependency_statuses
                )
                logger.info(
                    f"DEBUG_DEPS: Task {dependent_task.id} - should_block: "
                    f"{should_block}, should_unblock: {should_unblock}"
                )

                updated = False

                if should_block and dependent_task.status != TaskStatus.BLOCKED:
                    # Auto-block the task
                    old_status = dependent_task.status
                    logger.info(
                        f"DEBUG_DEPS: Auto-blocking task {dependent_task.id} "
                        f"from {old_status.value} to blocked"
                    )
                    dependent_task.update_status(
                        TaskStatus.BLOCKED,
                        f"Auto-blocked due to incomplete dependency: "
                        f"{changed_task_id}",
                    )
                    dependent_task.add_note(
                        f"Auto-blocked: dependency {changed_task_id} "
                        f"changed to {new_status.value}",
                        note_type=NoteType.DEPENDENCY,
                        author="system",
                    )
                    updated = True
                    logger.info(
                        f"Auto-blocked task {dependent_task.id}: "
                        f"{dependent_task.title} ({old_status.value} -> blocked)"
                    )

                elif should_unblock and dependent_task.status == TaskStatus.BLOCKED:
                    # Auto-unblock the task (return to TODO)
                    logger.info(
                        f"DEBUG_DEPS: Auto-unblocking task {dependent_task.id} "
                        f"from blocked to todo"
                    )
                    dependent_task.update_status(
                        TaskStatus.TODO, "Auto-unblocked: all dependencies complete"
                    )
                    dependent_task.add_note(
                        f"Auto-unblocked: dependency {changed_task_id} completed",
                        note_type=NoteType.DEPENDENCY,
                        author="system",
                    )
                    updated = True
                    logger.info(
                        f"Auto-unblocked task {dependent_task.id}: "
                        f"{dependent_task.title} (blocked -> todo)"
                    )
                else:
                    logger.info(
                        f"DEBUG_DEPS: No status change needed for task "
                        f"{dependent_task.id}"
                    )

                if updated:
                    self.storage.update_task(dependent_task)

        except Exception as e:
            logger.error(f"Error resolving dependent task statuses: {e}")
            # Don't raise - this is a background operation

    def auto_manage_blocked_status(self, project_id: str) -> List[str]:
        """
        Automatically manage blocked status for all tasks in a project.

        This method scans all tasks and updates their blocked status based
        on their dependencies. Useful for batch operations or maintenance.

        Args:
            project_id: Project ID

        Returns:
            List of task IDs that were updated

        Raises:
            ProjectNotFoundError: If project not found
            StorageError: If operation fails
        """
        project = self.get_project(project_id)
        updated_tasks = []

        try:
            tasks = self.storage.list_project_tasks(project.id)

            for task in tasks:
                if not task.dependencies:
                    # No dependencies, should not be blocked
                    if task.status == TaskStatus.BLOCKED:
                        task.update_status(
                            TaskStatus.TODO, "Auto-unblocked: no dependencies"
                        )
                        self.storage.update_task(task)
                        updated_tasks.append(task.id)
                        logger.info(f"Auto-unblocked task {task.id}: no dependencies")
                    continue

                # Get dependency statuses
                dependency_statuses = self._get_dependency_statuses(
                    project.id, task.dependencies
                )

                should_block = StatusWorkflow.should_auto_block(
                    task, dependency_statuses
                )
                should_unblock = StatusWorkflow.should_auto_unblock(
                    task, dependency_statuses
                )

                if should_block and task.status != TaskStatus.BLOCKED:
                    old_status = task.status
                    task.update_status(
                        TaskStatus.BLOCKED,
                        "Auto-blocked due to incomplete dependencies",
                    )
                    self.storage.update_task(task)
                    updated_tasks.append(task.id)
                    logger.info(
                        f"Auto-blocked task {task.id}: "
                        f"{task.title} ({old_status.value} -> blocked)"
                    )

                elif should_unblock and task.status == TaskStatus.BLOCKED:
                    task.update_status(
                        TaskStatus.TODO, "Auto-unblocked: all dependencies complete"
                    )
                    self.storage.update_task(task)
                    updated_tasks.append(task.id)
                    logger.info(
                        f"Auto-unblocked task {task.id}: "
                        f"{task.title} (blocked -> todo)"
                    )

            return updated_tasks

        except Exception as e:
            logger.error(f"Error in auto_manage_blocked_status: {e}")
            raise StorageError(f"Failed to manage blocked status: {e}")

    def bulk_update_task_status(
        self,
        task_ids: List[str],
        new_status: str,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update status for multiple tasks.

        Args:
            task_ids: List of task IDs
            new_status: New status for all tasks
            note: Optional note for all status changes

        Returns:
            Dictionary with updated and failed task lists
        """
        from .models import TaskStatus

        results: Dict[str, List[Dict[str, Any]]] = {"updated": [], "failed": []}

        for task_id in task_ids:
            try:
                # update_task_status validates task exists
                updated_task = self.update_task_status(
                    task_id, TaskStatus(new_status), note
                )
                results["updated"].append(updated_task.to_dict())
            except Exception as e:
                results["failed"].append({"task_id": task_id, "error": str(e)})
                logger.warning(f"Failed to update task {task_id}: {e}")

        logger.info(
            f"Bulk status update: {len(results['updated'])} updated, "
            f"{len(results['failed'])} failed"
        )
        return results

    def complete_task_steps(
        self,
        project_id: str,
        task_id: str,
        step_indices: List[int],
        note: Optional[str] = None,
        auto_complete: bool = False,
    ) -> Task:
        """
        Complete multiple task steps.

        Args:
            project_id: Project ID or name
            task_id: Task ID
            step_indices: List of step indices to complete
            note: Optional note about step completion
            auto_complete: Auto-complete task if all steps done

        Returns:
            Updated Task object
        """
        task = self.storage.get_task(task_id)

        # Ensure step_indices are integers (handle string inputs from MCP)
        converted_indices = []
        for idx in step_indices:
            try:
                converted_indices.append(int(idx))
            except (ValueError, TypeError):
                logger.warning(f"Invalid step index: {idx}, skipping")
                continue

        # Complete steps
        for step_index in converted_indices:
            task.complete_step(step_index)

        # Add note if provided
        if note:
            task.add_note(
                f"Completed steps {converted_indices}: {note}",
                note_type=NoteType.PROGRESS,
                author="system",
            )

        # Auto-complete task if all steps are done
        if auto_complete and len(task.completed_steps) == len(task.steps):
            task.update_status(TaskStatus.DONE)
            task.add_note(
                "Task auto-completed - all steps finished",
                note_type=NoteType.PROGRESS,
                author="system",
            )

        try:
            self.storage.update_task(task)
            logger.info(f"Completed steps {step_indices} for task: {task.title}")
            return task

        except StorageError as e:
            logger.error(f"Failed to complete task steps {task_id}: {e}")
            raise

    def uncomplete_task_steps(
        self,
        project_id: str,
        task_id: str,
        step_indices: List[int],
        note: Optional[str] = None,
    ) -> Task:
        """
        Mark task steps as incomplete.

        Args:
            project_id: Project ID or name
            task_id: Task ID
            step_indices: List of step indices to uncomplete
            note: Optional note about step incompletion

        Returns:
            Updated Task object
        """
        task = self.storage.get_task(task_id)

        # Uncomplete steps
        for step_index in step_indices:
            task.uncomplete_step(step_index)

        # Add note if provided
        if note:
            task.add_note(
                f"Uncompleted steps {step_indices}: {note}",
                note_type=NoteType.PROGRESS,
                author="system",
            )

        try:
            self.storage.update_task(task)
            logger.info(f"Uncompleted steps {step_indices} for task: {task.title}")
            return task

        except StorageError as e:
            logger.error(f"Failed to uncomplete task steps {task_id}: {e}")
            raise

    def get_task_progress_summary(
        self, project_id: str, task_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed progress summary for a task.

        Args:
            project_id: Project ID or name
            task_id: Task ID

        Returns:
            Dictionary with progress information
        """
        task = self.storage.get_task(task_id)

        completed_count = len(task.completed_steps)
        total_count = len(task.steps)
        remaining_count = total_count - completed_count

        return {
            "task_id": task.id,
            "task_title": task.title,
            "status": task.status.value,
            "completed_steps": completed_count,
            "total_steps": total_count,
            "remaining_steps": remaining_count,
            "completion_percentage": task.progress_percentage(),
            "completed_step_indices": sorted(task.completed_steps),
            "remaining_step_indices": [
                i for i in range(total_count) if i not in task.completed_steps
            ],
        }

    def assign_task(
        self,
        project_id: str,
        task_id: str,
        assignee: str,
        note: Optional[str] = None,
    ) -> Task:
        """
        Assign a task to someone.

        Args:
            project_id: Project ID or name
            task_id: Task ID
            assignee: Person to assign task to
            note: Optional note about assignment

        Returns:
            Updated Task object
        """
        task = self.storage.get_task(task_id)

        # Update assignment
        task.assigned_to = assignee
        task.updated = datetime.now(UTC)

        # Add note if provided
        if note:
            task.add_note(
                f"Assigned to {assignee}: {note}",
                note_type=NoteType.ASSIGNMENT,
                author="system",
            )
        else:
            task.add_note(
                f"Assigned to {assignee}",
                note_type=NoteType.ASSIGNMENT,
                author="system",
            )

        try:
            self.storage.update_task(task)
            logger.info(f"Assigned task {task.title} to {assignee}")
            return task

        except StorageError as e:
            logger.error(f"Failed to assign task {task_id}: {e}")
            raise

    def reassign_task(
        self,
        project_id: str,
        task_id: str,
        new_assignee: str,
        note: Optional[str] = None,
    ) -> Task:
        """
        Reassign a task to someone else.

        Args:
            project_id: Project ID or name
            task_id: Task ID
            new_assignee: New person to assign task to
            note: Optional note about reassignment

        Returns:
            Updated Task object
        """
        task = self.storage.get_task(task_id)

        old_assignee = task.assigned_to or "unassigned"

        # Update assignment
        task.assigned_to = new_assignee
        task.updated = datetime.now(UTC)

        # Add note
        if note:
            task.add_note(
                f"Reassigned from {old_assignee} to {new_assignee}: {note}",
                note_type=NoteType.ASSIGNMENT,
                author="system",
            )
        else:
            task.add_note(
                f"Reassigned from {old_assignee} to {new_assignee}",
                note_type=NoteType.ASSIGNMENT,
                author="system",
            )

        try:
            self.storage.update_task(task)
            logger.info(f"Reassigned task {task.title} to {new_assignee}")
            return task

        except StorageError as e:
            logger.error(f"Failed to reassign task {task_id}: {e}")
            raise

    def unassign_task(
        self, project_id: str, task_id: str, note: Optional[str] = None
    ) -> Task:
        """
        Unassign a task.

        Args:
            project_id: Project ID or name
            task_id: Task ID
            note: Optional note about unassignment

        Returns:
            Updated Task object
        """
        task = self.storage.get_task(task_id)

        old_assignee = task.assigned_to or "unassigned"

        # Remove assignment
        task.assigned_to = None
        task.updated = datetime.now(UTC)

        # Add note
        if note:
            task.add_note(
                f"Unassigned from {old_assignee}: {note}",
                note_type=NoteType.ASSIGNMENT,
                author="system",
            )
        else:
            task.add_note(
                f"Unassigned from {old_assignee}",
                note_type=NoteType.ASSIGNMENT,
                author="system",
            )

        try:
            self.storage.update_task(task)
            logger.info(f"Unassigned task {task.title}")
            return task

        except StorageError as e:
            logger.error(f"Failed to unassign task {task_id}: {e}")
            raise

    def bulk_assign_tasks(
        self,
        task_ids: List[str],
        assignee: str,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Assign multiple tasks to someone.

        Args:
            task_ids: List of task IDs
            assignee: Person to assign tasks to
            note: Optional note for all assignments

        Returns:
            Dictionary with assigned and failed task lists
        """
        results: Dict[str, List[Dict[str, Any]]] = {"assigned": [], "failed": []}

        for task_id in task_ids:
            try:
                # Get task directly since task IDs are globally unique
                task = self.storage.get_task(task_id)

                # Update assignment
                task.assigned_to = assignee
                task.updated = datetime.now(UTC)

                # Add note if provided
                if note:
                    task.add_note(
                        f"Assigned to {assignee}: {note}",
                        note_type=NoteType.ASSIGNMENT,
                        author="system",
                    )
                else:
                    task.add_note(
                        f"Assigned to {assignee}",
                        note_type=NoteType.ASSIGNMENT,
                        author="system",
                    )

                self.storage.update_task(task)
                results["assigned"].append(task.to_dict())
                logger.info(f"Assigned task {task.title} to {assignee}")

            except Exception as e:
                results["failed"].append({"task_id": task_id, "error": str(e)})
                logger.warning(f"Failed to assign task {task_id}: {e}")

        logger.info(
            f"Bulk assignment: {len(results['assigned'])} assigned, "
            f"{len(results['failed'])} failed"
        )
        return results

    def add_task_dependencies(
        self,
        project_id: str,
        task_id: str,
        dependency_ids: List[str],
        validate: bool = True,
    ) -> Task:
        """
        Add multiple dependencies to a task.

        Args:
            project_id: Project ID or name
            task_id: Task ID
            dependency_ids: List of dependency task IDs
            validate: Whether to validate dependencies

        Returns:
            Updated Task object
        """
        project = self.get_project(project_id)
        task = self.storage.get_task(task_id)

        # Validate dependencies if requested
        if validate:
            all_tasks = self.storage.list_project_tasks(project.id)
            for dep_id in dependency_ids:
                can_add, error_msg = dependency_validator.can_add_dependency(
                    task_id, dep_id, all_tasks
                )
                if not can_add:
                    raise DependencyError(
                        f"Cannot add dependency {dep_id}: {error_msg}"
                    )

        # Add dependencies
        for dep_id in dependency_ids:
            task.add_dependency(dep_id)

        try:
            self.storage.update_task(task)
            logger.info(
                f"Added {len(dependency_ids)} dependencies to task {task.title}"
            )
            return task

        except StorageError as e:
            logger.error(f"Failed to add dependencies to task {task_id}: {e}")
            raise

    def remove_task_dependencies(
        self, project_id: str, task_id: str, dependency_ids: List[str]
    ) -> Task:
        """
        Remove multiple dependencies from a task.

        Args:
            project_id: Project ID or name
            task_id: Task ID
            dependency_ids: List of dependency task IDs to remove

        Returns:
            Updated Task object
        """
        task = self.storage.get_task(task_id)
        logger.debug(f"Before removal: task dependencies = {task.dependencies}")

        # Remove dependencies
        for dep_id in dependency_ids:
            logger.debug(f"Removing dependency {dep_id}")
            task.remove_dependency(dep_id)
            logger.debug(
                f"After removing {dep_id}: task dependencies = {task.dependencies}"
            )

        try:
            logger.debug(f"Updating task with dependencies: {task.dependencies}")
            self.storage.update_task(task)

            # Verify the update worked by reloading the task
            updated_task = self.storage.get_task(task_id)
            logger.debug(
                f"After storage update: reloaded task dependencies = "
                f"{updated_task.dependencies}"
            )

            # Validate that dependencies were actually removed
            for dep_id in dependency_ids:
                if dep_id in updated_task.dependencies:
                    raise StorageError(
                        f"Dependency {dep_id} was not removed from storage"
                    )

            logger.info(
                f"Removed {len(dependency_ids)} dependencies from task {task.title}"
            )

            return updated_task

        except StorageError as e:
            logger.error(f"Failed to remove dependencies from task {task_id}: {e}")
            raise

    def replace_task_dependencies(
        self,
        project_id: str,
        task_id: str,
        new_dependency_ids: List[str],
        validate: bool = True,
    ) -> Task:
        """
        Replace all task dependencies with new ones.

        Args:
            project_id: Project ID or name
            task_id: Task ID
            new_dependency_ids: New list of dependency task IDs
            validate: Whether to validate new dependencies

        Returns:
            Updated Task object
        """
        project = self.get_project(project_id)
        task = self.storage.get_task(task_id)

        # Validate new dependencies if requested
        if validate:
            all_tasks = self.storage.list_project_tasks(project.id)
            for dep_id in new_dependency_ids:
                can_add, error_msg = dependency_validator.can_add_dependency(
                    task_id, dep_id, all_tasks
                )
                if not can_add:
                    raise DependencyError(
                        f"Cannot add dependency {dep_id}: {error_msg}"
                    )

        # Replace dependencies
        task.dependencies = set(new_dependency_ids)
        task.updated = datetime.now(UTC)

        try:
            self.storage.update_task(task)
            logger.info(f"Replaced dependencies for task {task.title}")
            return task

        except StorageError as e:
            logger.error(f"Failed to replace dependencies for task {task_id}: {e}")
            raise

    def clone_task(
        self,
        project_id: str,
        task_id: str,
        new_title: Optional[str] = None,
        copy_dependencies: bool = False,
        copy_progress: bool = False,
    ) -> Task:
        """
        Clone a task with optional modifications.

        Args:
            project_id: Project ID or name
            task_id: Task ID to clone
            new_title: Optional new title for cloned task
            copy_dependencies: Whether to copy dependencies
            copy_progress: Whether to copy progress

        Returns:
            Cloned Task object
        """
        project = self.get_project(project_id)
        original_task = self.storage.get_task(task_id)

        # Create cloned task
        cloned_task = Task.create_new(
            title=new_title or f"Copy of {original_task.title}",
            objective=original_task.objective,
            steps=original_task.steps.copy(),
            success_criteria=original_task.success_criteria.copy(),
            complexity=original_task.complexity,
            context=original_task.context,
            assigned_to=original_task.assigned_to,
            tags=original_task.tags.copy(),
            dependencies=(
                original_task.dependencies.copy() if copy_dependencies else set()
            ),
        )

        # Copy progress if requested
        if copy_progress:
            cloned_task.completed_steps = original_task.completed_steps.copy()
            cloned_task.status = original_task.status

        try:
            self.storage.create_task(project.id, cloned_task)
            logger.info(f"Cloned task {original_task.title} -> {cloned_task.title}")
            return cloned_task

        except StorageError as e:
            logger.error(f"Failed to clone task {task_id}: {e}")
            raise

    def archive_task(self, task_id: str, reason: Optional[str] = None) -> Task:
        """
        Archive a task.

        Args:
            task_id: Task ID
            reason: Optional reason for archiving

        Returns:
            Archived Task object
        """
        task = self.storage.get_task(task_id)

        # Add archived tag
        if "archived" not in task.tags:
            task.tags.append("archived")

        # Add note
        if reason:
            task.add_note(
                f"Task archived: {reason}", note_type=NoteType.ARCHIVE, author="system"
            )
        else:
            task.add_note("Task archived", note_type=NoteType.ARCHIVE, author="system")

        task.updated = datetime.now(UTC)

        try:
            self.storage.update_task(task)
            logger.info(f"Archived task: {task.title}")
            return task

        except StorageError as e:
            logger.error(f"Failed to archive task {task_id}: {e}")
            raise

    def restore_task(
        self, project_id: str, task_id: str, note: Optional[str] = None
    ) -> Task:
        """
        Restore an archived task.

        Args:
            project_id: Project ID or name
            task_id: Task ID
            note: Optional note about restoration

        Returns:
            Restored Task object
        """
        task = self.storage.get_task(task_id)

        # Remove archived tag

        # Add note
        if note:
            task.add_note(
                f"Task restored: {note}", note_type=NoteType.ARCHIVE, author="system"
            )
        else:
            task.add_note("Task restored", note_type=NoteType.ARCHIVE, author="system")

        task.updated = datetime.now(UTC)

        try:
            self.storage.update_task(task)
            logger.info(f"Restored task: {task.title}")
            return task

        except StorageError as e:
            logger.error(f"Failed to restore task {task_id}: {e}")
            raise

    def add_task_note(
        self,
        task_id: str,
        content: str,
        note_type: NoteType = NoteType.USER,
        author: Optional[str] = None,
        tags: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add a rich note to a task.

        Args:
            task_id: Task ID
            content: Note content (supports markdown)
            note_type: Type of note (user, system, etc.)
            author: Note author
            tags: Optional tags for the note
            metadata: Optional metadata for the note

        Returns:
            Dictionary with note details and task summary
        """
        task = self.storage.get_task(task_id)

        # Add the note
        note = task.add_note(
            content=content,
            note_type=note_type,
            author=author,
            tags=tags,
            metadata=metadata,
        )

        try:
            self.storage.update_task(task)
            logger.info(f"Added note to task {task.title}: {content[:50]}...")

            # Send notification
            # Get project for notification (derive from task)
            index = self.storage._get_project_index()
            project_id = index.get_task_project(task_id)
            if project_id:
                project = self.get_project(project_id)
                self.notifications.send_task_note_added(
                    project=project,
                    task=task,
                    note=note,
                )

            return {
                "note": note.to_dict(),
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status.value,
                    "note_count": task.note_manager.get_note_count(),
                },
            }

        except StorageError as e:
            logger.error(f"Failed to add note to task {task_id}: {e}")
            raise

    def find_notes(
        self,
        query: str,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
        note_type: Optional[NoteType] = None,
        author: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search notes with flexible scoping.

        Args:
            query: Search query
            project_id: Optional project ID (if None, searches all projects)
            task_id: Optional task ID (if provided, searches only that task)
            note_type: Optional note type filter
            author: Optional author filter
            limit: Optional result limit

        Returns:
            List of matching note dictionaries with context
        """
        import logging

        logger = logging.getLogger(__name__)
        logger.debug(
            f"FIND_NOTES_CALLED: query='{query}', "
            f"project_id={project_id}, task_id={task_id}"
        )

        all_matching_notes = []

        if task_id:
            # Task-scoped search (most specific)
            task = self.storage.get_task(task_id)
            matching_notes = task.note_manager.search_notes(
                query=query,
                note_type=note_type,
                author=author,
            )

            for note in matching_notes:
                note_dict = note.to_dict()
                note_dict["project_id"] = task.project_id
                note_dict["task_id"] = task.id
                note_dict["task_title"] = task.title
                all_matching_notes.append(note_dict)

        elif project_id:
            # Project-scoped search
            project_tasks = self.list_tasks(project_id)
            for task in project_tasks:
                matching_notes = task.note_manager.search_notes(
                    query=query,
                    note_type=note_type,
                    author=author,
                )

                for note in matching_notes:
                    note_dict = note.to_dict()
                    note_dict["project_id"] = project_id
                    note_dict["task_id"] = task.id
                    note_dict["task_title"] = task.title
                    all_matching_notes.append(note_dict)
        else:
            # Global search across all projects - get all tasks
            all_tasks = self.list_tasks()  # This now supports no project_id
            for task in all_tasks:
                matching_notes = task.note_manager.search_notes(
                    query=query,
                    note_type=note_type,
                    author=author,
                )

                for note in matching_notes:
                    note_dict = note.to_dict()
                    note_dict["project_id"] = task.project_id
                    note_dict["task_id"] = task.id
                    note_dict["task_title"] = task.title
                    all_matching_notes.append(note_dict)

        # Sort by creation time (newest first)
        all_matching_notes.sort(key=lambda n: n["created"], reverse=True)

        # Apply limit
        if limit:
            all_matching_notes = all_matching_notes[:limit]

        return all_matching_notes

    def get_task_notes(
        self,
        task_id: str,
        note_type: Optional[NoteType] = None,
        author: Optional[str] = None,
        tag: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get task notes with optional filtering.

        Args:
            task_id: Task ID
            note_type: Optional note type filter
            author: Optional author filter
            tag: Optional tag filter
            since: Optional start date filter
            until: Optional end date filter
            limit: Optional result limit

        Returns:
            List of note dictionaries

        Raises:
            ValidationError: If task_id is invalid
        """
        # Get task directly by ID
        task = self.storage.get_task(task_id)
        if not task:
            raise ValidationError(f"Task {task_id} not found")

        filtered_notes = task.note_manager.get_notes(
            note_type=note_type,
            author=author,
            tag=tag,
            since=since,
            until=until,
            limit=limit,
        )

        return [note.to_dict() for note in filtered_notes]

    def split_task(
        self,
        project_id: str,
        task_id: str,
        subtask_specs: List[Dict[str, Any]],
        archive_original: bool = True,
    ) -> Dict[str, Any]:
        """
        Split a task into multiple subtasks.

        Args:
            project_id: Project ID or name
            task_id: Task ID to split
            subtask_specs: List of subtask specifications
            archive_original: Whether to archive the original task

        Returns:
            Dictionary with split results
        """
        project = self.get_project(project_id)
        original_task = self.storage.get_task(task_id)

        subtasks = []
        subtask_ids = []

        try:
            # Create subtasks
            for spec in subtask_specs:
                subtask = Task.create_new(
                    title=spec["title"],
                    objective=spec["objective"],
                    steps=spec["steps"],
                    success_criteria=spec["success_criteria"],
                    complexity=original_task.complexity,
                    context=spec.get("context", original_task.context),
                    assigned_to=original_task.assigned_to,
                    tags=original_task.tags.copy(),
                )

                self.storage.create_task(project.id, subtask)
                subtasks.append(subtask)
                subtask_ids.append(subtask.id)

            # Archive original if requested
            original_archived = False
            if archive_original:
                self.archive_task(task_id, f"Split into {len(subtasks)} subtasks")
                original_archived = True

            logger.info(
                f"Split task {original_task.title} into {len(subtasks)} subtasks"
            )

            return {
                "original_task_id": task_id,
                "original_archived": original_archived,
                "subtask_ids": subtask_ids,
                "subtasks": [task.to_dict() for task in subtasks],
            }

        except StorageError as e:
            logger.error(f"Failed to split task {task_id}: {e}")
            raise

    def validate_task_data(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate task data structure.

        Args:
            task_data: Task data dictionary

        Returns:
            Validation result dictionary
        """
        errors = validator.validate_task_data(task_data)

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "validated_fields": list(task_data.keys()),
        }

    def bulk_delete_tasks(self, task_ids: List[str]) -> Dict[str, Any]:
        """
        Delete multiple tasks.

        Args:
            task_ids: List of task IDs to delete

        Returns:
            Dictionary with deleted and failed task lists
        """
        logger.debug(
            f"bulk_delete_tasks: Starting bulk delete of {len(task_ids)} tasks: "
            f"{task_ids}"
        )
        results: Dict[str, List[Dict[str, Any]]] = {"deleted": [], "failed": []}

        for i, task_id in enumerate(task_ids):
            try:
                logger.debug(
                    f"bulk_delete_tasks: Processing task {i+1}/{len(task_ids)}: "
                    f"{task_id}"
                )
                task = self.storage.get_task(task_id)
                logger.debug(
                    f"bulk_delete_tasks: Found task '{task.title}' "
                    f"in project {task.project_id}"
                )

                self.delete_task(task_id)
                logger.debug(f"bulk_delete_tasks: Successfully deleted task {task_id}")

                results["deleted"].append(task.to_dict())
            except Exception as e:
                logger.debug(f"bulk_delete_tasks: Failed to delete task {task_id}: {e}")
                results["failed"].append({"task_id": task_id, "error": str(e)})
                logger.warning(f"Failed to delete task {task_id}: {e}")

        logger.debug(
            f"bulk_delete_tasks: Completed - {len(results['deleted'])} deleted, "
            f"{len(results['failed'])} failed"
        )
        logger.info(
            f"Bulk delete: {len(results['deleted'])} deleted, "
            f"{len(results['failed'])} failed"
        )
        return results

    def bulk_update_task_properties(
        self,
        project_id: str,
        task_ids: List[str],
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update properties for multiple tasks.

        Args:
            project_id: Project ID or name
            task_ids: List of task IDs
            updates: Dictionary of property updates

        Returns:
            Dictionary with updated and failed task lists
        """
        project = self.get_project(project_id)
        results: Dict[str, List[Any]] = {"updated": [], "failed": []}

        for task_id in task_ids:
            try:
                updated_task = self.update_task(project.id, task_id, **updates)
                results["updated"].append(updated_task.to_dict())
            except Exception as e:
                results["failed"].append({"task_id": task_id, "error": str(e)})
                logger.warning(f"Failed to update task {task_id}: {e}")

        logger.info(
            f"Bulk update: {len(results['updated'])} updated, "
            f"{len(results['failed'])} failed"
        )
        return results

    @require_aws_profile
    def create_strand_template(
        self,
        project_id: str,
        output_path: Optional[str] = None,
        target_task_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate Strands execution template from Lackey project.

        Args:
            project_id: Project ID to convert
            output_path: Optional output path for template
            target_task_id: Optional target task - if provided, execute only this task
                and its dependencies

        Returns:
            Dict with template_path and metadata
        """
        logger.debug(
            "Starting strand template generation: "
            f"project_id={project_id}, target_task_id={target_task_id}, "
            f"output_path={output_path}"
        )
        try:
            from .strands.core.bridge import TemplateService

            # Validate project exists
            logger.debug(f"Validating project existence: {project_id}")
            project = self.storage.get_project(project_id)
            if not project:
                logger.error(f"Project not found: {project_id}")
                raise ValidationError(f"Project {project_id} not found")

            logger.debug(
                f"Project found: {project.friendly_name} with "
                f"{len(project.tasks)} tasks"
            )

            # Filter tasks if target_task_id is provided
            if target_task_id:
                logger.debug(f"Extracting upstream tasks for target: {target_task_id}")
                tasks = self._extract_upstream_tasks(project_id, target_task_id)
                logger.debug(
                    f"Extracted {len(tasks)} upstream tasks for target {target_task_id}"
                )
            else:
                logger.debug(f"Getting executable tasks for project {project_id}")
                all_tasks = self.storage.list_project_tasks(project_id)

                # Filter tasks by status - include TODO and recursively
                # unblockable BLOCKED tasks
                executable_tasks = []
                todo_tasks = [t for t in all_tasks if t.status == TaskStatus.TODO]
                blocked_tasks = [t for t in all_tasks if t.status == TaskStatus.BLOCKED]

                # Always include TODO tasks
                executable_tasks.extend(todo_tasks)

                # For BLOCKED tasks, recursively check if they can become unblocked
                if blocked_tasks:
                    # Get IDs of already completed tasks
                    completed_task_ids = {
                        t.id for t in all_tasks if t.status == TaskStatus.DONE
                    }
                    # Start with TODO tasks as initially executable
                    executable_task_ids = {t.id for t in todo_tasks}

                    # Recursively find tasks that can become unblocked
                    changed = True
                    while changed:
                        changed = False
                        for blocked_task in blocked_tasks:
                            # Skip if already included
                            if blocked_task.id in executable_task_ids:
                                continue

                            # Skip blocked tasks with no dependencies - they can't
                            # become unblocked
                            if not blocked_task.dependencies:
                                logger.debug(
                                    f"Skipping blocked task {blocked_task.id} - "
                                    f"no dependencies to satisfy"
                                )
                                continue

                            # Check if all dependencies will be satisfied
                            dependencies_satisfied = blocked_task.dependencies.issubset(
                                completed_task_ids | executable_task_ids
                            )
                            if dependencies_satisfied:
                                executable_tasks.append(blocked_task)
                                executable_task_ids.add(blocked_task.id)
                                changed = True
                                logger.debug(
                                    f"Including blocked task {blocked_task.id} - "
                                    f"dependencies will be satisfied"
                                )

                tasks = executable_tasks
                if not tasks:
                    logger.error(f"Project {project_id} has no executable tasks")
                    raise ValidationError(
                        f"Project {project_id} has no executable tasks"
                    )
                logger.debug(f"Found {len(tasks)} tasks in project")

            # Clean up task dependencies - remove references to completed tasks
            completed_task_ids = {
                t.id
                for t in self.storage.list_project_tasks(project_id)
                if t.status == TaskStatus.DONE
            }

            logger.debug(
                f"generate_strand_template: Found completed tasks: {completed_task_ids}"
            )

            if completed_task_ids:
                logger.debug(
                    f"generate_strand_template: Cleaning dependencies for "
                    f"{len(completed_task_ids)} completed tasks"
                )
                for task in tasks:
                    original_deps = task.dependencies.copy()
                    # Remove completed task IDs from dependencies
                    task.dependencies = task.dependencies - completed_task_ids
                    logger.debug(
                        f"generate_strand_template: Task {task.id} dependencies: "
                        f"{original_deps} -> {task.dependencies}"
                    )

            # Log final task states before calling bridge
            for task in tasks:
                logger.debug(
                    f"generate_strand_template: Final task {task.id} has "
                    f"dependencies: {task.dependencies}"
                )

            # Generate template using bridge
            logger.debug(
                f"Calling TemplateService.create_execution_template with "
                f"{len(tasks)} tasks"
            )
            result = TemplateService.create_execution_template(
                project, tasks, self.lackey_dir, target_task_id
            )

            # Add template mapping to index
            if "spec_id" in result:
                index = self.storage._get_project_index()
                index.add_template_mapping(result["spec_id"], project_id)
                self.storage._save_project_index(index)
                logger.debug(
                    f"Added template mapping: {result['spec_id']} -> {project_id}"
                )

            logger.debug(f"Template generation completed successfully: {result}")
            return result

        except Exception as e:
            logger.error(
                f"Failed to generate strand template for project {project_id}: {e}"
            )
            logger.debug("Template generation exception details", exc_info=True)
            raise ValidationError(f"Template generation failed: {e}")

    def _extract_upstream_tasks(self, project_id: str, target_task_id: str) -> List:
        """
        Extract target task and all upstream dependencies.

        Args:
            project_id: Project ID
            target_task_id: Target task ID

        Returns:
            List of tasks including target and all dependencies
        """
        import networkx as nx

        # Get all project tasks
        all_tasks = self.storage.list_project_tasks(project_id)
        if not all_tasks:
            raise ValidationError(f"Project {project_id} has no tasks")

        # Find target task and build task map
        target_task = None
        task_map = {}
        for task in all_tasks:
            task_map[task.id] = task
            if task.id == target_task_id:
                target_task = task

        if not target_task:
            raise ValidationError(f"Target task {target_task_id} not found")

        # Build DAG
        dag = nx.DiGraph()
        for task in all_tasks:
            dag.add_node(task.id)

        for task in all_tasks:
            if hasattr(task, "dependencies") and task.dependencies:
                for dep_id in task.dependencies:
                    dag.add_edge(dep_id, task.id)

        # Get all ancestors (upstream dependencies) + target task
        upstream_task_ids = set(nx.ancestors(dag, target_task_id))
        upstream_task_ids.add(target_task_id)

        # Return filtered tasks
        return [task for task in all_tasks if task.id in upstream_task_ids]

    @require_aws_profile
    async def create_strand_execution(
        self,
        template_id: str,
        execution_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a strand template with real-time task synchronization.

        Args:
            template_id: Template ID to execute
            execution_config: Optional execution configuration

        Returns:
            Dict with execution_id, status, and monitoring info
        """
        logger.debug(
            "execute_graph_template: Starting execution: "
            f"template_id={template_id}, config={execution_config}"
        )

        try:
            # Look up project_id from template
            index = self.storage._get_project_index()
            project_id = index.get_template_mapping(template_id)
            if not project_id:
                raise ValidationError(f"Template {template_id} not found in index")
            logger.debug(
                "execute_graph_template: Looked up project_id from template: "
                f"{template_id} -> {project_id}"
            )
            from .strands.core.bridge import ExecutionService

            # Validate project exists
            logger.debug(f"Validating project existence: {project_id}")
            project = self.storage.get_project(project_id)
            if not project:
                logger.error(f"Project not found: {project_id}")
                raise ValidationError(f"Project {project_id} not found")

            logger.debug(f"Project validated: {project.friendly_name}")

            # Get project tasks for synchronization
            logger.debug(f"Retrieving tasks for project: {project_id}")
            tasks = self.storage.list_project_tasks(project_id)
            if not tasks:
                logger.error(f"No tasks found in project: {project_id}")
                raise ValidationError(f"Project {project_id} has no tasks to execute")

            logger.debug(
                f"Found {len(tasks)} tasks for execution: "
                f"{[task.title for task in tasks]}"
            )

            # Execute template using bridge
            logger.debug(
                "Calling ExecutionService.start_template_execution "
                f"with {len(tasks)} tasks"
            )
            result = await ExecutionService.start_template_execution(
                project, tasks, self.lackey_dir, template_id, execution_config or {}
            )

            logger.debug(
                "Strand execution initiated successfully: "
                f"execution_id={result.get('execution_id')}, "
                f"status={result.get('status')}"
            )
            return result

        except Exception as e:
            logger.error(
                f"Failed to execute strand template for project {project_id}: {e}"
            )
            logger.debug("Strand execution exception details", exc_info=True)
            raise ValidationError(f"Template execution failed: {e}")

    @require_aws_profile
    def get_strand_execution(
        self, execution_id: str, include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Monitor the status of a strand execution.

        Args:
            execution_id: Execution ID to monitor
            include_details: Whether to include detailed execution logs

        Returns:
            Dict with execution status, progress, and optional details
        """
        try:
            # Validate execution_id is a valid UUID
            try:
                uuid.UUID(execution_id)
            except ValueError:
                raise ValidationError(
                    f"Invalid execution_id format: {execution_id}. "
                    f"Must be a valid UUID."
                )

            from .strands.core.bridge import ExecutionService

            # Get project_id from index
            index = self.storage._get_project_index()
            project_id = index.get_execution_mapping(execution_id)

            if not project_id:
                raise ValidationError(f"Execution {execution_id} not found")

            # Get execution status using bridge with correct parameters
            result = ExecutionService.get_execution_status(
                execution_id, self.lackey_dir, project_id, include_details
            )

            if not result:
                raise ValidationError(f"Execution {execution_id} not found")

            return result

        except Exception as e:
            logger.error(f"Failed to monitor strand execution {execution_id}: {e}")
            raise ValidationError(f"Execution monitoring failed: {e}")

    def get_execution_report(self, execution_id: str) -> Dict[str, Any]:
        """
        Get detailed execution report for a strand execution.

        Args:
            execution_id: ID of the execution to analyze

        Returns:
            Dict with detailed execution report
        """
        try:
            import asyncio

            from .strands.monitor.analytics import ExecutionMetricsService

            analytics_collector = ExecutionMetricsService()
            report = asyncio.run(analytics_collector.generate_report(execution_id))

            return {
                "execution_id": report.execution_id,
                "template_id": report.template_id,
                "project_id": report.project_id,
                "start_time": (
                    report.start_time.isoformat() if report.start_time else None
                ),
                "end_time": report.end_time.isoformat() if report.end_time else None,
                "duration": (
                    report.duration.total_seconds() if report.duration else None
                ),
                "status": report.status,
                "metrics_count": len(report.metrics),
                "node_performance": report.node_performance,
                "recommendations": report.recommendations,
                "bottlenecks": report.bottlenecks,
            }

        except Exception as e:
            logger.error(f"Failed to get execution report: {e}")
            raise ValidationError(f"Failed to get execution report: {str(e)}")

    def analyze_template_performance(self, template_id: str) -> Dict[str, Any]:
        """
        Analyze performance across all executions of a template.

        Args:
            template_id: ID of the template to analyze

        Returns:
            Dict with template performance analysis
        """
        try:
            import asyncio

            from .strands.monitor.analytics import (
                ExecutionMetricsService,
                OptimizationEngine,
            )

            analytics_collector = ExecutionMetricsService()
            optimization_engine = OptimizationEngine(analytics_collector)

            return asyncio.run(
                optimization_engine.analyze_template_performance(template_id)
            )

        except Exception as e:
            logger.error(f"Failed to analyze template performance: {e}")
            raise ValidationError(f"Failed to analyze template performance: {str(e)}")

    # Private Helper Methods

    def _validate_task_dependencies(
        self, project_id: str, task: Task, dependencies: List[str]
    ) -> None:
        """Validate task dependencies exist and don't create cycles."""
        # Get all project tasks
        all_tasks = self.storage.list_project_tasks(project_id)

        # Check each dependency exists
        existing_task_ids = {t.id for t in all_tasks}
        for dep_id in dependencies:
            if dep_id not in existing_task_ids:
                raise DependencyError(f"Dependency task {dep_id} not found")

        # Check for cycles by simulating the task addition
        temp_tasks = all_tasks + [task]
        can_add, error_msg = (
            dependency_validator.can_add_dependency(
                task.id, dependencies[0], temp_tasks
            )
            if dependencies
            else (True, None)
        )

        if not can_add:
            raise DependencyError(f"Dependency validation failed: {error_msg}")

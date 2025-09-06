"""Bridge module for strand template generation and execution functionality."""

import asyncio
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .storage import ExecutionStorageService


class TemplateService:
    """Bridge class for strand template generation from Lackey core."""

    @staticmethod
    def create_execution_template(
        project: Any,
        tasks: List[Any],
        lackey_dir: Path,
        target_task_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate Strands execution template from Lackey project.

        Args:
            project: Lackey project object
            tasks: List of project tasks (filtered if partial execution)
            lackey_dir: Lackey directory path
            target_task_id: Optional target task ID for partial execution

        Returns:
            Dict with template_path and metadata
        """
        import logging

        logger = logging.getLogger(__name__)

        project_id = project.id if hasattr(project, "id") else str(project)
        logger.debug(
            f"TemplateService.create_execution_template starting: "
            f"project_id={project_id}, tasks={len(tasks)}, "
            f"target_task_id={target_task_id}"
        )

        # Convert project and tasks to strand graph specification
        from ..generate.template_generator import GraphBuilder

        # Convert project and tasks to dict format for template generator
        logger.debug(
            "Converting project and tasks to dict format for template generator"
        )
        project_data = {
            "id": project.id if hasattr(project, "id") else str(project),
            "name": project.name if hasattr(project, "name") else str(project),
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "objective": task.objective if hasattr(task, "objective") else "",
                    "complexity": (
                        task.complexity.value
                        if hasattr(task, "complexity")
                        and hasattr(task.complexity, "value")
                        else "medium"
                    ),
                    "dependencies": (
                        list(task.dependencies) if hasattr(task, "dependencies") else []
                    ),
                }
                for task in tasks
            ],
        }

        builder = GraphBuilder()
        spec = builder.build_from_project(project_data)

        # Store template using strand storage
        from ...storage import LackeyStorage

        lackey_storage = LackeyStorage(str(lackey_dir))
        storage = ExecutionStorageService(
            lackey_storage, project.id if hasattr(project, "id") else None
        )
        storage.save_execution_graph(spec)

        # Calculate template path
        template_path = storage.graphs_dir / f"{spec.id}.json"

        # Generate Python code during generation phase
        logger.debug("Generating Python execution code using Jinja2 template")

        # Prepare task info map from actual tasks
        task_info_map = {}
        for task in tasks:
            # Handle complexity enum properly
            complexity = "medium"  # default
            if hasattr(task, "complexity"):
                if hasattr(task.complexity, "value"):
                    complexity = task.complexity.value
                else:
                    complexity = str(task.complexity).lower()

            # Get task steps and success criteria
            steps = getattr(task, "steps", [])
            success_criteria = getattr(task, "success_criteria", [])

            # Get task notes (all notes for complete context)
            notes = []
            if hasattr(task, "note_manager") and task.note_manager:
                try:
                    # Get all user and system notes, excluding status changes
                    all_notes = task.note_manager.get_notes()
                    for note in all_notes:
                        if not note.content.startswith("Status changed to"):
                            notes.append(
                                {
                                    "content": note.content,
                                    "type": (
                                        note.note_type.value
                                        if hasattr(note.note_type, "value")
                                        else str(note.note_type)
                                    ),
                                    "created": (
                                        note.created.isoformat()
                                        if hasattr(note.created, "isoformat")
                                        else str(note.created)
                                    ),
                                }
                            )
                except (AttributeError, ValueError, KeyError) as e:
                    # If note retrieval fails, continue without notes
                    logger.debug(f"Note retrieval failed: {e}")

            task_info_map[task.id] = {
                "title": task.title,
                "objective": getattr(
                    task, "objective", "Complete this task effectively."
                ),
                "complexity": complexity,
                "steps": steps,
                "success_criteria": success_criteria,
                "notes": notes,
            }

        # Generate Python code using the Jinja2 template system
        from lackey.strands.generate.template_generator import generate_template

        logger.debug(
            f"create_execution_template: About to call generate_template "
            f"with lackey_dir: {lackey_dir}"
        )
        logger.debug(f"create_execution_template: lackey_dir type: {type(lackey_dir)}")
        logger.debug(
            f"create_execution_template: lackey_dir exists: "
            f"{lackey_dir.exists() if lackey_dir else 'N/A'}"
        )

        python_code = generate_template(spec, task_info_map, lackey_dir)

        # Save generated Python code to generated directory
        generated_dir = storage.graphs_dir.parent / "generated"
        generated_dir.mkdir(parents=True, exist_ok=True)
        python_file = generated_dir / f"{spec.id}.py"
        python_file.write_text(python_code)

        logger.debug(f"Generated Python execution file: {python_file}")

        # Determine execution type
        execution_type = "partial" if target_task_id else "full"

        return {
            "template_path": str(template_path),
            "python_file": str(python_file),
            "spec_id": spec.id,
            "node_count": len(spec.nodes),
            "validation_passed": True,
            "execution_type": execution_type,
            "target_task_id": target_task_id,
            "selected_task_count": len(tasks),
        }

    @staticmethod
    def get_template_metadata(
        template_id: str,
        lackey_dir: Path,
        project_id: Optional[str] = None,
        include_details: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Get the metadata of a strand template and its executions.

        Args:
            template_id: Template ID to check
            lackey_dir: Lackey directory path
            project_id: Optional project ID for context
            include_details: Whether to include detailed execution information

        Returns:
            Dict with template status, active executions, and history
        """
        try:
            # If no project_id provided, use template_id as project_id (common pattern)
            if not project_id:
                project_id = template_id

            project_strands_dir = lackey_dir / "projects" / project_id / "strands"
            template_file = project_strands_dir / "graphs" / f"{template_id}.json"
            executions_dir = project_strands_dir / "executions"
            generated_dir = project_strands_dir / "generated"

            # Check if template exists
            if not template_file.exists():
                return None

            # Load template info
            template_data = json.loads(template_file.read_text())

            # Find executions for this template
            template_executions = []
            active_executions = []

            if executions_dir.exists():
                for execution_file in executions_dir.glob("*.json"):
                    try:
                        execution_data = json.loads(execution_file.read_text())
                        if execution_data.get("template_id") == template_id:
                            execution_info = {
                                "execution_id": execution_data.get("execution_id"),
                                "status": execution_data.get("status", "unknown"),
                                "created": execution_data.get("created"),
                                "node_count": execution_data.get("node_count", 0),
                            }

                            if include_details:
                                execution_info.update(
                                    {
                                        "monitoring_available": execution_data.get(
                                            "monitoring_available", False
                                        ),
                                        "execution_config": execution_data.get(
                                            "execution_config", {}
                                        ),
                                    }
                                )

                            template_executions.append(execution_info)

                            # Track active executions
                            if execution_data.get("status") in ["running", "pending"]:
                                active_executions.append(execution_info)

                    except (json.JSONDecodeError, KeyError):
                        continue

            # Check for generated templates
            generated_templates = []
            if generated_dir.exists():
                for generated_file in generated_dir.glob(f"{template_id}*.py"):
                    generated_templates.append(
                        {
                            "file": generated_file.name,
                            "created": datetime.fromtimestamp(
                                generated_file.stat().st_mtime, tz=UTC
                            ).isoformat(),
                        }
                    )

            result = {
                "template_id": template_id,
                "project_id": project_id,
                "template_exists": True,
                "node_count": len(template_data.get("nodes", [])),
                "execution_count": len(template_executions),
                "active_execution_count": len(active_executions),
                "generated_template_count": len(generated_templates),
                "last_execution": (
                    template_executions[0] if template_executions else None
                ),
                "active_executions": active_executions,
            }

            if include_details:
                result.update(
                    {
                        "template_data": template_data,
                        "all_executions": template_executions,
                        "generated_templates": generated_templates,
                    }
                )

            return result

        except Exception as e:
            raise ValueError(f"Failed to get template status: {e}")


class ExecutionService:
    """Bridge class for strand execution and monitoring from Lackey core."""

    @staticmethod
    async def start_template_execution(
        project: Any,
        tasks: List[Any],
        lackey_dir: Path,
        template_id: Optional[str] = None,
        execution_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a strand template with real-time task synchronization.

        Args:
            project: Lackey project object
            tasks: List of project tasks
            lackey_dir: Lackey directory path
            template_id: Optional specific template ID
            execution_config: Optional execution configuration

        Returns:
            Dict with execution_id, status, and monitoring info
        """
        import logging

        logger = logging.getLogger(__name__)

        project_id = project.id if hasattr(project, "id") else "unknown"
        logger.debug(
            f"StrandExecutionBridge.start_template_execution starting: "
            f"project_id={project_id}, template_id={template_id}, "
            f"tasks={len(tasks)}"
        )

        try:
            from ...storage import LackeyStorage
            from ..core.storage import ExecutionStorageService

            # Initialize storage
            logger.debug(f"Initializing storage systems for project {project_id}")
            lackey_storage = LackeyStorage(str(lackey_dir))
            strand_storage = ExecutionStorageService(
                lackey_storage, project.id if hasattr(project, "id") else None
            )

            # Get or find template
            if template_id:
                logger.debug(f"Loading specific template: {template_id}")
                spec = strand_storage.get_execution_graph(template_id)
                if not spec:
                    logger.error(f"Template not found: {template_id}")
                    raise ValueError(f"Template {template_id} not found")
                logger.debug(
                    f"Template loaded successfully: {spec.id} "
                    f"with {len(spec.nodes)} nodes"
                )
            else:
                # Find most recent template for project
                logger.debug(f"Finding most recent template for project {project_id}")
                templates = strand_storage.list_execution_graphs()
                project_templates = []
                for t in templates:
                    if isinstance(t, dict):
                        metadata: Any = t.get("metadata", {})
                        if (
                            isinstance(metadata, dict)
                            and metadata.get("project_id") == project.id
                        ):
                            project_templates.append(t)
                if not project_templates:
                    logger.error(
                        f"BRIDGE_DEBUG: No templates found for project {project.id}"
                    )
                    raise ValueError(f"No templates found for project {project.id}")

                # Use most recent template
                latest_template = max(
                    project_templates, key=lambda x: x.get("created", "")
                )
                spec = strand_storage.get_execution_graph(latest_template["id"])

            # Create execution record
            execution_id = str(uuid.uuid4())
            execution_record = {
                "execution_id": execution_id,
                "template_id": spec.id,
                "project_id": project.id,
                "status": "pending",
                "created": datetime.now(UTC).isoformat(),
                "config": execution_config or {},
                "task_mappings": {
                    node.id: node.metadata.get("task_id") for node in spec.nodes
                },
                "progress": {
                    "total_nodes": len(spec.nodes),
                    "completed_nodes": 0,
                    "failed_nodes": 0,
                    "active_nodes": 0,
                },
            }

            # Initialize analytics collection
            try:
                from ..monitor.analytics import ExecutionMetricsService

                analytics_collector = ExecutionMetricsService()
                asyncio.create_task(
                    analytics_collector.record_execution_start_time(
                        execution_id=execution_id,
                        template_id=spec.id,
                        project_id=project.id,
                        config=execution_config or {},
                    )
                )
            except ImportError:
                logger.debug(
                    "Analytics collection not available - module could not be imported"
                )
            except Exception as e:
                logger.debug(f"Analytics collection failed: {e}")

            # Save execution record
            executions_dir = (
                lackey_dir / "projects" / project.id / "strands" / "executions"
            )
            executions_dir.mkdir(parents=True, exist_ok=True)
            execution_file = executions_dir / f"{execution_id}.json"
            execution_file.write_text(json.dumps(execution_record, indent=2))

            # Add execution mapping to index
            try:
                from ...storage import LackeyStorage

                storage = LackeyStorage(str(lackey_dir))
                index = storage._get_project_index()
                index.add_execution_mapping(execution_id, project.id)
                storage._save_project_index(index)
            except Exception as e:
                logger.warning(f"Failed to update execution index: {e}")

            # Use simplified runtime executor approach
            try:
                # Update execution record
                execution_record["status"] = "running"

                # Save updated record
                execution_file.write_text(json.dumps(execution_record, indent=2))

                # Use pre-generated Python code instead of generating during execution
                logger.debug("Looking for pre-generated Python execution file")

                # Look for pre-generated Python file in the generated
                # directory
                generated_dir = (
                    lackey_dir / "projects" / project.id / "strands" / "generated"
                )
                python_file = generated_dir / f"{spec.id}.py"

                if not python_file.exists():
                    # Fallback: generate Python code if not found
                    # (for backward compatibility)
                    logger.warning(
                        f"Pre-generated Python file not found: {python_file}"
                    )
                    logger.debug(
                        "Falling back to runtime generation for backward compatibility"
                    )

                    # Prepare task info map from actual tasks
                    task_info_map = {}
                    for task in tasks:
                        # Handle complexity enum properly
                        complexity = "medium"  # default
                        if hasattr(task, "complexity"):
                            if hasattr(task.complexity, "value"):
                                complexity = task.complexity.value
                            else:
                                complexity = str(task.complexity).lower()

                        # Get task steps and success criteria
                        steps = getattr(task, "steps", [])
                        success_criteria = getattr(task, "success_criteria", [])

                        # Get task notes (all notes for complete context)
                        notes = []
                        if hasattr(task, "note_manager") and task.note_manager:
                            try:
                                # Get all user and system notes,
                                # excluding status changes
                                all_notes = task.note_manager.get_notes()
                                for note in all_notes:
                                    if not note.content.startswith("Status changed to"):
                                        notes.append(
                                            {
                                                "content": note.content,
                                                "type": (
                                                    note.note_type.value
                                                    if hasattr(note.note_type, "value")
                                                    else str(note.note_type)
                                                ),
                                                "created": (
                                                    note.created.isoformat()
                                                    if hasattr(
                                                        note.created, "isoformat"
                                                    )
                                                    else str(note.created)
                                                ),
                                            }
                                        )
                            except (AttributeError, ValueError, KeyError) as e:
                                # If note retrieval fails, continue without notes
                                logger.debug(f"Note retrieval failed: {e}")

                        task_info_map[task.id] = {
                            "title": task.title,
                            "objective": getattr(
                                task, "objective", "Complete this task effectively."
                            ),
                            "complexity": complexity,
                            "steps": steps,
                            "success_criteria": success_criteria,
                            "notes": notes,
                        }

                    from lackey.strands.generate.template_generator import (
                        generate_template,
                    )

                    python_code = generate_template(spec, task_info_map, lackey_dir)

                    # Save generated code with execution-specific filename
                    generated_dir.mkdir(parents=True, exist_ok=True)
                    python_file = generated_dir / f"{execution_id}.py"
                    python_file.write_text(python_code)
                    logger.debug(
                        f"Generated Python file during execution: {python_file}"
                    )
                else:
                    logger.debug(f"Using pre-generated Python file: {python_file}")

                # Use simplified runtime executor with Strands Graph pattern
                from lackey.strands.execute.runtime_executor import (
                    GraphExecutionService,
                )

                runtime_executor = GraphExecutionService(lackey_storage, lackey_dir)

                # Start execution in background using the Python template
                logger.debug(
                    "BRIDGE_DEBUG: About to create asyncio task for "
                    "simplified runtime executor"
                )
                logger.debug(f"BRIDGE_DEBUG: Execution ID: {execution_id}")
                logger.debug(f"BRIDGE_DEBUG: Python code file: {python_file}")

                # Start execution in background without blocking
                absolute_path = str(python_file.resolve())
                logger.info(f"BRIDGE_DEBUG: Absolute path: {absolute_path}")

                # Start the execution asynchronously in a separate thread
                import threading

                def run_execution() -> None:
                    """Run execution in background thread."""
                    try:
                        result = runtime_executor.execute_graph_template(
                            template_path=absolute_path,
                            execution_id=execution_id,
                            timeout=300,
                        )
                        logger.info(
                            f"BRIDGE_DEBUG: Template execution completed: {result}"
                        )
                    except Exception as e:
                        logger.error(f"BRIDGE_DEBUG: Template execution failed: {e}")

                execution_thread = threading.Thread(target=run_execution, daemon=True)
                execution_thread.start()

                logger.debug("BRIDGE_DEBUG: Background execution started")
                logger.debug("BRIDGE_DEBUG: Returning execution response")

                return {
                    "execution_id": execution_id,
                    "status": "running",
                    "template_id": spec.id,
                    "project_id": project.id,
                    "node_count": len(spec.nodes),
                    "monitoring_available": True,
                }

            except ImportError as e:
                # Show the actual import error at info level
                import logging
                import traceback

                logger = logging.getLogger(__name__)
                error_details = traceback.format_exc()
                logger.info(f"Runtime executor import failed: {e}")
                logger.info(f"Full traceback: {error_details}")

                # Fallback to basic execution tracking without runtime executor
                execution_record["status"] = "queued"
                execution_file.write_text(json.dumps(execution_record, indent=2))

                return {
                    "execution_id": execution_id,
                    "status": "queued",
                    "template_id": spec.id,
                    "project_id": project.id,
                    "node_count": len(spec.nodes),
                    "monitoring_available": True,
                    "note": f"Runtime executor import failed: {e}",
                    "error_details": str(e),
                }

        except Exception as e:
            raise ValueError(f"Failed to execute template: {e}")

    @staticmethod
    def get_execution_status(
        execution_id: str,
        lackey_dir: Path,
        project_id: str,
        include_details: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Get the real-time status of a strand execution by checking running processes.

        Args:
            execution_id: Execution ID to check
            lackey_dir: Lackey directory path
            project_id: Project ID for path resolution
            include_details: Whether to include detailed process info

        Returns:
            Dict with actual execution status and process details, or None
            if not found
        """
        from datetime import datetime, timezone

        import psutil  # Required for process monitoring

        # Check if process is actually running by searching for execution_id
        # in process list
        running_process = None
        for proc in psutil.process_iter(
            ["pid", "name", "cmdline", "cpu_percent", "memory_percent", "create_time"]
        ):
            try:
                cmdline = " ".join(proc.info["cmdline"] or [])
                if execution_id in cmdline and "python" in proc.info["name"]:
                    running_process = {
                        "pid": proc.info["pid"],
                        "cpu_percent": proc.info["cpu_percent"] or 0.0,
                        "memory_percent": proc.info["memory_percent"] or 0.0,
                        "start_time": datetime.fromtimestamp(
                            proc.info["create_time"]
                        ).strftime("%H:%M:%S"),
                        "cpu_time": "0:00",  # psutil doesn't directly provide this
                        # in the same format
                    }
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Process may have disappeared or we don't have access
                continue

        # Check for execution record (for metadata)
        executions_dir = lackey_dir / "projects" / project_id / "strands" / "executions"
        execution_file = executions_dir / f"{execution_id}.json"

        execution_record = {}
        if execution_file.exists():
            execution_record = json.loads(execution_file.read_text())

        # Executor log path
        log_file = lackey_dir / "logs" / f"executor_{execution_id}.log"

        # Determine actual status based on process check
        if running_process:
            status = "running"
            # Calculate runtime if we have start time from record
            runtime_seconds = None
            if execution_record.get("created"):
                try:
                    created_time = datetime.fromisoformat(
                        execution_record["created"].replace("Z", "+00:00")
                    )
                    runtime_seconds = (
                        datetime.now(timezone.utc) - created_time
                    ).total_seconds()
                except (ValueError, TypeError):
                    # Handle parsing errors gracefully, default to None
                    runtime_seconds = None

            result = {
                "execution_id": execution_id,
                "status": status,
                "template_id": execution_record.get("template_id"),
                "project_id": execution_record.get("project_id"),
                "created": execution_record.get("created"),
                "log_path": str(log_file),
                "process": {
                    "pid": running_process["pid"],
                    "cpu_percent": running_process["cpu_percent"],
                    "memory_percent": running_process["memory_percent"],
                    "cpu_time": running_process["cpu_time"],
                    "runtime_seconds": runtime_seconds,
                },
            }
        else:
            # Process not running - check if we have logs to determine final status
            if log_file.exists():
                # Check last few lines of log to determine if completed or failed
                try:
                    log_content = log_file.read_text()
                    if (
                        "Graph execution completed with status: Status.COMPLETED"
                        in log_content
                    ):
                        status = "completed"
                    elif (
                        "failed" in log_content.lower()
                        or "error" in log_content.lower()
                    ):
                        status = "failed"
                    else:
                        status = "unknown"
                except Exception:
                    status = "unknown"
            else:
                status = "not_found" if not execution_record else "unknown"

            result = {
                "execution_id": execution_id,
                "status": status,
                "template_id": execution_record.get("template_id"),
                "project_id": execution_record.get("project_id"),
                "created": execution_record.get("created"),
                "log_path": str(log_file) if log_file.exists() else None,
                "process": None,
            }

        return result

    @staticmethod
    def list_executions(lackey_dir: Path, project_id: str) -> List[Dict[str, Any]]:
        """
        List all strand executions for a project.

        Args:
            lackey_dir: Lackey directory path
            project_id: Project ID for path resolution

        Returns:
            List of execution summaries
        """
        try:
            executions_dir = (
                lackey_dir / "projects" / project_id / "strands" / "executions"
            )
            if not executions_dir.exists():
                return []

            executions = []
            for execution_file in executions_dir.glob("*.json"):
                if execution_file.name.endswith("_logs.json"):
                    continue  # Skip log files

                try:
                    execution_record = json.loads(execution_file.read_text())

                    # Validate that execution has required fields
                    required_fields = [
                        "execution_id",
                        "status",
                        "project_id",
                        "template_id",
                    ]
                    if not all(
                        field in execution_record
                        and execution_record[field] is not None
                        for field in required_fields
                    ):
                        import logging

                        logger = logging.getLogger(__name__)
                        logger.warning(
                            f"Skipping execution file with missing required fields "
                            f"{execution_file}: missing one of {required_fields}"
                        )
                        continue

                    executions.append(
                        {
                            "execution_id": execution_record.get("execution_id"),
                            "status": execution_record.get("status"),
                            "project_id": execution_record.get("project_id"),
                            "template_id": execution_record.get("template_id"),
                            "created": execution_record.get("created"),
                            "progress": execution_record.get("progress", {}),
                        }
                    )

                except json.JSONDecodeError as e:
                    # Log corrupted JSON files with specific error
                    import logging

                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"Skipping execution file with invalid JSON "
                        f"{execution_file}: {e}"
                    )
                    continue
                except (KeyError, ValueError) as e:
                    # Log files with missing required fields or invalid values
                    import logging

                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"Skipping execution file with invalid structure "
                        f"{execution_file}: {e}"
                    )
                    continue

            # Sort by creation time (most recent first)
            executions.sort(key=lambda x: x.get("created") or "", reverse=True)
            return executions

        except Exception as e:
            raise ValueError(f"Failed to list executions: {e}")

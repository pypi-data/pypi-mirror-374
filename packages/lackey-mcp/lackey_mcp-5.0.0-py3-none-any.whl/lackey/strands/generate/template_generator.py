"""Template generation engine for Strands execution graphs using Jinja2 templates."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import jinja2

from ..core.models import ExecutionGraphSpec, ExecutionNode, NodeType
from ..generate.dag_analyzer import GraphAnalysisService


@dataclass
class AgentConfig:
    """Agent configuration for strand execution."""

    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None


class PythonCodeGenerator:
    """Generates Python templates for Strands execution graphs.

    Uses separate template files for generating Python code.

    Uses separate template files for generating Python code.
    """

    def __init__(self) -> None:
        """Initialize Python code generator with DAG analyzer."""
        self.dag_analyzer = GraphAnalysisService()

    def generate_python_code(
        self,
        spec: ExecutionGraphSpec,
        task_info_map: Optional[Dict[str, Dict[str, Any]]] = None,
        lackey_dir: Optional[Path] = None,
    ) -> str:
        """Generate Python code from strand graph specification using Jinja2."""
        # Validate DAG structure
        if not self.dag_analyzer.validate_graph_structure(spec):
            raise ValueError("Invalid DAG structure detected")

        # Get AWS profile from config
        try:
            from lackey.config.config_manager import get_config

            config = get_config()
            aws_profile = config.get_aws_profile()
            session_setup = f"""# Configure AWS session with profile
session = boto3.Session(
    profile_name={repr(aws_profile)}, region_name='us-east-1'
)"""
        except Exception:
            # Fallback if config not available
            session_setup = """# Using default AWS credentials
session = None"""

        # Load rules for embedding in system prompts
        rules = []

        # Get logger for proper logging
        import logging

        logger = logging.getLogger(__name__)

        logger.debug(
            f"generate_python_code: Template generator called with lackey_dir: "
            f"{lackey_dir}"
        )
        logger.debug(f"generate_python_code: lackey_dir type: {type(lackey_dir)}")
        logger.debug(
            f"generate_python_code: lackey_dir exists: "
            f"{lackey_dir.exists() if lackey_dir else 'N/A'}"
        )

        if lackey_dir:
            try:
                logger.debug(
                    "generate_python_code: Attempting to import "
                    "load_all_project_rules"
                )
                from ..execute.rules_injection import load_all_project_rules

                logger.debug(
                    f"generate_python_code: Import successful, loading rules from: "
                    f"{lackey_dir}"
                )

                # Rules are in the project root, not inside .lackey directory
                # lackey_dir points to .lackey, so we need its parent for the
                # project root
                project_root = lackey_dir.parent
                logger.debug(f"generate_python_code: Project root: {project_root}")

                # Check if rules directory exists
                rules_dir = project_root / ".amazonq" / "rules"
                logger.debug(f"generate_python_code: Rules directory path: {rules_dir}")
                logger.debug(
                    f"generate_python_code: Rules directory exists: "
                    f"{rules_dir.exists()}"
                )

                if rules_dir.exists():
                    logger.debug(
                        f"generate_python_code: Rules directory contents: "
                        f"{list(rules_dir.iterdir())}"
                    )

                rules = load_all_project_rules(project_root)
                logger.debug(
                    f"generate_python_code: Successfully loaded {len(rules)} rules"
                )
                if rules:
                    logger.debug(f"generate_python_code: First 3 rules: {rules[:3]}")
                else:
                    logger.debug("generate_python_code: Rules list is empty")
            except ImportError as e:
                logger.debug(
                    f"generate_python_code: Import failed for rules_injection: {e}"
                )
                rules = []
            except Exception as e:
                logger.debug(
                    f"generate_python_code: Exception during rules loading: {e}"
                )
                import traceback

                logger.debug(
                    f"generate_python_code: Traceback: {traceback.format_exc()}"
                )
                rules = []
        else:
            logger.debug(
                "generate_python_code: lackey_dir is None, skipping rules loading"
            )

        # Generate task mapping for Graph nodes with complexity info
        task_mapping = {}
        for node in spec.nodes:
            # Use provided task info map or fallback to node information
            if task_info_map and node.id in task_info_map:
                task_info = task_info_map[node.id]
                task_name = task_info.get("title", "Execute task")
                task_prompt = task_info.get(
                    "objective", "Complete this task effectively."
                )
                task_complexity = task_info.get("complexity", "medium")
            else:
                # Fallback to node information
                task_name = node.name or "Execute task"
                task_prompt = node.prompt or "Complete this task effectively."
                task_complexity = "medium"

            task_mapping[node.id] = {
                "title": task_name,
                "objective": task_prompt,
                "complexity": task_complexity,
            }

            # Include additional task info if available
            if task_info_map and node.id in task_info_map:
                task_info = task_info_map[node.id]
                if "steps" in task_info:
                    task_mapping[node.id]["steps"] = task_info["steps"]
                if "success_criteria" in task_info:
                    task_mapping[node.id]["success_criteria"] = task_info[
                        "success_criteria"
                    ]
                # Remove notes to prevent semantic drift contamination

        # Generate dependency mapping
        dependencies = {}
        for node in spec.nodes:
            dependencies[node.id] = list(node.dependencies) if node.dependencies else []

        # Prepare template data for Jinja2
        logger.debug(f"generate_python_code: Raw rules count: {len(rules)}")
        logger.debug(
            f"generate_python_code: Raw rules sample: {rules[:2] if rules else 'EMPTY'}"
        )

        # Format rules as a single string block for template insertion
        if rules:
            logger.debug("generate_python_code: Rules exist, formatting...")
            # Create single string containing all rules with proper escaping
            import json

            all_rules_text = "\n".join(f"- {rule}" for rule in rules)
            rules_string = json.dumps(all_rules_text)
            logger.debug(
                f"generate_python_code: Final rules string length: {len(rules_string)}"
            )
        else:
            logger.debug("generate_python_code: No rules found, setting empty string")
            rules_string = ""

        logger.debug(f"generate_python_code: Rules string length: {len(rules_string)}")
        logger.debug(
            f"generate_python_code: Rules string is empty: {rules_string == ''}"
        )

        template_data: Dict[str, Any] = {
            "execution_id": spec.id,
            "session_setup": session_setup.strip(),
            "task_mapping": task_mapping,
            "dependencies": dependencies,
            "nodes": [],
            "edges": [],
            # Single formatted string
            "rules_block": rules_string,
        }

        logger.debug(
            f"generate_python_code: Template data keys: "
            f"{list(template_data.keys())}"
        )
        logger.debug(
            f"generate_python_code: rules_block in template_data: "
            f"{bool(template_data.get('rules_block'))}"
        )
        rules_preview = (
            template_data["rules_block"][:100]
            if template_data["rules_block"]
            else "EMPTY"
        )
        logger.debug(f"generate_python_code: rules_block value: {rules_preview}")
        logger.debug(
            f"generate_python_code: rules_block type: "
            f"{type(template_data['rules_block'])}"
        )

        # Prepare nodes data for template
        for node in spec.nodes:
            template_data["nodes"].append(
                {"id": node.id, "task_info": task_mapping[node.id]}
            )

        # Prepare edges data for template
        for node in spec.nodes:
            if node.dependencies:
                for dep_id in node.dependencies:
                    template_data["edges"].append({"from_id": dep_id, "to_id": node.id})

        # Load and render Jinja2 template
        template_path = (
            Path(__file__).parent.parent
            / "execute"
            / "templates"
            / "execution_template.py.j2"
        )

        try:
            # Create Jinja2 environment with autoescape enabled for security
            env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(template_path.parent),
                trim_blocks=True,
                lstrip_blocks=True,
                autoescape=False,  # nosec B701 - Safe for Python code generation
            )

            # Load template
            template = env.get_template(template_path.name)

            # Render template with data
            rendered_code = str(template.render(**template_data))

            return rendered_code

        except jinja2.TemplateNotFound:
            raise ValueError(f"Jinja2 template file not found: {template_path}")
        except jinja2.TemplateError as e:
            raise ValueError(f"Jinja2 template rendering error: {e}")
        except Exception as e:
            raise ValueError(f"Template generation failed: {e}")


class GraphBuilder:
    """Builder for creating strand graph specifications from Lackey projects."""

    def __init__(self) -> None:
        """Initialize graph builder with logger and template generator."""
        import logging

        self.logger = logging.getLogger(__name__)
        self.template_generator = PythonCodeGenerator()
        self.logger.debug("GraphBuilder initialized")

    def build_from_project(self, project_data: Dict) -> ExecutionGraphSpec:
        """Build strand graph specification from Lackey project data."""
        project_id = project_data.get("id", "unknown")
        tasks = project_data.get("tasks", [])
        self.logger.debug(
            f"build_from_project: Building strand graph from project: "
            f"project_id={project_id}, task_count={len(tasks)}"
        )

        # Filter out completed tasks - only include TODO, BLOCKED,
        # IN_PROGRESS
        incomplete_tasks = []
        completed_task_ids = set()

        for task in tasks:
            task_status = task.get("status", "todo")
            task_id = task.get("id", "unknown")

            if task_status == "done":
                completed_task_ids.add(task_id)
                self.logger.debug(
                    f"build_from_project: Excluding completed task: {task_id}"
                )
            else:
                incomplete_tasks.append(task)
                self.logger.debug(
                    f"build_from_project: Including incomplete task: "
                    f"{task_id} ({task_status})"
                )

        self.logger.debug(
            f"build_from_project: Filtered tasks: {len(incomplete_tasks)} incomplete, "
            f"{len(completed_task_ids)} completed"
        )

        nodes = []
        edges = []
        included_task_ids = set()

        # Convert incomplete tasks to nodes
        for task in incomplete_tasks:
            task_id = task.get("id", "unknown")
            task_deps = set(task.get("dependencies", []))
            included_task_ids.add(task_id)

            self.logger.debug(
                f"build_from_project: Converting task to node: task_id={task_id}, "
                f"dependencies={task_deps}"
            )

            node = ExecutionNode(
                id=task["id"],
                name=task["title"],
                node_type=NodeType.AGENT,
                complexity=task.get("complexity", "medium"),
                prompt=task.get("objective", ""),
                dependencies=task_deps,
            )
            nodes.append(node)

        self.logger.debug(
            f"build_from_project: Created {len(nodes)} nodes from incomplete " f"tasks"
        )

        # Convert dependencies to edges, but only for included tasks
        for task in incomplete_tasks:
            task_id = task["id"]
            for dep_id in task.get("dependencies", []):
                # Only create edge if both nodes are included in the
                # template
                if dep_id in included_task_ids:
                    edge = {"from_node": dep_id, "to_node": task_id}
                    edges.append(edge)
                    self.logger.debug(
                        f"build_from_project: Created edge: {dep_id} -> {task_id}"
                    )
                else:
                    self.logger.debug(
                        f"build_from_project: Skipping edge from completed task: "
                        f"{dep_id} -> {task_id}"
                    )

        self.logger.debug(
            f"build_from_project: Created {len(edges)} valid edges from dependencies"
        )

        spec = ExecutionGraphSpec(
            id=project_data["id"], name=project_data["name"], nodes=nodes, edges=edges
        )
        self.logger.debug(
            f"build_from_project: Built strand graph spec: id={spec.id}, "
            f"nodes={len(spec.nodes)}, edges={len(spec.edges)}"
        )
        return spec


def generate_template(
    spec: ExecutionGraphSpec,
    task_info_map: Optional[Dict[str, Dict[str, Any]]] = None,
    lackey_dir: Optional[Path] = None,
) -> str:
    """Generate template using PythonCodeGenerator."""
    generator = PythonCodeGenerator()
    return generator.generate_python_code(spec, task_info_map, lackey_dir)

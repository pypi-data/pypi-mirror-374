"""Atomic template storage with security validation."""

import hashlib
import json
import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.models import ExecutionGraphSpec
from ..generate.template_generator import PythonCodeGenerator

logger = logging.getLogger(__name__)


class TemplateStorageError(Exception):
    """Raised when template storage operations fail."""

    pass


class SecurityValidationError(TemplateStorageError):
    """Raised when security validation fails."""

    pass


class TemplateSecurityValidator:
    """Security validator for template content and paths."""

    # Dangerous patterns to detect in template content
    DANGEROUS_PATTERNS = [
        r"__import__\s*\(",
        r"eval\s*\(",
        r"exec\s*\(",
        r"subprocess\.",
        r"os\.system",
        r'open\s*\([^)]*["\'][wax]',  # File writes
    ]

    MAX_TEMPLATE_SIZE = 1024 * 1024  # 1MB limit

    def validate_project_id(self, project_id: str) -> None:
        """Validate project ID for path traversal attacks."""
        if not project_id or not isinstance(project_id, str):
            raise SecurityValidationError("Invalid project ID")

        if ".." in project_id or "/" in project_id or "\\" in project_id:
            raise SecurityValidationError("Project ID contains invalid characters")

    def validate_template_content(self, content: str) -> None:
        """Validate template content for dangerous patterns."""
        if len(content) > self.MAX_TEMPLATE_SIZE:
            raise SecurityValidationError(
                f"Template exceeds size limit ({self.MAX_TEMPLATE_SIZE} bytes)"
            )

        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                raise SecurityValidationError(
                    f"Template contains dangerous pattern: {pattern}"
                )


class StrandTemplateStorage:
    """Atomic template storage with project metadata integration."""

    def __init__(self, lackey_dir: Path):
        """Initialize template storage with security validation."""
        self.lackey_dir = lackey_dir
        self.templates_dir = lackey_dir / "strands" / "templates"
        self.metadata_file = self.templates_dir / "metadata.json"
        self.generator = PythonCodeGenerator()
        self.security_validator = TemplateSecurityValidator()

        # Ensure directories exist
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Initialize metadata if not exists
        if not self.metadata_file.exists():
            self._write_metadata({})

    def store_template(
        self,
        project_id: str,
        spec: ExecutionGraphSpec,
        task_info_map: Optional[Dict[str, Dict[Any, Any]]] = None,
    ) -> str:
        """Store template atomically with security validation and metadata tracking."""
        # Security validation
        self.security_validator.validate_project_id(project_id)

        template_id = f"{project_id}_{spec.id}"
        template_path = self.templates_dir / f"{template_id}.py"

        # Generate template content with task info map
        template_content = self.generator.generate_python_code(spec, task_info_map)

        # Validate template content for security
        self.security_validator.validate_template_content(template_content)

        # Calculate content hash for versioning
        content_hash = hashlib.sha256(template_content.encode()).hexdigest()[:12]

        # Atomic write with backup
        temp_path = template_path.with_suffix(".tmp")
        backup_path = (
            template_path.with_suffix(".bak") if template_path.exists() else None
        )

        try:
            # Write to temporary file
            temp_path.write_text(template_content, encoding="utf-8")

            # Backup existing file if present
            if backup_path and template_path.exists():
                template_path.rename(backup_path)

            # Atomic move
            temp_path.rename(template_path)

            # Update template metadata
            template_info = {
                "project_id": project_id,
                "spec_id": spec.id,
                "path": str(template_path.relative_to(self.lackey_dir)),
                "content_hash": content_hash,
                "created": datetime.now(UTC).isoformat(),
                "version": (
                    1 if not backup_path else self._get_next_version(template_id)
                ),
            }
            self._update_metadata(template_id, template_info)

            # Clean up backup on success
            if backup_path and backup_path.exists():
                backup_path.unlink()

            return str(template_path)

        except Exception as e:
            # Rollback on failure
            if temp_path.exists():
                temp_path.unlink()
            if backup_path and backup_path.exists():
                backup_path.rename(template_path)
            raise TemplateStorageError(f"Failed to store template: {e}")

    def get_template_path(self, project_id: str, spec_id: str) -> Optional[str]:
        """Get template path from metadata."""
        template_id = f"{project_id}_{spec_id}"
        metadata = self._read_metadata()
        template_info = metadata.get(template_id)

        if template_info:
            return str(self.lackey_dir / template_info["path"])
        return None

    def cleanup_templates(self, project_id: str, keep_versions: int = 3) -> List[str]:
        """Clean up old template versions."""
        metadata = self._read_metadata()
        cleaned_files = []

        # Group templates by project
        project_templates = {
            tid: info
            for tid, info in metadata.items()
            if info.get("project_id") == project_id
        }

        # Sort by version and clean up old ones
        for template_id, info in project_templates.items():
            version = info.get("version", 1)
            if version > keep_versions:
                template_path = self.lackey_dir / info["path"]
                if template_path.exists():
                    template_path.unlink()
                    cleaned_files.append(str(template_path))

                # Remove from metadata
                del metadata[template_id]

        self._write_metadata(metadata)
        return cleaned_files

    def cleanup_stale_templates(self) -> Dict[str, List[str]]:
        """Clean up stale templates and references."""
        result: Dict[str, List[str]] = {"cleaned_files": [], "cleaned_references": []}

        # Clean up orphaned template files
        metadata = self._read_metadata()
        for template_file in self.templates_dir.glob("*.py"):
            template_id = template_file.stem
            if template_id not in metadata:
                template_file.unlink()
                result["cleaned_files"].append(str(template_file))

        return result

    def _read_metadata(self) -> Dict[Any, Any]:
        """Read metadata atomically."""
        try:
            data = json.loads(self.metadata_file.read_text())
            if isinstance(data, dict):
                return data
            else:
                return {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _write_metadata(self, metadata: Dict) -> None:
        """Write metadata atomically."""
        temp_file = self.metadata_file.with_suffix(".tmp")
        try:
            temp_file.write_text(json.dumps(metadata, indent=2))
            temp_file.rename(self.metadata_file)
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            raise TemplateStorageError(f"Failed to write metadata: {e}")

    def _update_metadata(self, template_id: str, info: Dict) -> None:
        """Update metadata for a template."""
        metadata = self._read_metadata()
        metadata[template_id] = info
        self._write_metadata(metadata)

    def _get_next_version(self, template_id: str) -> int:
        """Get next version number for template."""
        metadata = self._read_metadata()
        template_data = metadata.get(template_id, {})
        current_version = (
            template_data.get("version", 0) if isinstance(template_data, dict) else 0
        )
        return current_version + 1 if isinstance(current_version, int) else 1

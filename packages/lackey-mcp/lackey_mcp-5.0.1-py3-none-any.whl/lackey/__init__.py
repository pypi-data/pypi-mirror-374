"""Lackey - Task chain management engine for AI agents."""

import logging
from pathlib import Path

from .core import LackeyCore
from .dependencies import (
    CircularDependencyError,
    DependencyError,
    DependencyValidator,
    dependency_validator,
)
from .file_ops import (
    FileOperationError,
    IntegrityError,
    TransactionError,
    TransactionManager,
    atomic_write,
)
from .models import (
    Complexity,
    LackeyConfig,
    Project,
    ProjectIndex,
    ProjectStatus,
    Task,
    TaskStatus,
)
from .storage import (
    LackeyStorage,
    ProjectNotFoundError,
    StorageError,
    TaskNotFoundError,
)
from .validation import InputValidator, SecurityError, ValidationError, validator

__version__ = "5.0.1"
__api_version__ = "5.0.0"  # MCP API compatibility version (semantic versioning)
__data_version__ = "2.0.0"  # Individual file version
__author__ = "Lackey Contributors"
__email__ = "contact@lackey.dev"

# API Compatibility Matrix
# Maps package versions to supported API versions
API_COMPATIBILITY_MATRIX = {
    "0.8.0": ["1.0.0"],
    "0.8.1": ["1.0.0"],
    "0.8.2": ["1.0.0"],
    "0.8.3": ["1.0.0"],
    "0.8.4": ["1.0.0"],
    "0.8.5": ["1.0.0"],
    "0.8.6": ["1.0.0"],
    "0.8.7": ["1.0.0"],  # Current baseline
    # Future versions will support multiple API versions for backward compatibility
    # "0.9.0": ["1.0.0", "1.1.0"],  # Example: backward compatible addition
    # "1.0.0": ["2.0.0"],           # Example: breaking change
    "1.0.0": ["2.0.0"],
    "3.0.0": ["3.0.0"],
    "3.0.1": ["3.0.0"],
    "3.0.2": ["3.0.0"],
    "3.0.3": ["3.0.0"],
    "3.0.4": ["3.0.0"],
    "3.0.5": ["3.0.0"],
    "3.1.0": ["3.0.0"],
    "3.1.1": ["3.0.0"],
    "4.0.0": ["4.0.0"],
    "5.0.0": ["5.0.0"],
}

# Configure logging - read level from config if available


def _get_log_level() -> str:
    """Get log level from lackey.config or default to INFO."""
    # Try current directory first, then .lackey subdirectory
    config_paths = [
        Path.cwd() / "lackey.config",
        Path.cwd() / ".lackey" / "lackey.config",
    ]

    for config_path in config_paths:
        if config_path.exists():
            try:
                import configparser

                config = configparser.ConfigParser()
                config.read(config_path)
                return config.get("general", "log_level", fallback="INFO").upper()
            except (configparser.Error, ValueError, AttributeError) as e:
                # Log config-related errors but continue checking other files
                logging.debug(f"Failed to read log level from {config_path}: {e}")
                continue
            except IOError as e:
                # Log file access errors
                logging.debug(f"I/O error while reading {config_path}: {e}")
                continue
            except Exception as e:
                # Log any unexpected exceptions instead of silently ignoring them
                logging.debug(f"Unexpected error reading {config_path}: {e}")
                # Continue to next config path or default value if all paths fail
                continue

    # Default log level if no config file is found or all failed to provide a log level
    return "INFO"


log_level = _get_log_level()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

__all__ = [
    # Version info
    "__version__",
    "__api_version__",
    "__data_version__",
    "API_COMPATIBILITY_MATRIX",
    # Core classes
    "LackeyCore",
    "LackeyStorage",
    # Models
    "Task",
    "Project",
    "ProjectIndex",
    "LackeyConfig",
    "TaskStatus",
    "Complexity",
    "ProjectStatus",
    # Validators
    "dependency_validator",
    "DependencyValidator",
    "validator",
    "InputValidator",
    # File operations
    "atomic_write",
    "TransactionManager",
    # Exceptions
    "ValidationError",
    "SecurityError",
    "FileOperationError",
    "IntegrityError",
    "TransactionError",
    "DependencyError",
    "CircularDependencyError",
    "StorageError",
    "TaskNotFoundError",
    "ProjectNotFoundError",
]

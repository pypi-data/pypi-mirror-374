"""Enhanced note system for Lackey task management.

This module provides rich note functionality with timestamps, metadata,
markdown support, and search capabilities for coordinated agent workflows.
"""

from __future__ import annotations

import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Union


def _high_precision_utcnow() -> datetime:
    """Generate high-precision UTC timestamp to avoid collisions."""
    # Use time.time_ns() for nanosecond precision, then convert to datetime
    # This ensures unique timestamps even for rapid operations
    ns_timestamp = time.time_ns()
    return datetime.fromtimestamp(ns_timestamp / 1_000_000_000, UTC)


class NoteType(Enum):
    """Note type enumeration for categorization."""

    USER = "user"  # Manual user note
    SYSTEM = "system"  # System-generated note
    STATUS_CHANGE = "status_change"  # Status transition note
    ASSIGNMENT = "assignment"  # Task assignment note
    PROGRESS = "progress"  # Progress update note
    DEPENDENCY = "dependency"  # Dependency change note
    ARCHIVE = "archive"  # Archive/restore note


@dataclass
class Note:
    """
    Rich note model with metadata and markdown support.

    Notes provide context, communication, and audit trail for task management
    with support for categorization, search, and chronological ordering.
    """

    id: str
    content: str
    note_type: NoteType
    created: datetime
    author: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        """Validate note data after initialization."""
        if not self.id:
            self.id = str(uuid.uuid4())

        # Normalize tags to lowercase and strip whitespace
        if self.tags:
            self.tags = {tag.lower().strip() for tag in self.tags if tag.strip()}

    @classmethod
    def create_user_note(
        cls,
        content: str,
        author: Optional[str] = None,
        tags: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Note:
        """Create a new user note."""
        return cls(
            id=str(uuid.uuid4()),
            content=content.strip(),
            note_type=NoteType.USER,
            created=_high_precision_utcnow(),
            author=author,
            tags=tags or set(),
            metadata=metadata or {},
        )

    @classmethod
    def create_system_note(
        cls,
        content: str,
        note_type: NoteType = NoteType.SYSTEM,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Note:
        """Create a new system-generated note."""
        return cls(
            id=str(uuid.uuid4()),
            content=content.strip(),
            note_type=note_type,
            created=_high_precision_utcnow(),
            author="system",
            metadata=metadata or {},
        )

    def add_tag(self, tag: str) -> None:
        """Add a tag to the note."""
        self.tags.add(tag.lower().strip())

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the note."""
        self.tags.discard(tag.lower().strip())

    def has_tag(self, tag: str) -> bool:
        """Check if note has a specific tag."""
        return tag.lower().strip() in self.tags

    def get_plain_text(self) -> str:
        """Extract plain text from markdown content."""
        # Remove markdown formatting for search
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", self.content)  # Bold
        text = re.sub(r"\*(.*?)\*", r"\1", text)  # Italic
        text = re.sub(r"`(.*?)`", r"\1", text)  # Code
        text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)  # Links
        text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)  # Headers
        text = re.sub(r"^\s*[-*+]\s*", "", text, flags=re.MULTILINE)  # Lists
        return text.strip()

    def matches_search(self, query: str) -> bool:
        """Check if note matches search query."""
        query_lower = query.lower()

        # Search in content (both markdown and plain text)
        if query_lower in self.content.lower():
            return True
        if query_lower in self.get_plain_text().lower():
            return True

        # Search in tags
        if any(query_lower in tag for tag in self.tags):
            return True

        # Search in author
        if self.author and query_lower in self.author.lower():
            return True

        # Search in metadata values
        for value in self.metadata.values():
            if isinstance(value, str) and query_lower in value.lower():
                return True

        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert note to dictionary for serialization."""
        return {
            "id": self.id,
            "content": self.content,
            "note_type": self.note_type.value,
            "created": self.created.isoformat(),
            "author": self.author,
            "metadata": self.metadata,
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Note:
        """Create note from dictionary."""
        created_dt = datetime.fromisoformat(data["created"])
        # Ensure timezone-aware datetime
        if created_dt.tzinfo is None:
            created_dt = created_dt.replace(tzinfo=UTC)

        return cls(
            id=data["id"],
            content=data["content"],
            note_type=NoteType(data["note_type"]),
            created=created_dt,
            author=data.get("author"),
            metadata=data.get("metadata", {}),
            tags=set(data.get("tags", [])),
        )

    def __str__(self) -> str:
        """Return string representation of note."""
        timestamp = self.created.strftime("%Y-%m-%d %H:%M")
        author_str = f" by {self.author}" if self.author else ""
        return f"[{timestamp}]{author_str}: {self.content}"


class NoteManager:
    """
    Manager for note operations with search and filtering capabilities.

    Provides high-level operations for managing task notes including
    chronological ordering, search, filtering, and history management.
    """

    def __init__(
        self,
        task_id: Optional[str] = None,
        project_id: Optional[str] = None,
        storage_path: Optional[Path] = None,
        notes: Optional[List[Note]] = None,
    ) -> None:
        """Initialize note manager with filesystem path or existing notes."""
        # Declare all attributes with types upfront to avoid redefinition
        self.task_id: Optional[str] = task_id
        self.project_id: Optional[str] = project_id
        self.notes_dir: Optional[Path] = None
        self._deferred_init: bool = False
        self._notes: Optional[List[Note]]
        self._notes_cache: Optional[List[Note]]
        self._filesystem_mode: bool

        # Set attribute values based on mode
        if notes is not None:
            # Legacy mode: in-memory notes (for backward compatibility)
            self._notes = notes
            self._notes_cache = None
            self._filesystem_mode = False
        elif all([task_id, project_id, storage_path]):
            # New mode: filesystem-based notes
            assert (  # nosec B101 - parameter validation assert
                task_id is not None
                and project_id is not None
                and storage_path is not None
            )
            self.notes_dir = (
                storage_path / "projects" / project_id / "tasks" / task_id / "notes"
            )
            self._notes = None
            self._notes_cache = None
            self._filesystem_mode = True
        else:
            # Deferred initialization mode - will be set up later
            self._notes = []
            self._notes_cache = None
            self._filesystem_mode = False
            self._deferred_init = True

    def initialize_filesystem_mode(
        self, task_id: str, project_id: str, storage_path: Path
    ) -> None:
        """Initialize filesystem mode after construction."""
        if hasattr(self, "_deferred_init") and self._deferred_init:
            self.task_id = task_id
            self.project_id = project_id
            if storage_path is not None:  # Ensure storage_path is not None for mypy
                self.notes_dir = (
                    storage_path / "projects" / project_id / "tasks" / task_id / "notes"
                )
            self._notes_cache = None
            self._filesystem_mode = True
            delattr(self, "_deferred_init")
            # Clear legacy notes list
            if hasattr(self, "_notes"):
                self._notes = None

    def _load_notes(self) -> List[Note]:
        """Load all notes from filesystem or cache."""
        # Check for deferred init
        if hasattr(self, "_deferred_init") and self._deferred_init:
            return []

        if not self._filesystem_mode:
            return self._notes if self._notes is not None else []

        if self._notes_cache is not None:
            return self._notes_cache

        notes = []
        if self.notes_dir and self.notes_dir.exists():
            from datetime import datetime, timezone

            for note_file in self.notes_dir.glob("*.md"):
                try:
                    content = note_file.read_text()

                    # Try to parse YAML frontmatter first
                    if content.startswith("---\n"):
                        # Split frontmatter and content
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            # Parse YAML frontmatter
                            import yaml

                            try:
                                frontmatter = yaml.safe_load(parts[1])
                                note_content = parts[2].strip()

                                # Use frontmatter data
                                note_data: Dict[str, Any] = {
                                    "id": frontmatter.get("id", note_file.stem),
                                    "content": note_content,
                                    "note_type": frontmatter.get("note_type", "user"),
                                    "created": frontmatter.get(
                                        "created",
                                        datetime.fromtimestamp(
                                            note_file.stat().st_mtime, tz=timezone.utc
                                        ).isoformat(),
                                    ),
                                    "author": frontmatter.get("author"),
                                    "tags": frontmatter.get("tags", []),
                                    "metadata": frontmatter.get("metadata", {}),
                                }
                            except yaml.YAMLError:
                                # Fall back to legacy format if YAML parsing fails
                                note_data = {
                                    "id": note_file.stem,
                                    "content": content.strip(),
                                    "note_type": "user",
                                    "created": datetime.fromtimestamp(
                                        note_file.stat().st_mtime, tz=timezone.utc
                                    ).isoformat(),
                                    "author": None,
                                    "tags": [],
                                    "metadata": {},
                                }
                        else:
                            # Malformed frontmatter, treat as legacy
                            note_data = {
                                "id": note_file.stem,
                                "content": content.strip(),
                                "note_type": "user",
                                "created": datetime.fromtimestamp(
                                    note_file.stat().st_mtime, tz=timezone.utc
                                ).isoformat(),
                                "author": None,
                                "tags": [],
                                "metadata": {},
                            }
                    else:
                        # Legacy format without frontmatter
                        note_data = {
                            "id": note_file.stem,
                            "content": content.strip(),
                            "note_type": "user",  # Default type for legacy notes
                            "created": datetime.fromtimestamp(
                                note_file.stat().st_mtime, tz=timezone.utc
                            ).isoformat(),
                            "author": None,
                            "tags": [],
                            "metadata": {},
                        }

                    notes.append(Note.from_dict(note_data))
                except (OSError, ValueError, KeyError) as e:
                    # Log specific error for debugging but continue processing
                    # other notes.
                    # Possible errors:
                    # - OSError: file read issues
                    # - ValueError: date parsing
                    # - KeyError: missing fields
                    import logging

                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"Failed to load note from {note_file}: {e!r} - skipping"
                    )
                    continue

        self._notes_cache = sorted(notes, key=lambda n: n.created)
        return self._notes_cache

    def add_note(
        self,
        content: str,
        note_type: Union[NoteType, str] = NoteType.USER,
        author: Optional[str] = None,
        tags: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Note:
        """Add a new note and return it."""
        import logging

        logger = logging.getLogger(__name__)

        # Convert string note_type to NoteType enum if needed
        if isinstance(note_type, str):
            try:
                note_type = NoteType(note_type)
            except ValueError:
                # If invalid string, default to USER
                note_type = NoteType.USER

        logger.info(
            f"add_note: Adding note with type={note_type}, content='{content[:30]}...'"
        )

        if note_type == NoteType.USER:
            logger.info("add_note: Creating user note")
            note = Note.create_user_note(content, author, tags, metadata)
        else:
            # For non-user notes, create manually to preserve author
            logger.info(f"add_note: Creating {note_type} note manually")
            note = Note(
                id=str(uuid.uuid4()),
                content=content.strip(),
                note_type=note_type,
                created=_high_precision_utcnow(),
                author=author or "system",
                tags=tags or set(),
                metadata=metadata or {},
            )

        logger.info(
            f"add_note: Created note with id={note.id}, type={note.note_type}, "
            f"content='{note.content[:30]}...'"
        )

        if self._filesystem_mode:
            # Save to filesystem as markdown with YAML frontmatter
            if self.notes_dir:
                self.notes_dir.mkdir(parents=True, exist_ok=True)
                note_file = self.notes_dir / f"{note.id}.md"

                # Create YAML frontmatter with metadata
                import yaml

                frontmatter: Dict[str, Any] = {
                    "id": note.id,
                    "note_type": (
                        note.note_type.value
                        if hasattr(note.note_type, "value")
                        else str(note.note_type)
                    ),
                    "created": (
                        note.created.isoformat()
                        if hasattr(note.created, "isoformat")
                        else str(note.created)
                    ),
                    "author": note.author,
                }

                # Add optional fields
                if note.tags:
                    frontmatter["tags"] = list(note.tags)
                if note.metadata:
                    frontmatter["metadata"] = note.metadata

                # Build markdown content with frontmatter
                lines = ["---"]
                yaml_content = yaml.dump(frontmatter, default_flow_style=False)
                lines.extend(yaml_content.strip().split("\n"))
                lines.append("---")
                lines.append("")
                lines.append(note.content)

                note_file.write_text("\n".join(lines))

            # Update cache
            if self._notes_cache is not None:
                self._notes_cache.append(note)
                self._notes_cache.sort(key=lambda n: n.created)
        else:
            # Legacy mode: in-memory
            if self._notes is not None:
                self._notes.append(note)

        return note

    def get_notes(
        self,
        note_type: Optional[NoteType] = None,
        author: Optional[str] = None,
        tag: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[Note]:
        """Get notes with optional filtering."""
        filtered_notes = self._load_notes().copy()

        # Filter by type
        if note_type:
            filtered_notes = [n for n in filtered_notes if n.note_type == note_type]

        # Filter by author
        if author:
            filtered_notes = [n for n in filtered_notes if n.author == author]

        # Filter by tag
        if tag:
            filtered_notes = [n for n in filtered_notes if n.has_tag(tag)]

        # Filter by date range
        if since:
            filtered_notes = [n for n in filtered_notes if n.created >= since]
        if until:
            filtered_notes = [n for n in filtered_notes if n.created <= until]

        # Sort chronologically (newest first)
        filtered_notes.sort(key=lambda n: n.created, reverse=True)

        # Apply limit
        if limit:
            filtered_notes = filtered_notes[:limit]

        return filtered_notes

    def search_notes(
        self,
        query: str,
        note_type: Optional[NoteType] = None,
        author: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Note]:
        """Search notes by content, tags, and metadata."""
        import logging

        logger = logging.getLogger(__name__)
        logger.debug(
            f"search_notes called with query='{query}' "
            f"(type: {type(query)}, len: {len(query) if query else 'None'})"
        )

        if not query or not query.strip():
            logger.debug("Query is empty, returning empty list")
            return []

        # Get base filtered notes
        filtered_notes = self.get_notes(note_type=note_type, author=author)
        logger.debug(f"Got {len(filtered_notes)} base notes to search")

        # Apply search filter
        matching_notes = [n for n in filtered_notes if n.matches_search(query)]
        logger.debug(f"Found {len(matching_notes)} matching notes")

        # Apply limit
        if limit:
            matching_notes = matching_notes[:limit]

        return matching_notes

    def get_note_by_id(self, note_id: str) -> Optional[Note]:
        """Get a specific note by ID."""
        for note in self._load_notes():
            if note.id == note_id:
                return note
        return None

    def remove_note(self, note_id: str) -> bool:
        """Remove a note by ID. Returns True if removed."""
        if self._filesystem_mode:
            if self.notes_dir:
                note_file = self.notes_dir / f"{note_id}.md"
                if note_file.exists():
                    note_file.unlink()
                    # Update cache
                    if self._notes_cache is not None:
                        self._notes_cache = [
                            n for n in self._notes_cache if n.id != note_id
                        ]
                    return True
            return False
        else:
            if self._notes is not None:
                for i, note in enumerate(self._notes):
                    if note.id == note_id:
                        del self._notes[i]
                        return True
            return False

    def get_note_count(self) -> int:
        """Get total number of notes."""
        return len(self._load_notes())

    def get_note_count_by_type(self) -> Dict[str, int]:
        """Get note counts by type."""
        counts: Dict[str, int] = {}
        for note in self._load_notes():
            note_type = note.note_type.value
            counts[note_type] = counts.get(note_type, 0) + 1
        return counts

    def get_recent_notes(self, limit: int = 10) -> List[Note]:
        """Get most recent notes."""
        return self.get_notes(limit=limit)

    def clear_notes(self) -> None:
        """Remove all notes."""
        if self._filesystem_mode:
            if self.notes_dir and self.notes_dir.exists():
                for note_file in self.notes_dir.glob("*.md"):
                    note_file.unlink()
            self._notes_cache = []
        else:
            if self._notes is not None:
                self._notes.clear()

    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert all notes to list of dictionaries."""
        return [note.to_dict() for note in self._load_notes()]

    def __len__(self) -> int:
        """Return number of notes."""
        return len(self._load_notes())

    def __iter__(self) -> Iterator[Note]:
        """Iterate over notes in chronological order (oldest first)."""
        return iter(sorted(self._load_notes(), key=lambda n: n.created))

    @classmethod
    def from_dict_list(cls, data: List[Dict[str, Any]]) -> "NoteManager":
        """Create note manager from list of dictionaries."""
        notes = [Note.from_dict(note_data) for note_data in data]
        return cls(notes=notes)

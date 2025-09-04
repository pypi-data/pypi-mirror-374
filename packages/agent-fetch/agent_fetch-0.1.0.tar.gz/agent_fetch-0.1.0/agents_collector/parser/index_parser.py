"""
Index file parser for agent-fetch.

Handles parsing, validation, and querying of index.yaml files containing
AGENTS.md file definitions and their source/target mappings.
"""

import pathlib
from typing import Dict, List, Optional, Any
import yaml
from rapidfuzz import fuzz, process
from dataclasses import dataclass


@dataclass
class IndexEntry:
    """Represents a single entry in the index.yaml file."""
    name: str
    source: str
    target: str

    def __str__(self) -> str:
        return f"{self.name} → {self.target}"

    def to_dict(self) -> Dict[str, str]:
        """Convert the entry to a dictionary."""
        return {
            "name": self.name,
            "source": self.source,
            "target": self.target,
        }


class IndexParser:
    """Parses and validates index.yaml files for the agent-fetch."""

    def __init__(self, search_choice_ratio: float = 75.0):
        """Initialize the index parser.

        Args:
            search_choice_ratio: Fuzzy matching threshold for search (0-100).
        """
        self.search_choice_ratio = search_choice_ratio

    def parse_index_file(self, file_path: pathlib.Path) -> List[IndexEntry]:
        """Parse an index.yaml file and return a list of validated entries.

        Args:
            file_path: Path to the index.yaml file.

        Returns:
            List of validated IndexEntry objects.

        Raises:
            FileNotFoundError: If the index file doesn't exist.
            yaml.YAMLError: If the YAML is malformed.
            ValueError: If the index structure is invalid.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Index file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if data is None:
                raise ValueError("Index file is empty or contains no data")

            return self._validate_and_parse_entries(data)

        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in index file {file_path}: {e}")

    def _validate_and_parse_entries(self, data: Dict[str, Any]) -> List[IndexEntry]:
        """Validate the parsed YAML data and convert to IndexEntry objects.

        Args:
            data: Parsed YAML data.

        Returns:
            List of IndexEntry objects.

        Raises:
            ValueError: If validation fails.
        """
        entries = []

        # Check if 'agents' key exists
        if "agents" not in data:
            raise ValueError("Index file must contain an 'agents' key at the root level")

        agents_data = data["agents"]
        if not isinstance(agents_data, list):
            raise ValueError("'agents' must be a list of entries")

        for i, entry_data in enumerate(agents_data):
            if not isinstance(entry_data, dict):
                raise ValueError(f"Entry {i} must be a dictionary")

            try:
                entry = self._parse_single_entry(entry_data)
                entries.append(entry)
            except ValueError as e:
                raise ValueError(f"Invalid entry {i}: {e}")

        if not entries:
            raise ValueError("Index file must contain at least one valid entry")

        return entries

    def _parse_single_entry(self, entry_data: Dict[str, Any]) -> IndexEntry:
        """Parse and validate a single entry from the index file.

        Args:
            entry_data: Dictionary representing a single entry.

        Returns:
            IndexEntry object.

        Raises:
            ValueError: If required fields are missing or invalid.
        """
        # Required fields
        name = entry_data.get("name")
        source = entry_data.get("source")
        target = entry_data.get("target")

        if not name:
            raise ValueError("Entry must have a 'name' field")
        if not source:
            raise ValueError("Entry must have a 'source' field")
        if not target:
            raise ValueError("Entry must have a 'target' field")

        # Validate field types
        if not isinstance(name, str):
            raise ValueError("'name' must be a string")
        if not isinstance(source, str):
            raise ValueError("'source' must be a string")
        if not isinstance(target, str):
            raise ValueError("'target' must be a string")

        # Validate source path (basic checks)
        source = source.strip()
        if not source:
            raise ValueError("'source' cannot be empty")
        if source.startswith("/") or ".." in source:
            raise ValueError("'source' must be a relative path within the repository")

        # Validate target path
        target = target.strip()
        if not target:
            raise ValueError("'target' cannot be empty")

        return IndexEntry(name=name, source=source, target=target)

    def find_entries_by_name(self,
                           entries: List[IndexEntry],
                           query: str,
                           limit: Optional[int] = None) -> List[IndexEntry]:
        """Find entries by name using fuzzy matching.

        Args:
            entries: List of entries to search.
            query: Search query string.
            limit: Maximum number of results to return.

        Returns:
            List of matching entries ordered by relevance.
        """
        if not entries:
            return []

        # Prepare data for fuzzy search
        names = [entry.name for entry in entries]
        query = query.lower().strip()

        # Use rapidfuzz for fuzzy matching
        matches = process.extract(
            query,
            names,
            scorer=fuzz.partial_ratio,
            score_cutoff=self.search_choice_ratio,
            limit=limit
        )

        # Convert back to IndexEntry objects
        result = []
        for match_name, score, index in matches:
            result.append(entries[index])

        return result

    def find_exact_entry_by_name(self, entries: List[IndexEntry], name: str) -> Optional[IndexEntry]:
        """Find an exact match by name (case-insensitive).

        Args:
            entries: List of entries to search.
            name: Exact name to match.

        Returns:
            Matching entry or None if not found.
        """
        name_lower = name.lower().strip()

        for entry in entries:
            if entry.name.lower() == name_lower:
                return entry

        return None

    def list_entries(self, entries: List[IndexEntry], format_output: bool = True) -> List[str]:
        """Get a formatted list of entries for display.

        Args:
            entries: List of entries to format.
            format_output: Whether to format with arrows for display.

        Returns:
            List of formatted strings.
        """
        if not entries:
            return ["No entries found"]

        if format_output:
            return [f"{entry.name} → {entry.target}" for entry in entries]
        else:
            return [entry.name for entry in entries]

    def validate_index_structure(self, file_path: pathlib.Path) -> bool:
        """Validate that an index file has the required structure.

        Args:
            file_path: Path to the index file.

        Returns:
            True if valid, False otherwise.
        """
        try:
            self.parse_index_file(file_path)
            return True
        except (FileNotFoundError, yaml.YAMLError, ValueError):
            return False

    def get_entry_names(self, entries: List[IndexEntry]) -> List[str]:
        """Get just the names from a list of entries.

        Args:
            entries: List of entries.

        Returns:
            List of entry names.
        """
        return [entry.name for entry in entries]

    def filter_entries_by_name_patterns(self,
                                       entries: List[IndexEntry],
                                       patterns: List[str]) -> List[IndexEntry]:
        """Filter entries by multiple name patterns using fuzzy matching.

        Args:
            entries: List of entries to filter.
            patterns: List of patterns to match against.

        Returns:
            Filtered list of entries.
        """
        if not patterns:
            return entries

        filtered = []
        for pattern in patterns:
            matches = self.find_entries_by_name(entries, pattern)
            for match in matches:
                if match not in filtered:
                    filtered.append(match)

        return filtered

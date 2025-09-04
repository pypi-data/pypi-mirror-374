"""
Index file parser module for agent-fetch.

This module handles parsing and validating index.yaml files that contain
the list of AGENTS.md files and their source/target mappings.
"""

from .index_parser import IndexParser

__all__ = ["IndexParser"]

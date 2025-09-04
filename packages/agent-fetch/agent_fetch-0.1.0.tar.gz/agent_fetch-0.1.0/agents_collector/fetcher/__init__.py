"""
File fetcher module for agent-fetch.

This module handles fetching AGENTS.md files and other markdown documentation
from GitHub repositories using their raw file endpoints.
"""

from .github_fetcher import GitHubFetcher

__all__ = ["GitHubFetcher"]

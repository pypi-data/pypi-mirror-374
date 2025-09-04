"""
agent-fetch - A Python command-line tool for fetching AGENTS.md files from GitHub repositories.

This package provides a modular, extensible CLI tool designed for collecting documentation
files from GitHub repositories with interactive selection and automation capabilities.
"""

__version__ = "0.1.0"
__author__ = "FreeMarketamilitia"

# Package metadata
__title__ = "agent-fetch"
__description__ = "CLI tool for fetching AGENTS.md files from GitHub"
__url__ = "https://github.com/FreeMarketamilitia/agent-fetch"

from .cli import app

__all__ = ["app"]

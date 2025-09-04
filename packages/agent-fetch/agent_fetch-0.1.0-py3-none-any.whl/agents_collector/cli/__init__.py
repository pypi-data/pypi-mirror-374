"""
CLI interface module for agent-fetch.

This module provides the command-line interface using Typer,
implementing all the commands and flags specified in the PRD.
"""

from .cli_main import app

__all__ = ["app"]

"""
Main CLI module for agent-fetch.

Implements the command-line interface using Typer, providing all the
functionality specified in the PRD including interactive mode and various flags.
"""

import pathlib
import sys
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import typer

from ..config import ConfigManager
from ..fetcher import GitHubFetcher
from ..parser import IndexParser
from ..ui import InteractiveSelector

# Typer app
app = typer.Typer(no_args_is_help=True)
console = Console()


@app.callback()
def callback():
    """agent-fetch - Fetch AGENTS.md files from GitHub repositories.

    Run without arguments to enter interactive mode.
    """
    pass


def _get_repo_and_index(repo_url: Optional[str] = None,
                       branch: Optional[str] = None) -> tuple:
    """Get repository URL and index file path.

    Args:
        repo_url: Repository URL override
        branch: Branch name override

    Returns:
        Tuple of (repo_url, index_path, branch)
    """
    config = ConfigManager()

    # Handle case where repo_url might be a Typer object
    if repo_url and hasattr(repo_url, '__class__') and 'OptionInfo' in str(repo_url.__class__):
        repo_url = None

    # Use provided repo or get from config
    final_repo_url = repo_url or config.get_default_repo()
    if not final_repo_url:
        console.print("[red]Error:[/red] No repository URL specified. Use --repo or set default with 'agentscli set-repo <url>'")
        raise typer.Exit(1)

    # Use provided branch or get from config
    final_branch = branch or config.get_default_branch()

    # Build index.yaml path in the repository
    fetcher = GitHubFetcher()
    index_path = "index.yaml"  # Default index file path

    return final_repo_url, index_path, final_branch


def _fetch_index_entries(repo_url: str, index_path: str, branch: str) -> List:
    """Fetch and parse index.yaml entries.

    Args:
        repo_url: Repository URL
        index_path: Path to index file in repo
        branch: Branch name

    Returns:
        List of index entries
    """
    fetcher = GitHubFetcher()

    try:
        # Build URL for index.yaml
        index_url = fetcher.build_raw_url(repo_url, index_path, branch)

        # Create temporary file to store index.yaml
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.yaml', delete=False) as temp_file:
            temp_path = pathlib.Path(temp_file.name)

        # Fetch index file
        fetcher.fetch_file(index_url, temp_path)

        # Parse the index file
        parser = IndexParser()
        entries = parser.parse_index_file(temp_path)
        temp_path.unlink()  # Clean up temp file

        return entries

    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to load index.yaml: {e}")
        raise typer.Exit(1)


def _perform_fetch(repo_url: str,
                   entries: List,
                   branch: str,
                   overwrite: bool = True) -> dict:
    """Perform the actual file fetching.

    Args:
        repo_url: Repository URL
        entries: List of entries to fetch
        branch: Branch name
        overwrite: Whether to overwrite existing files

    Returns:
        Dictionary of fetch results
    """
    fetcher = GitHubFetcher()
    entry_dicts = [entry.to_dict() for entry in entries]

    with console.status("[bold green]Fetching files...[/bold green]") as status:
        results = fetcher.fetch_files_from_index(repo_url, entry_dicts, branch, overwrite)

    return results


def _display_results(results: dict) -> None:
    """Display fetch results in a nice table.

    Args:
        results: Dictionary mapping entry names to success status
    """
    table = Table(title="Fetch Results")
    table.add_column("File", style="cyan", min_width=30)
    table.add_column("Status", justify="center", min_width=15)

    success_count = 0
    for name, success in results.items():
        status = "[green]✓ Success[/green]" if success else "[red]✗ Failed[/red]"
        table.add_row(name, status)
        if success:
            success_count += 1

    console.print(table)
    console.print(f"\n[bold]Summary:[/bold] {success_count}/{len(results)} files fetched successfully")


@app.command()
def main(all: bool = typer.Option(False, "--all", help="Fetch all files defined in index.yaml"),
         name: Optional[str] = typer.Option(None, "--name", help="Fetch one file by name (supports fuzzy matching)"),
         repo: Optional[str] = typer.Option(None, "--repo", help="Fetch from alternate repository URL"),
         branch: Optional[str] = typer.Option(None, "--branch", help="Fetch from specific branch"),
         no_overwrite: bool = typer.Option(False, "--no-overwrite", help="Skip existing files instead of overwriting")):
    """Run interactive mode or fetch files based on flags."""

    # Get repository and branch
    repo_url, index_path, final_branch = _get_repo_and_index(repo, branch)

    # Fetch index entries
    entries = _fetch_index_entries(repo_url, index_path, final_branch)

    # Filter entries based on flags
    selected_entries = entries
    parser = IndexParser()

    if name:
        # Find entries by name (fuzzy matching)
        matches = parser.find_entries_by_name(entries, name)
        if not matches:
            console.print(f"[yellow]No files found matching '{name}'[/yellow]")
            raise typer.Exit(0)
        selected_entries = matches

    elif not all:
        # Interactive selection
        try:
            selector = InteractiveSelector()
            selected_entries = selector.select_from_entries(entries)

            if not selected_entries:
                console.print("[yellow]No files selected[/yellow]")
                return
        except Exception as e:
            # Fallback to non-interactive mode if interactive fails
            console.print("[yellow]Interactive selection failed, falling back to fetching first file only[/yellow]")
            console.print(f"[dim]Error: {e}[/dim]")
            if entries:
                selected_entries = [entries[0]]  # Fetch first file only
                console.print(f"[green]Will fetch: {entries[0].name}[/green]")
            else:
                console.print("[yellow]No files to fetch[/yellow]")
                return

    # Perform the fetch
    overwrite = not no_overwrite
    results = _perform_fetch(repo_url, selected_entries, final_branch, overwrite)
    _display_results(results)


@app.command()
def list(repo: Optional[str] = typer.Option(None, "--repo", help="Repository URL to list from"),
         branch: Optional[str] = typer.Option(None, "--branch", help="Branch to list from")):
    """Print out entries in index.yaml (non-interactive)."""

    repo_url, index_path, final_branch = _get_repo_and_index(repo, branch)
    entries = _fetch_index_entries(repo_url, index_path, final_branch)

    if not entries:
        console.print("[yellow]No entries found in index.yaml[/yellow]")
        return

    table = Table("Name", "Source", "Target")
    for entry in entries:
        table.add_row(entry.name, entry.source, entry.target)

    console.print(table)


@app.command()
def validate(repo: Optional[str] = typer.Option(None, "--repo", help="Repository URL to validate"),
            branch: Optional[str] = typer.Option(None, "--branch", help="Branch to validate")):
    """Check that index.yaml exists and is well-formed."""

    try:
        repo_url, index_path, final_branch = _get_repo_and_index(repo, branch)

        fetcher = GitHubFetcher()

        # Test if index.yaml exists
        index_url = fetcher.build_raw_url(repo_url, index_path, final_branch)
        console.print(f"[bold]Validating index.yaml from {repo_url}[/bold]")

        # Test connection
        if not fetcher.test_connection(repo_url, index_path, final_branch):
            console.print("[red]✗ Validation failed: Cannot access index.yaml[/red}")
            raise typer.Exit(1)

        # Try to fetch and parse
        entries = _fetch_index_entries(repo_url, index_path, final_branch)

        console.print(f"[green]✓ Validation successful![/green]")
        console.print(f"Found {len(entries)} entries in index.yaml")

    except Exception as e:
        console.print(f"[red]✗ Validation failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def set_repo(url: str = typer.Argument(..., help="Repository URL to set as default")):
    """Set the global default repository URL."""

    # Validate the URL format
    fetcher = GitHubFetcher()
    if not fetcher.validate_repo_url(url):
        console.print("[red]Error:[/red] Invalid GitHub repository URL format")
        raise typer.Exit(1)

    config = ConfigManager()
    config.set_default_repo(url)

    console.print(f"[green]✓ Default repository set to:[/green] {url}")


@app.command()
def show_repo():
    """Show the current default repository configuration."""

    config = ConfigManager()

    repo = config.get_default_repo()
    branch = config.get_default_branch()

    if not repo:
        console.print("[yellow]No default repository configured[/yellow]")
        console.print("Use [bold]agentscli set-repo <url>[/bold] to set one")
        return

    table = Table("Setting", "Value")
    table.add_row("Repository", repo)
    table.add_row("Branch", branch)

    console.print(table)


if __name__ == "__main__":
    app()

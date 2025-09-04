"""
Interactive selector for agent-fetch.

Provides beautiful, colorful interactive menus using questionary
for file selection with arrow key navigation, fuzzy search, and multi-select.
"""

from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Confirm, Prompt
from questionary import Style, Choice
import questionary

from ..parser.index_parser import IndexEntry


class InteractiveSelector:
    """Handles interactive file selection with beautiful UI."""

    def __init__(self):
        """Initialize the interactive selector."""
        self.console = Console()

        # Custom questionary style for beautiful UI
        self.style = Style([
            ("qmark", "fg:#9944FF bold"),  # Purple question mark
            ("question", "bold"),  # Bold questions
            ("answer", "fg:#00AA00 bold"),  # Green answers
            ("pointer", "fg:#FF4400 bold"),  # Orange pointer
            ("highlighted", "fg:#9944FF bold"),  # Purple highlighted text
            ("selected", "fg:#00AA00 bold"),  # Green selected items
            ("separator", "fg:#9944FF"),  # Purple separators
            ("instruction", "fg:#666666"),  # Gray instructions
            ("text", ""),  # Default text
        ])

    def _create_choices_from_entries(self, entries: List[IndexEntry]) -> List[Choice]:
        """Create questionary choices from index entries.

        Args:
            entries: List of index entries to convert to choices

        Returns:
            List of questionary Choice objects
        """
        choices = []

        for i, entry in enumerate(entries):
            # Format: "Name → downloads/target.md"
            choice_text = f"{entry.name} → {entry.target}"

            # Create choice with name as value and formatted text as title
            choice = Choice(
                title=choice_text,
                value=i,  # Use index so we can map back to the original entry
                disabled=False
            )
            choices.append(choice)

        return choices

    def select_from_entries(self, entries: List[IndexEntry]) -> List[IndexEntry]:
        """Present an interactive menu for selecting entries.

        Args:
            entries: List of entries to choose from

        Returns:
            List of selected entries
        """
        if not entries:
            self.console.print("[yellow]No files available in index.yaml[/yellow]")
            return []

        if len(entries) == 1:
            # If only one file, ask if user wants to fetch it
            entry = entries[0]
            self.console.print(f"[bold]Only one file available:[/bold]")
            self.console.print(f"{entry.name} → {entry.target}")

            fetch_single = Confirm.ask(
                "Fetch this file?",
                default=True,
                console=self.console
            )

            return [entry] if fetch_single else []

        # Create choices for multi-select
        choices = self._create_choices_from_entries(entries)

        # Display header with clear instructions
        self.console.print(f"[bold green]📁 Available AGENTS.md files:[/bold green]")
        self.console.print("[dim]─" * 60 + "[/dim]")
        self.console.print()

        # Show choice list first
        for i, choice in enumerate(choices, 1):
            self.console.print(f"  {i}. {choice.title}")

        self.console.print()

        # Display instructions prominently
        self.console.print("[bold cyan]🎯 HOW TO SELECT FILES[/bold cyan]")
        self.console.print("┌─────────────────────────────────────────────────┐")
        self.console.print("│ 1. Use ↑↓ arrows to navigate between files       │")
        self.console.print("│ 2. Press SPACEBAR to select/deselect each file   │")
        self.console.print("│    ✓ = selected | ○ = not selected              │")
        self.console.print("│ 3. Press ENTER to download selected files        │")
        self.console.print("└─────────────────────────────────────────────────┘")
        self.console.print()

        # Present the multi-select menu with very clear prompt
        try:
            self.console.print("[bold yellow]Navigate with ↑↓, select with SPACEBAR, confirm with ENTER[/bold yellow]")

            selected_indices = questionary.checkbox(
                "Which files would you like to download?",
                choices=choices,
                style=self.style,
                qmark="❯",
                pointer="▶",
                instruction="↑↓ to move, SPACEBAR to select/unselect, ENTER to download selected files",
            ).ask()

            # Debug output
            self.console.print(f"[dim]Debug: Selected indices: {selected_indices}[/dim]")

            # Handle exit/cancel
            if selected_indices is None or len(selected_indices) == 0:
                self.console.print("[yellow]No files selected or selection cancelled[/yellow]")
                return []

        except KeyboardInterrupt:
            self.console.print("[yellow]Selection cancelled with Ctrl+C[/yellow]")
            return []
        except Exception as e:
            self.console.print(f"[red]Error during selection: {e}[/red]")
            # Try alternative method
            return self._fallback_selection(entries)

        # Map selected indices back to entries
        selected_entries = [entries[i] for i in selected_indices]

        if not selected_entries:
            self.console.print("[yellow]No files selected[/yellow]")
            return []

        # Show summary of selection
        self._display_selection_summary(selected_entries)
        return selected_entries

    def _display_selection_summary(self, selected_entries: List[IndexEntry]) -> None:
        """Display a summary of selected files.

        Args:
            selected_entries: List of selected entries
        """
        if not selected_entries:
            return

        self.console.print(f"\n[bold green]✓ Selected {len(selected_entries)} file(s):[/bold green]")

        table = Table(show_header=False, padding=(0, 2))
        table.add_column("", style="cyan")
        table.add_column("", style="dim cyan")

        for entry in selected_entries:
            short_source = entry.source.replace("AGENTS.md", "").rstrip("/")
            table.add_row(
                f"• {entry.name}",
                f"{short_source} → {entry.target}"
            )

        self.console.print(table)

        # Confirm action
        confirmed = Confirm.ask(
            f"Fetch {len(selected_entries)} file(s)?",
            default=True,
            console=self.console
        )

        if not confirmed:
            self.console.print("[yellow]Fetch cancelled[/yellow]")

        self.console.print()  # Add spacing

    def show_welcome_message(self, repo_url: str, entry_count: int) -> None:
        """Show a welcome message with repository info.

        Args:
            repo_url: Repository URL
            entry_count: Number of entries in index
        """
        repo_name = self._extract_repo_name(repo_url)

        welcome_panel = Panel(
            f"🚀 [bold magenta]Welcome to agent-fetch![/bold magenta]\n\n"
            f"📂 Repository: [cyan]{repo_name}[/cyan]\n"
            f"📄 Available files: [green]{entry_count}[/green]\n\n"
            f"[dim]Use arrow keys to navigate, space to select, enter to confirm[/dim]",
            title="[bold blue]🎯 Interactive Mode[/bold blue]",
            border_style="blue"
        )

        self.console.print(welcome_panel)
        self.console.print()

    def _extract_repo_name(self, repo_url: str) -> str:
        """Extract repository name from URL.

        Args:
            repo_url: Repository URL

        Returns:
            Short repository name
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(repo_url)
            path_parts = parsed.path.strip("/").split("/")

            if len(path_parts) >= 2:
                owner, repo = path_parts[0], path_parts[1]
                return f"{owner}/{repo}"
            else:
                return repo_url  # Fallback to full URL
        except:
            return repo_url  # Fallback

    def show_no_entries_message(self) -> None:
        """Show message when no entries are available."""
        panel = Panel(
            "📭 [yellow]No files found in index.yaml[/yellow]\n\n"
            "Please check that:\n"
            "• The repository contains an index.yaml file\n"
            "• The index.yaml has valid entries\n"
            "• The repository URL is correct",
            title="[bold yellow]⚠️ No Files Available[/bold yellow]",
            border_style="yellow"
        )
        self.console.print(panel)

    def show_error_message(self, error: str, details: str = None) -> None:
        """Show error message with optional details.

        Args:
            error: Main error message
            details: Optional detailed information
        """
        panel_content = f"❌ [red]{error}[/red]"
        if details:
            panel_content += f"\n\n[dim]{details}[/dim]"

        panel = Panel(
            panel_content,
            title="[bold red]💥 Error[/bold red]",
            border_style="red"
        )
        self.console.print(panel)

    def ask_confirmation(self, message: str, default: bool = True) -> bool:
        """Ask for user confirmation.

        Args:
            message: Confirmation message
            default: Default value

        Returns:
            User's choice
        """
        return Confirm.ask(message, default=default, console=self.console)

    def _fallback_selection(self, entries: List[IndexEntry]) -> List[IndexEntry]:
        """Fallback selection method using numeric input when questionary fails.

        Args:
            entries: List of entries to choose from

        Returns:
            List of selected entries
        """
        self.console.print("[yellow]🔄 Using fallback selection method[/yellow]")

        # Display numbered list
        self.console.print("[bold cyan]Available files:[/bold cyan]")
        for i, entry in enumerate(entries, 1):
            self.console.print(f"  {i}. {entry.name} → {entry.target}")

        # Get user input
        try:
            selection = Prompt.ask(
                "\nEnter file numbers to download (comma-separated, e.g., '1,3' or 'all')",
                default="all",
                console=self.console
            )

            if selection.lower() == "all":
                selected_entries = entries[:]
            else:
                indices = []
                for part in selection.split(","):
                    try:
                        idx = int(part.strip()) - 1  # Convert to 0-based index
                        if 0 <= idx < len(entries):
                            indices.append(idx)
                        else:
                            self.console.print(f"[red]Invalid number: {part.strip()}[/red]")
                    except ValueError:
                        self.console.print(f"[red]Not a number: {part.strip()}[/red]")

                selected_entries = [entries[i] for i in indices]

            if selected_entries:
                return selected_entries
            else:
                self.console.print("[yellow]No valid selections made[/yellow]")
                return []

        except Exception as e:
            self.console.print(f"[red]Error in selection: {e}[/red]")
            return []

# agent-fetch

A Python command-line tool for fetching `AGENTS.md` files (or other markdown/docs) from GitHub repositories.

## 🚀 Features

- **Interactive-first**: Default command triggers beautiful interactive file selection
- **Flexible Automation**: Flags let advanced users skip interaction with `--all`, `--name`, or `--repo`
- **Configurable Defaults**: Global default repo stored in config with branch overrides
- **Beautiful UI**: Colorful menus with arrow key navigation and fuzzy search using `questionary`
- **Cross-platform**: Works on Linux, macOS, and Windows

## 📦 Installation

```bash
# Option 1: Traditional pip installation
pip install -e .

# Option 2: Modern uv installation (recommended)
uv pip install -e .
```

## 🎯 Quick Start

### Default Setup (No Configuration Required)
The tool comes with a pre-configured default repository and works immediately:

```bash
# Interactive mode (with default repo)
agentfetch
```

### Change Default Repository (Optional)
If you want to use a different repository:

```bash
agentfetch set-repo https://github.com/your-org/docs
```

### Quick Usage Examples

```bash
# Interactive mode (default)
agentfetch

# Fetch all files from default repo
agentfetch main --all

# Search for specific files
agentfetch main --name "api"  # Fuzzy matching

# Use different repository
agentfetch main --all --repo https://github.com/org/docs
```

### Expected Interactive Output
```
📁 Files in index.yaml
Select files to fetch using ↑/↓ arrows, space to select, enter to confirm

❯ Python APIs Guide
  Shadcn UI Components Guide
  Next.js App APIs Guide
```

## 📋 Commands

| Command | Description |
|---------|-------------|
| `agentfetch` | Interactive mode (default) |
| `agentfetch --all` | Fetch all files |
| `agentfetch --name <query>` | Fetch by name (fuzzy matching) |
| `agentfetch --repo <url>` | Fetch from alternate repo |
| `agentfetch --branch <branch>` | Fetch from specific branch |
| `agentfetch --no-overwrite` | Skip existing files |
| `agentfetch set-repo <url>` | Set global default repo |
| `agentfetch show-repo` | Display current config |
| `agentfetch list` | List files in index.yaml |
| `agentfetch validate` | Validate index.yaml |

## 🔧 Configuration

Configuration is stored in:
- **Linux/macOS**: `~/.agentfetch/config.yaml`
- **Windows**: `%APPDATA%\agentfetch\config.yaml`

Example config:
```yaml
default_repo: "https://github.com/org/agents"
default_branch: "main"
```

## 📁 Index File Specification

The tool expects an `index.yaml` file in the repository root with this structure:

```yaml
agents:
  - name: "Root Guide"           # Human-readable name
    source: "AGENTS.md"          # Repo-relative path
    target: "downloads/root.md"  # Local destination

  - name: "API Guide"
    source: "services/api/AGENTS.md"
    target: "downloads/api.md"
```

## 🔍 Example Workflows

### Standard Development Workflow
```bash
# Set up default repository
agentfetch set-repo https://github.com/your-org/docs

# Interactive selection for daily use
agentfetch

# Automate fetching all docs
agentfetch --all

# Fetch specific documentation
agentfetch --name "user guide"
```

### CI/CD Integration
```bash
# Non-interactive batch operation
agentfetch --all --repo https://github.com/org/docs --branch main
```

### Multi-Repository Setup
```bash
# Fetch from monorepo
agentfetch --repo https://github.com/org/monorepo

# Fetch from specific branch
agentfetch --repo https://github.com/org/monorepo --branch feature/new-docs
```

## 🛠️ Development

This tool is modular and easily extensible, following Python best practices with:

- **OOP Design**: Clean class-based architecture
- **Separation of Concerns**: Config, fetching, parsing, and UI as separate modules
- **Robust Error Handling**: Comprehensive error handling throughout
- **Rich UI**: Beautiful, colorful console output with Rich

### Project Structure
```
agents_collector/
├── config/              # Configuration management
├── fetcher/             # GitHub fetching logic
├── parser/              # Index file parsing
├── cli/                 # Command-line interface
├── ui/                  # Interactive UI components
└── __init__.py
```

### Dependencies
- `typer`: CLI framework
- `pyyaml`: YAML parsing
- `requests`: HTTP client
- `questionary`: Interactive menus
- `rapidfuzz`: Fuzzy matching
- `rich`: Beautiful console output

## 🤝 Contributing

The tool follows a modular architecture that makes it easy to:
- Add new fetcher backends (GitLab, local files, etc.)
- Extend interactive selection features
- Add new CLI commands
- Support additional index file formats

## 📄 License

MIT License

---

## 🎉 Why agent-fetch?

This tool makes it simple to **collect, organize, and update** `AGENTS.md` files across monorepos or multiple projects, ensuring consistency for both developers and coding agents.

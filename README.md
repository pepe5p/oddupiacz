# Oddupiacz

A global pre-commit hook to check for forbidden words in git changes.

## Features

- 🚫 Block commits containing forbidden phrases
- 🌍 Works globally across all your Git repositories
- ⚙️ User-friendly configuration with YAML
- 🎨 Clean CLI powered by Typer
- 🔧 Customizable forbidden phrase list
- 🔗 Chain with local pre-commit hooks

## Installation

### Prerequisites

- Python 3.13+
- Git
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Quick Install with uv (Recommended)

[uv](https://docs.astral.sh/uv/) is a fast Python package manager. If you don't have it installed:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/oddupiacz.git
cd oddupiacz

# Sync dependencies (uv will automatically create a virtual environment)
uv sync

# Install the global pre-commit hook
./install
```

### Alternative: Install with pip

```bash
# Clone the repository
git clone https://github.com/yourusername/oddupiacz.git
cd oddupiacz

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install pyyaml typer

# Install the global pre-commit hook
python -m oddupiacz.cli_setup install
```


## Configuration

Create a `config.yaml` file with your forbidden phrases:

```yaml
forbidden_phrases:
  - "temp_fix"
  - "TODO"
  - "FIXME"
  - "console.log"
  - "debugger"
```

See `configs/sample_config.yaml` for an example.

## Usage

Once installed, Oddupiacz runs automatically on every commit. If forbidden phrases are detected, the commit will be blocked:

```bash
$ git commit -m "Add feature"
[BLOCKED] Forbidden phrase found: 'console.log'
  File: src/app.js
  Line: console.log("debug");
----------------------------------------
Commit aborted.
```

### Manual Checking

You can also manually check changes:

```bash
# Check staged changes
git diff --cached --unified=0 --no-color | python -m oddupiacz.cli_hook

# Use a custom config
git diff --cached --unified=0 --no-color | python -m oddupiacz.cli_hook --config myconfig.yaml
```

## How It Works

1. **Setup generates a shim**: The installation creates a shell script at `~/.githooks_global/pre-commit`
2. **Shim runs git diff**: The shim executes `git diff --cached` and pipes the output
3. **Python script checks diff**: The cli_hook script reads from stdin and searches for forbidden phrases
4. **Local hooks chain**: After checking, it runs any local pre-commit hooks in your repository

### Architecture

```
┌─────────────────────┐
│   Git Commit        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Global Pre-commit  │ (shim at ~/.githooks_global/pre-commit)
│  git diff | python  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  cli_hook.py        │ (reads from stdin)
│  Check phrases      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Local Pre-commit   │ (if exists)
└─────────────────────┘
```

## Uninstallation

To remove Oddupiacz:

```bash
./uninstall
```

This will:
- Remove the global pre-commit hook
- Reset Git's `core.hooksPath` configuration

## Development

### Project Structure

The codebase is organized into modular, testable components:

```
oddupiacz/
├── __init__.py          # Package exports
├── checker.py           # Core diff parsing and violation detection logic
├── config.py            # Configuration file loading and management
├── git_utils.py         # Git command utilities
├── installer.py         # Hook installation/uninstallation logic
├── cli_hook.py          # CLI for pre-commit hook (runs on each commit)
├── cli_setup.py         # CLI for installation/uninstallation
└── shim.py              # Shim template

tests/
├── test_checker.py      # Tests for checker.py
├── test_config.py       # Tests for config.py
└── test_installer.py    # Tests for installer.py
```

**Design Principles:**
- **Pure functions**: Core logic separated from I/O for testability
- **Modular structure**: Each file has a single responsibility
- **CLI separation**: Typer CLIs are thin wrappers around pure functions
- **Test coverage**: Each module has corresponding tests (except git_utils which requires integration testing)

### Setup Development Environment

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and sync dependencies
git clone https://github.com/yourusername/oddupiacz.git
cd oddupiacz
uv sync
```

### Running Tests

```bash
# With uv (recommended)
uv run pytest tests/

# Or activate the virtual environment
source .venv/bin/activate
pytest tests/
```

### Code Style

The project uses Ruff for linting and formatting:

```bash
# With uv
uv run ruff check .
uv run ruff format .

# Or in activated venv
ruff check .
ruff format .
```

## License

[Add your license here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


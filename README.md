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

I recommend using [uv](https://docs.astral.sh/uv/) to set up a virtual environment, but you can safely use any other tool of your choice.
The only real requirement is that you must pass Python interpreter path to the `./install` script.
It will be called every time you commit.

## Configuration

Run `./install`. Interactive prompts will guide you through setting up your configuration.

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

### Setup Development Environment

```bash
git clone https://github.com/yourusername/oddupiacz.git
cd oddupiacz
uv sync
```

### Running Tests

```bash
just test
```

### Code Style

The project uses Ruff for linting and formatting, all linters can be run with `just`:

```bash
just lint_full
just lint_full_ff  # (fast-fail mode)
just all  # (lint + tests)
just all_ff  # (lint + tests in fast-fail mode)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


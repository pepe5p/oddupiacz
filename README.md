# Oddupiacz

A global pre-commit hook to check for forbidden words in git changes.

## Prerequisites

This project uses [just](https://github.com/casey/just) as a command runner. You'll need to install it first. If you don't want to install `just`, you can manually run commands from `justfile` instead.

```bash
cat justfile
```

## Installation

```bash
# Install the hook
just install

# Configure forbidden words
just edit_config
```

This will:
1. Create `~/.githooks/` directory and set it as your global hooks path
2. Install the pre-commit hook
3. Prompt you to enter forbidden words (space-separated)

## Uninstallation

```bash
just uninstall
```

This will remove the pre-commit hook and configuration file.

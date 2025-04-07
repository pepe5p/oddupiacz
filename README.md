# Oddupiacz

Oddupiacz is a global pre-commit hook to check for forbidden word "dupa" in file names and contents

## Usage

1. Create `~/.githooks/` catalog if you haven't already.

```bash
mkdir ~/.githooks
```

2. Add `~/.githooks` to your git configuration. This will set the global hooks path to `~/.githooks`.

```bash
git config --global core.hooksPath ~/.githooks
```

3. Copy the `oddupiacz` script to `~/.githooks/pre-commit`. Make sure not to overwrite any existing pre-commit hook.

```bash
cp oddupiacz ~/.githooks/pre-commit
```

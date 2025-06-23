install: _ensure_git_hooks
    cp oddupiacz.sh ~/.githooks/pre-commit
    chmod +x ~/.githooks/pre-commit

edit_config:
    #!/bin/sh
    echo "Enter forbidden words (space-separated):"
    read words
    echo "$words" > ~/.githooks/oddupiacz.conf
    echo "Forbidden words saved to ~/.githooks/oddupiacz.conf"

uninstall:
    rm ~/.githooks/pre-commit
    rm ~/.githooks/oddupiacz.conf

_ensure_git_hooks:
    mkdir -pv ~/.githooks
    git config --global core.hooksPath ~/.githooks


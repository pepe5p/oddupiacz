install: _ensure_git_hooks
    cp oddupiacz.sh $HOME/.githooks/pre-commit
    chmod +x $HOME/.githooks/pre-commit

edit_config:
    #!/bin/sh
    echo "Enter forbidden words (space-separated):"
    read words
    echo "$words" > $HOME/.githooks/oddupiacz.conf
    echo "Forbidden words saved to $HOME/.githooks/oddupiacz.conf"

uninstall:
    rm $HOME/.githooks/pre-commit
    rm $HOME/.githooks/oddupiacz.conf

watch:
	watchexec -w oddupiacz.sh just install

_ensure_git_hooks:
    mkdir -pv $HOME/.githooks
    git config --global core.hooksPath $HOME/.githooks

_test:
    ./tests/test_oddupiacz.sh

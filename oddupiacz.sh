#!/bin/sh

CONFIG_FILE="$HOME/.githooks/oddupiacz.conf"
if [ -f "$CONFIG_FILE" ]; then
    FORBIDDEN_WORDS=$(cat "$CONFIG_FILE")
else
    FORBIDDEN_WORDS="dupa"
fi

GREP_PATTERN=$(echo "$FORBIDDEN_WORDS" | sed 's/ /|/g')

filename_matches=$(git diff --cached --name-status | grep -i -E "$GREP_PATTERN")
content_matches=$(git diff --cached | grep -i -E "$GREP_PATTERN")

if [ -n "$filename_matches" ] || [ -n "$content_matches" ]; then
    if [ -n "$filename_matches" ]; then
        echo "Found forbidden words in file names:"
        echo ""
        echo "$filename_matches" | sed 's/^/    /'
        echo ""
    fi
    if [ -n "$content_matches" ]; then
        echo "Found forbidden words in staged diff content:"
        echo ""
        echo "$content_matches" | sed 's/^/    /'
        echo ""
    fi
    echo "Aborting commit due to \`oddupiacz\`."
    exit 1
fi

echo "\`oddupiacz\` finished successfully."
exit 0

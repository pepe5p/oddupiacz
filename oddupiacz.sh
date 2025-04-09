#!/bin/sh
# Global pre-commit hook to check for forbidden word "dupa" in git diff (staged changes)

echo "Oddupianie..."

filename_matches=$(git diff --cached --name-only | grep "dupa")
content_matches=$(git diff --cached | grep -n "dupa")

if [ -n "$filename_matches" ] || [ -n "$content_matches" ]; then
    echo "Error: dupa found in staged changes."
    if [ -n "$filename_matches" ]; then
        echo "In file names:"
        echo "$filename_matches"
    fi
    if [ -n "$content_matches" ]; then
        echo "In staged diff content:"
        echo "$content_matches"
    fi
    exit 1
fi

echo "Oddupianie finished"

exit 0

#!/bin/sh
# Global pre-commit hook to check for forbidden word "dupa" in file names and contents

echo "Running oddupiacz for file names and contents..."

# Search for "dupa" in file names (excluding .git directory)
filename_matches=$(find . -type f -name "*dupa*" -not -path "./.git/*")

# Search for "dupa" in file contents (excluding .git directory)
content_matches=$(grep -R --exclude-dir=".git" --line-number "dupa" .)

# If either check finds matches, output the details and abort the commit.
if [ -n "$filename_matches" ] || [ -n "$content_matches" ]; then
    echo "Error: Forbidden word 'dupa' found."
    if [ -n "$filename_matches" ]; then
        echo "In file names:"
        echo "$filename_matches"
    fi
    if [ -n "$content_matches" ]; then
        echo "In file contents:"
        echo "$content_matches"
    fi
    exit 1
fi

exit 0


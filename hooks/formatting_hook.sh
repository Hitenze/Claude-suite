#!/bin/bash
# Claude Code Hook wrapper for formatting.sh
# Reads JSON from stdin and extracts file paths

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Read JSON from stdin
if [ -t 0 ]; then
    # No stdin data, check environment variable
    if [ -n "$CLAUDE_FILE_PATHS" ]; then
        exec "$SCRIPT_DIR/formatting.sh"
    else
        echo "No files to format" >&2
        exit 0
    fi
else
    # Read JSON from stdin
    json_data=$(cat)
    
    # Extract file path using jq (or simple grep if jq not available)
    if command -v jq >/dev/null 2>&1; then
        file_path=$(echo "$json_data" | jq -r '.tool_input.file_path // empty')
    else
        # Fallback: simple extraction
        file_path=$(echo "$json_data" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
    fi
    
    if [ -n "$file_path" ]; then
        # Set environment variable and run formatting script
        export CLAUDE_FILE_PATHS="$file_path"
        exec "$SCRIPT_DIR/formatting.sh"
    else
        echo "No file path found in JSON" >&2
        exit 0
    fi
fi
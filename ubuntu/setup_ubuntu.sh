#!/bin/bash
# Setup script for Claude Code Hooks on Ubuntu/Linux

set -e

echo "==================================="
echo "Claude Code Hooks Setup for Ubuntu"
echo "==================================="

# Get the repository root directory (parent of script directory)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
HOOKS_DIR="$REPO_ROOT/hooks"

# Check if hooks directory exists
if [ ! -d "$HOOKS_DIR" ]; then
    echo "Error: hooks directory not found at $HOOKS_DIR"
    echo "Please ensure you're running this script from the CLAUDE repository"
    exit 1
fi

# Make scripts executable
echo "Setting permissions..."
chmod +x "$HOOKS_DIR"/*.py
chmod +x "$HOOKS_DIR"/*.sh

# Create Claude settings directory
echo "Creating Claude settings directory..."
mkdir -p ~/.claude

# Check if settings.json exists
if [ -f ~/.claude/settings.json ]; then
    echo ""
    echo "WARNING: ~/.claude/settings.json already exists!"
    echo "Please manually add the hooks configuration from the README.md"
    echo ""
else
    # Create settings.json with proper configuration
    echo "Creating settings.json..."
    cat > ~/.claude/settings.json << 'EOF'
{
  "model": "opus",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "CHECK_MODE=comments $HOOKS_DIR/check_chinese_hook.py"
          }
        ]
      },
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "$HOOKS_DIR/filename_ban_hook.py"
          }
        ]
      },
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "$HOOKS_DIR/no_show_in_python_hook.py"
          }
        ]
      },
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "$HOOKS_DIR/protect_phase_file.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "$HOOKS_DIR/formatting_hook.sh"
          }
        ]
      }
    ]
  }
}
EOF
    
    # Replace variables with actual paths
    sed -i "s|\$HOOKS_DIR|$HOOKS_DIR|g" ~/.claude/settings.json
    echo "Success: Settings file created successfully!"
fi

# Check for optional formatters
echo ""
echo "Checking for optional formatters..."
echo "===================================="

check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        echo "Success: $1 is installed"
        return 0
    else
        echo "Error: $1 is not installed"
        return 1
    fi
}

# Check each formatter
check_command "black" || echo "   Install: pip install black"
check_command "prettier" || echo "   Install: npm install -g prettier"
check_command "shfmt" || echo "   Install: sudo apt-get install shfmt"
check_command "clang-format" || echo "   Install: sudo apt-get install clang-format"
check_command "jq" || echo "   Install: sudo apt-get install jq"
check_command "gofmt" || echo "   Install: Install Go language"
check_command "rustfmt" || echo "   Install: Install Rust language"
check_command "xmllint" || echo "   Install: sudo apt-get install libxml2-utils"

echo ""
echo "===================================="
echo "Setup complete!"
echo ""
echo "Hooks directory: $HOOKS_DIR"
echo "Settings file at: ~/.claude/settings.json"
echo ""
echo "To test the hooks, try:"
echo "  echo '{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"fix_bug.py\"}}' | python3 $HOOKS_DIR/filename_ban_hook.py"
echo ""
echo "For more information, see README.md"
echo "===================================="
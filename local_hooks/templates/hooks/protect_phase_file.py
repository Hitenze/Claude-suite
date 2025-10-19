#!/usr/bin/env python3
"""
Claude Code PreToolUse Hook - Protect phase file from direct modification
Prevents Agent from directly modifying .claude/current_phase file
Phase changes should only be done through custom commands

Configuration in settings.json:
{
  "matcher": "Edit|Write|MultiEdit|NotebookEdit",
  "hooks": [
    {
      "type": "command",
      "command": "/path/to/.claude/hooks/protect_phase_file.py"
    }
  ]
}

Protected tools:
- Edit: Modifies existing files
- Write: Creates/overwrites files
- MultiEdit: Multiple edits in one operation
- NotebookEdit: Modifies Jupyter notebooks
"""
import json
import os
import sys
from pathlib import Path


def is_phase_file(filepath):
    """Check if the file is a current_phase file"""
    if not filepath:
        return False
    # Normalize path
    path = Path(filepath).resolve()
    filename = path.name
    # Check if it's the current_phase file
    if filename == "current_phase":
        # Check if it's in a .claude directory
        parts = path.parts
        for i, part in enumerate(parts):
            if part == ".claude":
                return True
    return False


def main():
    """Main function"""
    # Read JSON data from stdin
    if sys.stdin.isatty():
        print("[ERROR] No input data received", file=sys.stderr)
        sys.exit(1)
    try:
        data = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parsing error: {e}", file=sys.stderr)
        sys.exit(1)
    # Get tool information
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    # For Edit operations, also check old_string content
    old_string = tool_input.get("old_string", "") or tool_input.get("old_str", "")
    new_string = tool_input.get("new_string", "") or tool_input.get("new_str", "")
    # For MultiEdit operations
    edits = tool_input.get("edits", [])
    # Check if trying to modify phase file
    if is_phase_file(file_path):
        print(
            "\n[ERROR] Direct modification of current_phase file is forbidden",
            file=sys.stderr,
        )
        print("=" * 60, file=sys.stderr)
        print(f"Attempted to modify: {file_path}", file=sys.stderr)
        print(
            "\nPhase transitions must be done through custom commands:", file=sys.stderr
        )
        print("  • Use /phase_01_explore to switch to EXPLORE phase", file=sys.stderr)
        print("  • Use /phase_02_plan to switch to PLAN phase", file=sys.stderr)
        print(
            "  • Use /phase_03_testdesign to switch to TESTDESIGN phase",
            file=sys.stderr,
        )
        print("  • Use /phase_04_code to switch to CODE phase", file=sys.stderr)
        print("  • Use /phase_05_sandbox to switch to SANDBOX phase", file=sys.stderr)
        print("\nThese commands ensure proper workflow enforcement.", file=sys.stderr)
        print("Direct file modification would bypass phase rules.", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        # Return JSON format decision
        decision = {
            "decision": "block",
            "reason": "Direct modification of current_phase is forbidden. Use phase commands instead.",
        }
        print(json.dumps(decision, ensure_ascii=False))
        sys.exit(2)  # Block operation
    # Allow all other operations
    print(f"[OK] Operation allowed for: {file_path}", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()

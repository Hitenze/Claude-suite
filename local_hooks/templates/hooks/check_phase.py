#!/usr/bin/env python3
"""
Claude Code PreToolUse Hook - Phase-based operation control
Controls what operations are allowed in each development phase
"""
import json
import os
import sys
from pathlib import Path


def get_current_phase():
    phase_file = os.path.join(os.path.dirname(__file__), "../current_phase")
    try:
        with open(phase_file, "r") as f:
            phase = f.read().strip().lower()
            return phase
    except Exception as e:
        print(f"[ERROR] Failed to read phase file: {e}", file=sys.stderr)
        return "unknown"


def is_markdown_file(filepath):
    """Check if the file is a markdown file"""
    return filepath.lower().endswith(".md")


def is_explore_file(filepath):
    """Check if the file is DESIGN.md, QUALITY.md, TODO.md, or CLAUDE.md (allowed in explore phase)"""
    filename = os.path.basename(filepath).upper()
    return filename in ["DESIGN.MD", "QUALITY.MD", "TODO.MD", "CLAUDE.MD"]


def is_test_file(filepath):
    """Check if the file is in any tests directory (anywhere in path)"""
    return "/tests/" in filepath or filepath.startswith("tests/")


def is_temp_file(filepath):
    """Check if the file is in any temp directory (anywhere in path)"""
    return "/temp/" in filepath or filepath.startswith("temp/")


def main():
    if sys.stdin.isatty():
        print("[ERROR] No input data received", file=sys.stderr)
        sys.exit(1)
    try:
        data = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parsing error: {e}", file=sys.stderr)
        sys.exit(1)
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    tool_name = data.get("tool_name", "")
    current_phase = get_current_phase()
    print(f"[INFO] Current phase: {current_phase}", file=sys.stderr)
    if not file_path:
        print("[OK] No file path to check", file=sys.stderr)
        sys.exit(0)
    if current_phase == "explore":
        if not is_explore_file(file_path):
            error_message = f"""
[ERROR] File blocked in explore phase

Current phase: {current_phase}
Attempted operation on: {file_path}

In explore phase, only these files can be modified:
- TODO.md (mark items as [COMPLETED] or [OBSOLETE] only)
- QUALITY.md (mark [RESOLVED] and add new issues)
- DESIGN.md (update architecture understanding)
- CLAUDE.md (project instructions and AI guidance)

To modify other files:
1. Change to 'plan' for other markdown files
2. Change to 'testdesign' for test files
3. Change to 'code' for implementation

To change phase, update: .claude/current_phase
"""
            print(error_message, file=sys.stderr)
            decision = {
                "decision": "block",
                "reason": "Explore phase only allows TODO.md, QUALITY.md, DESIGN.md, and CLAUDE.md",
            }
            print(json.dumps(decision))
            sys.exit(2)
        else:
            print(
                f"[OK] {os.path.basename(file_path)} allowed in explore phase: {file_path}",
                file=sys.stderr,
            )
    elif current_phase == "plan":
        if not is_markdown_file(file_path):
            error_message = f"""
[ERROR] Non-markdown file blocked in plan phase

Current phase: {current_phase}
Attempted operation on: {file_path}

In plan phase, only markdown (.md) files are allowed.
To modify other file types:
1. Change to 'testdesign' for test files
2. Change to 'code' for implementation

To change phase, update: .claude/current_phase
"""
            print(error_message, file=sys.stderr)
            decision = {
                "decision": "block",
                "reason": "Plan phase only allows markdown files",
            }
            print(json.dumps(decision))
            sys.exit(2)
        else:
            print(
                f"[OK] Markdown file allowed in plan phase: {file_path}",
                file=sys.stderr,
            )
    elif current_phase == "testdesign":
        if is_markdown_file(file_path):
            print(
                f"[OK] Markdown file allowed in testdesign phase: {file_path}",
                file=sys.stderr,
            )
        elif is_test_file(file_path) or is_temp_file(file_path):
            print(
                f"[OK] Test/temp file allowed in testdesign phase: {file_path}",
                file=sys.stderr,
            )
        else:
            error_message = f"""
[ERROR] Non-test/non-markdown file blocked in testdesign phase

Current phase: {current_phase}
Attempted operation on: {file_path}

In testdesign phase, only these files are allowed:
1. Markdown files (.md) anywhere
2. Files in any tests/ directory (e.g., tests/, src/tests/, project/tests/)
3. Files in any temp/ directory (e.g., temp/, build/temp/, project/temp/)

To modify implementation code, change phase to 'code'.

To change phase, update: .claude/current_phase
"""
            print(error_message, file=sys.stderr)
            decision = {
                "decision": "block",
                "reason": "Testdesign phase only allows markdown files and files in tests/ or temp/ directories",
            }
            print(json.dumps(decision))
            sys.exit(2)
    elif current_phase == "code":
        print(f"[OK] All files allowed in code phase: {file_path}", file=sys.stderr)
    elif current_phase == "sandbox":
        if is_temp_file(file_path):
            print(
                f"[OK] File in temp/ directory allowed in sandbox phase: {file_path}",
                file=sys.stderr,
            )
        else:
            error_message = f"""
[ERROR] File outside temp/ blocked in sandbox phase

Current phase: {current_phase}
Attempted operation on: {file_path}

In sandbox phase, all operations must be confined to temp/ directories.
Allowed: temp/, build/temp/, project/temp/, etc.
To modify main project files, change phase to 'code'.

To change phase, update: .claude/current_phase
"""
            print(error_message, file=sys.stderr)
            decision = {
                "decision": "block",
                "reason": "Sandbox phase only allows operations in temp/ directory",
            }
            print(json.dumps(decision))
            sys.exit(2)
    else:
        error_message = f"""
[ERROR] Unknown phase: {current_phase}

Valid phases are: explore, plan, testdesign, code, sandbox
Current phase file: .claude/current_phase

Please set a valid phase to continue.
"""
        print(error_message, file=sys.stderr)
        decision = {
            "decision": "block",
            "reason": f"Unknown phase: {current_phase}. Use: explore, plan, testdesign, code, or sandbox",
        }
        print(json.dumps(decision))
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()

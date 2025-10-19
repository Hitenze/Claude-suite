#!/usr/bin/env python3
"""
Claude Code PreToolUse Hook - Prevent .show() in Python files
Blocks any Python file containing .show() calls to avoid blocking execution
"""
import json
import os
import re
import sys
from pathlib import Path

# Configuration via environment variables
BLOCK_ON_DETECTION = os.environ.get("BLOCK_ON_DETECTION", "true").lower() == "true"
CHECK_TESTS_ONLY = (
    os.environ.get("CHECK_TESTS_ONLY", "false").lower() == "true"
)  # Default: check ALL Python files

# Pattern to detect .show() calls
SHOW_PATTERN = re.compile(
    r"\.show\s*\(", re.MULTILINE  # Matches .show( with optional whitespace
)

# Common matplotlib/plotting related .show() patterns for better error messages
SPECIFIC_PATTERNS = [
    (r"plt\.show\s*\(", "plt.show()"),
    (r"fig\.show\s*\(", "fig.show()"),
    (r"\.plot\(\)\.show\s*\(", ".plot().show()"),
    (r"ax\.show\s*\(", "ax.show()"),
]


def is_test_file(file_path):
    """Check if file is a test file"""
    if not file_path:
        return False

    path = Path(file_path)
    path_str = str(path).lower()

    # Check if 'test' appears in the path or filename
    return "test" in path_str


def find_show_calls(content):
    """Find all .show() calls in content"""
    matches = SHOW_PATTERN.findall(content)

    # Find specific patterns for better error messages
    found_patterns = []
    for pattern, name in SPECIFIC_PATTERNS:
        if re.search(pattern, content):
            found_patterns.append(name)

    return matches, found_patterns


def get_line_numbers(content, pattern):
    """Get line numbers where pattern appears"""
    lines = content.split("\n")
    line_numbers = []

    for i, line in enumerate(lines, 1):
        if re.search(pattern, line):
            line_numbers.append(i)

    return line_numbers


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

    # Get tool input
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "")

    # For Edit operations, check both old and new strings
    if not content:
        old_str = tool_input.get("old_string", "") or tool_input.get("old_str", "")
        new_str = tool_input.get("new_string", "") or tool_input.get("new_str", "")
        content = old_str + "\n" + new_str

    # For MultiEdit operations
    if not content and "edits" in tool_input:
        edits = tool_input.get("edits", [])
        content_parts = []
        for edit in edits:
            content_parts.append(edit.get("old_string", ""))
            content_parts.append(edit.get("new_string", ""))
        content = "\n".join(content_parts)

    if not content:
        print("[OK] No content to check", file=sys.stderr)
        sys.exit(0)

    # Check if it's a Python file
    if not file_path.endswith(".py"):
        print(f"[OK] Not a Python file: {file_path}", file=sys.stderr)
        sys.exit(0)

    # If CHECK_TESTS_ONLY is true, only check test files
    if CHECK_TESTS_ONLY and not is_test_file(file_path):
        print(f"[OK] Not a test file, skipping: {file_path}", file=sys.stderr)
        sys.exit(0)

    # Find .show() calls
    matches, specific_patterns = find_show_calls(content)

    if matches:
        # Get line numbers for better error reporting
        line_numbers = get_line_numbers(content, SHOW_PATTERN)

        print(
            f"\n[ERROR] .show() detected in Python file: {file_path}", file=sys.stderr
        )
        print("=" * 60, file=sys.stderr)

        if line_numbers:
            print(
                f"Found .show() calls on line(s): {', '.join(map(str, line_numbers[:10]))}",
                file=sys.stderr,
            )
            if len(line_numbers) > 10:
                print(
                    f"  ... and {len(line_numbers) - 10} more locations",
                    file=sys.stderr,
                )

        if specific_patterns:
            print(
                f"\nDetected patterns: {', '.join(specific_patterns)}", file=sys.stderr
            )

        print("\nSuggestion: Save plots to files instead:", file=sys.stderr)
        print("  Replace: plt.show()", file=sys.stderr)
        print("  With:    plt.savefig('output.png')", file=sys.stderr)
        print("           plt.close()", file=sys.stderr)
        print("\nOr use:", file=sys.stderr)
        print("  fig.savefig('figure.png')", file=sys.stderr)
        print("  matplotlib.pyplot.close('all')", file=sys.stderr)

        if is_test_file(file_path):
            print("\nFor tests, consider using:", file=sys.stderr)
            print("  plt.savefig(f'test_output_{test_name}.png')", file=sys.stderr)
            print(
                "  assert os.path.exists(f'test_output_{test_name}.png')",
                file=sys.stderr,
            )

        print("=" * 60, file=sys.stderr)

        if BLOCK_ON_DETECTION:
            # Return JSON format decision
            decision = {
                "decision": "block",
                "reason": f".show() calls found in Python file - use savefig() instead",
            }
            print(json.dumps(decision, ensure_ascii=False))
            sys.exit(2)  # Block operation
        else:
            print(
                "[WARNING] .show() calls found, but allowing operation to continue",
                file=sys.stderr,
            )
            sys.exit(0)
    else:
        print(f"[OK] No .show() calls found in {file_path}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()

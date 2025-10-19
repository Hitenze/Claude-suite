#!/usr/bin/env python3
"""
Claude Code PreToolUse Hook - Check for Chinese characters in content
Designed specifically for Claude Code hooks, checks content to be written
"""
import json
import os
import re
import sys

# Chinese and other non-ASCII character Unicode ranges
CHINESE_PATTERN = re.compile(
    r"[\u4e00-\u9fff"  # CJK Unified Ideographs
    r"\u3400-\u4dbf"  # CJK Extension A
    r"\U00020000-\U0002a6df"  # CJK Extension B
    r"\U0002a700-\U0002b73f"  # CJK Extension C
    r"\U0002b740-\U0002b81f"  # CJK Extension D
    r"\U0002b820-\U0002ceaf"  # CJK Extension E
    r"\U0002ceb0-\U0002ebef"  # CJK Extension F
    r"\U00030000-\U0003134f"  # CJK Extension G
    r"]"
)

# Japanese character ranges
JAPANESE_PATTERN = re.compile(
    r"[\u3040-\u309f"  # Hiragana
    r"\u30a0-\u30ff"  # Katakana
    r"]"
)

# Korean character ranges
KOREAN_PATTERN = re.compile(r"[\uac00-\ud7af]")  # Hangul Syllables

# Configuration
CHECK_MODE = os.environ.get("CHECK_MODE", "comments")  # 'comments', 'all', 'strings'
BLOCK_ON_DETECTION = os.environ.get("BLOCK_ON_DETECTION", "true").lower() == "true"
CHECK_CHINESE = os.environ.get("CHECK_CHINESE", "true").lower() == "true"
CHECK_JAPANESE = os.environ.get("CHECK_JAPANESE", "false").lower() == "true"
CHECK_KOREAN = os.environ.get("CHECK_KOREAN", "false").lower() == "true"


def extract_comments_from_content(content, file_ext):
    """Extract comments from content"""
    comments = []

    if file_ext in [
        ".cpp",
        ".cc",
        ".c",
        ".h",
        ".hpp",
        ".cxx",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".go",
        ".rs",
    ]:
        # C-style comments
        for match in re.finditer(r"//(.*)$", content, re.MULTILINE):
            comments.append(match.group(1))
        for match in re.finditer(r"/\*[\s\S]*?\*/", content):
            comments.append(match.group(0))

    elif file_ext in [".py", ".pyw"]:
        # Python comments
        for match in re.finditer(r"#(.*)$", content, re.MULTILINE):
            comments.append(match.group(1))
        # Docstrings
        for match in re.finditer(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'', content):
            comments.append(match.group(0))

    elif file_ext in [".sh", ".bash", ".zsh"]:
        # Shell comments
        for match in re.finditer(r"#(.*)$", content, re.MULTILINE):
            comments.append(match.group(1))

    return comments


def check_for_non_ascii(text):
    """Check for non-ASCII characters in text"""
    found_chars = {}

    if CHECK_CHINESE:
        chinese_matches = CHINESE_PATTERN.findall(text)
        if chinese_matches:
            found_chars["Chinese"] = chinese_matches

    if CHECK_JAPANESE:
        japanese_matches = JAPANESE_PATTERN.findall(text)
        if japanese_matches:
            found_chars["Japanese"] = japanese_matches

    if CHECK_KOREAN:
        korean_matches = KOREAN_PATTERN.findall(text)
        if korean_matches:
            found_chars["Korean"] = korean_matches

    return found_chars


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

    if not content:
        # If no content, try to read old_str and new_str (for Edit tool)
        old_str = tool_input.get("old_str", "")
        new_str = tool_input.get("new_str", "")
        content = old_str + "\n" + new_str

    if not content:
        print("[OK] No content to check", file=sys.stderr)
        sys.exit(0)

    # Get file extension
    from pathlib import Path

    file_ext = Path(file_path).suffix.lower() if file_path else ""

    # Check content based on check mode
    found_issues = {}

    if CHECK_MODE == "all":
        # Check entire content
        found_issues = check_for_non_ascii(content)
    elif CHECK_MODE == "comments":
        # Check only comments
        comments = extract_comments_from_content(content, file_ext)
        all_comments = "\n".join(comments)
        found_issues = check_for_non_ascii(all_comments)
    elif CHECK_MODE == "strings":
        # Check only strings (simplified version)
        strings = re.findall(r'"[^"]*"|\'[^\']*\'', content)
        all_strings = "\n".join(strings)
        found_issues = check_for_non_ascii(all_strings)

    # Output results
    if found_issues:
        print(f"\n[ERROR] Non-ASCII characters found in {file_path}:", file=sys.stderr)
        print("=" * 60, file=sys.stderr)

        for char_type, chars in found_issues.items():
            unique_chars = list(set(chars))[:20]  # Show first 20 different characters
            print(f"  {char_type} characters: {''.join(unique_chars)}", file=sys.stderr)
            if len(chars) > len(unique_chars):
                print(f"  (Total {len(chars)} {char_type} characters)", file=sys.stderr)

        print("=" * 60, file=sys.stderr)

        if BLOCK_ON_DETECTION:
            # Return JSON format decision
            decision = {
                "decision": "block",
                "reason": f"Non-ASCII characters found: {', '.join(found_issues.keys())}",
            }
            print(json.dumps(decision, ensure_ascii=False))
            sys.exit(2)  # Block operation
        else:
            print(
                "[WARNING] Non-ASCII characters found, but allowing operation to continue",
                file=sys.stderr,
            )
            sys.exit(0)
    else:
        print(f"[OK] No non-ASCII characters found in {file_path}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()

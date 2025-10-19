#!/usr/bin/env python3
"""
Claude Code PreToolUse Hook - Ban poor file naming patterns
Encourages good naming practices and organized file structure
"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Common typos mapping
COMMON_TYPOS = {
    # Final/finish related
    "fianl": "final",
    "finial": "final",
    "finel": "final",
    # Modified/update related
    "modifed": "modified",
    "modifeid": "modified",
    "modfied": "modified",
    "udpate": "update",
    "updaet": "update",
    "upadte": "update",
    # Service/server related
    "servce": "service",
    "serivce": "service",
    "sevice": "service",
    "srevice": "service",
    # Function/utility related
    "fucntion": "function",
    "funtion": "function",
    "funciton": "function",
    "utitlity": "utility",
    "utilty": "utility",
    # Manager/handler related
    "manger": "manager",
    "maneger": "manager",
    "mangaer": "manager",
    "hanlder": "handler",
    "hadnler": "handler",
    # Config/version related
    "confing": "config",
    "cofnig": "config",
    "verison": "version",
    "vresion": "version",
    # Template/temporary related
    "tempalte": "template",
    "tempate": "template",
    "templat": "template",
    # Return/result related
    "retrun": "return",
    "retunr": "return",
    "resutl": "result",
    "reuslt": "result",
    # Enhanced/improved related
    "enhacned": "enhanced",
    "enhaced": "enhanced",
    # Controller/component related
    "controler": "controller",
    "contoller": "controller",
    "componenet": "component",
    "compoennt": "component",
}

# Bad naming patterns (both prefix and suffix)
BAD_PATTERNS = {
    # Temporary and junk files
    "temporary": {
        "patterns": [
            r"^temp$",
            r"^temp_",
            r"_temp$",
            r"^temporary$",
            r"^temporary_",
            r"_temporary$",
            r"^tmp$",
            r"^tmp_",
            r"_tmp$",
            r"^scratch$",
            r"^scratch_",
            r"_scratch$",
        ],
        "reason": "Temporary file pattern detected",
        "suggestion": "Use the temp/ directory for temporary files",
    },
    "junk": {
        "patterns": [
            r"^junk_",
            r"_junk$",
            r"^trash_",
            r"_trash$",
            r"^delete_me_",
            r"_delete_me$",
        ],
        "reason": "Junk file pattern detected",
        "suggestion": "Use descriptive names or place in temp/ if truly temporary",
    },
    # Version control anti-patterns
    "version": {
        "patterns": [r"^v\d+_", r"_v\d+$", r"^version\d+_", r"_version\d+$"],
        "reason": "Version number in filename",
        "suggestion": "Use git for version control, not filenames",
    },
    "final": {
        "patterns": [r"^final_", r"_final$", r"_final_final$", r"_final_v\d+$"],
        "reason": "Final/latest pattern detected",
        "suggestion": "Nothing is ever final - use descriptive names instead",
    },
    "temporal": {
        "patterns": [
            r"^new_",
            r"_new$",
            r"^old_",
            r"_old$",
            r"^latest_",
            r"_latest$",
            r"^current_",
            r"_current$",
        ],
        "reason": "Temporal descriptor in filename",
        "suggestion": "These terms become outdated - use descriptive names",
    },
    # Poor naming patterns
    "copy": {
        "patterns": [r"^copy_", r"_copy$", r"^copy\d+_", r"_copy\d+$", r"^\([0-9]+\)"],
        "reason": "Copy/duplicate pattern detected",
        "suggestion": "Use descriptive names or backup/ directory for copies",
    },
    "generic": {
        "patterns": [
            r"^untitled",
            r"^noname",
            r"^unnamed_",
            r"_unnamed$",
            r"^misc_",
            r"_misc$",
        ],
        "reason": "Generic/meaningless name",
        "suggestion": "Use descriptive names that explain the file purpose",
    },
    # Fix/modification markers (both present and past tense)
    "fix": {
        "patterns": [
            r"^fix$",
            r"^fix_",
            r"_fix$",
            r"^fixed$",
            r"^fixed_",
            r"_fixed$",
            r"^bugfix$",
            r"^bugfix_",
            r"_bugfix$",
            r"^hotfix$",
            r"^hotfix_",
            r"_hotfix$",
            r"^repair$",
            r"^repair_",
            r"_repair$",
            r"^repaired$",
            r"^repaired_",
            r"_repaired$",
        ],
        "reason": "Fix/bugfix pattern detected",
        "suggestion": "Fix the original file and use git commits to track changes",
    },
    "modified": {
        "patterns": [
            r"^modify_",
            r"_modify$",
            r"^modified_",
            r"_modified$",
            r"^update_",
            r"_update$",
            r"^updated_",
            r"_updated$",
            r"^change_",
            r"_change$",
            r"^changed_",
            r"_changed$",
        ],
        "reason": "Modification marker detected",
        "suggestion": "Modify the original file directly, backup to backup/ if needed",
    },
    "enhanced": {
        "patterns": [
            r"^enhance_",
            r"_enhance$",
            r"^enhanced_",
            r"_enhanced$",
            r"^improve_",
            r"_improve$",
            r"^improved_",
            r"_improved$",
            r"^optimize_",
            r"_optimize$",
            r"^optimized_",
            r"_optimized$",
        ],
        "reason": "Enhancement marker detected",
        "suggestion": "Enhance the original file, use git commits to track improvements",
    },
    # Validation/check markers (both present and past tense)
    "validation": {
        "patterns": [
            r"^check_",
            r"_check$",
            r"^checked_",
            r"_checked$",
            r"^run_",
            r"_run$",
            r"^verify_",
            r"_verify$",
            r"^verified_",
            r"_verified$",
            r"^validate_",
            r"_validate$",
            r"^validated_",
            r"_validated$",
        ],
        "reason": "Validation/check marker detected",
        "suggestion": "Use git commits or comments to track validation status. Use temp/ directories for temp test code",
    },
    # Experimental/demo patterns
    "experimental": {
        "patterns": [
            r"^demo_",
            r"_demo$",
            r"^example_",
            r"_example$",
            r"^sample_",
            r"_sample$",
            r"^poc_",
            r"_poc$",
            r"^experiment_",
            r"_experiment$",
        ],
        "reason": "Experimental/demo pattern detected",
        "suggestion": "Use demos/, examples/, or temp/ directories for demo code",
    },
    # Work in progress patterns
    "draft": {
        "patterns": [
            r"^draft_",
            r"_draft$",
            r"^wip_",
            r"_wip$",
            r"^attempt_",
            r"_attempt$",
            r"^try_",
            r"_try$",
        ],
        "reason": "Work-in-progress pattern detected",
        "suggestion": "Complete the work or use temp/ for drafts",
    },
    # Version comparison patterns
    "versioning": {
        "patterns": [
            r"^original_",
            r"_original$",
            r"^before_",
            r"_before$",
            r"^after_",
            r"_after$",
            r"^backup_",
            r"_backup$",
        ],
        "reason": "Version comparison pattern detected",
        "suggestion": "Use git for version control or backup/ directory",
    },
    # Hack patterns
    "hack": {
        "patterns": [
            r"^hack_",
            r"_hack$",
            r"^quick_hack",
            r"_quick_hack$",
            r"^dirty_hack",
            r"_dirty_hack$",
            r"^workaround_",
            r"_workaround$",
        ],
        "reason": "Hack pattern detected",
        "suggestion": "Use proper implementation instead of hacks",
    },
    # Numbered file patterns
    "numbered": {
        "patterns": [
            r"^test\d+$",
            r"^file\d+$",
            r"^script\d+$",
            r"^code\d+$",
            r"^main\d+$",
            r"^untitled\d+$",
            r"^document\d+$",
        ],
        "reason": "Numbered file pattern detected",
        "suggestion": "Use descriptive names instead of numbers",
    },
    # Debug patterns
    "debug": {
        "patterns": [
            r"^debug$",
            r"^debug_",
            r"_debug$",
            r"^debugging$",
            r"^debugging_",
            r"_debugging$",
            r"^debugger$",
            r"^debugger_",
            r"_debugger$",
        ],
        "reason": "Debug pattern detected",
        "suggestion": "Remove debug code or use logging instead",
    },
}

# Allowed patterns for standard test files
ALLOWED_TEST_PATTERNS = [
    r"^test_.*\.py$",
    r".*_test\.py$",
    r"^test.*\.js$",
    r".*\.test\.[jt]s$",
    r"^Test.*\.java$",
]

# Special directories with relaxed rules
SPECIAL_DIRS = [
    "temp",
    "tmp",
    "backup",
    "backups",
    "archive",
    "docs",
]


def check_bad_patterns(filename):
    """Check if filename matches any bad patterns"""
    name_without_ext = Path(filename).stem

    for category, info in BAD_PATTERNS.items():
        for pattern in info["patterns"]:
            if re.search(pattern, name_without_ext, re.IGNORECASE):
                return {
                    "matched": True,
                    "pattern": pattern,
                    "category": category,
                    "reason": info["reason"],
                    "suggestion": info["suggestion"],
                }
    return {"matched": False}


def check_typos(filename):
    """Check if filename contains common typos"""
    name_without_ext = Path(filename).stem.lower()

    # Split on common separators
    parts = re.split(r"[_\-\.]", name_without_ext)

    found_typos = []
    corrections = []

    for part in parts:
        if part in COMMON_TYPOS:
            found_typos.append(part)
            corrections.append(COMMON_TYPOS[part])

    if found_typos:
        # Rebuild the corrected filename
        corrected_parts = []
        for part in parts:
            if part in COMMON_TYPOS:
                corrected_parts.append(COMMON_TYPOS[part])
            else:
                corrected_parts.append(part)

        corrected_name = "_".join(corrected_parts) + Path(filename).suffix

        return {
            "matched": True,
            "typos": found_typos,
            "corrections": corrections,
            "suggested_name": corrected_name,
            "reason": f"Typo detected: {', '.join(f'{t}→{c}' for t, c in zip(found_typos, corrections))}",
        }

    return {"matched": False}


def is_test_file(filepath):
    """Check if file follows standard test naming conventions"""
    filename = os.path.basename(filepath)
    return any(re.match(pattern, filename) for pattern in ALLOWED_TEST_PATTERNS)


def is_in_special_dir(filepath):
    """Check if file is in a special directory (case-insensitive)"""
    parts = Path(filepath).parts
    special_dirs_lower = [d.lower() for d in SPECIAL_DIRS]
    return any(part.lower() in special_dirs_lower for part in parts)


def is_in_test_dir(filepath):
    """Check if file is in a test directory (tests/test/TESTS/TEST)"""
    parts = Path(filepath).parts
    test_dir_names = ["tests", "test"]
    return any(part.lower() in test_dir_names for part in parts)


def is_context_appropriate(filepath, match_result):
    """Check if the pattern is appropriate for the directory context"""
    parts = Path(filepath).parts
    filename = os.path.basename(filepath)
    pattern = match_result.get("pattern", "")

    # Context-aware exceptions
    context_rules = {
        "tests": {"patterns": [r"^test_"], "reason": "test files belong in tests/"},
        "examples": {
            "patterns": [r"^example_"],
            "reason": "example files belong in examples/",
        },
        "demos": {"patterns": [r"^demo_"], "reason": "demo files belong in demos/"},
    }

    # Check each directory in the path
    for dir_name, rule in context_rules.items():
        if dir_name in [part.lower() for part in parts]:
            # This directory allows certain patterns
            for allowed_pattern in rule["patterns"]:
                if re.match(allowed_pattern, filename, re.IGNORECASE):
                    return (
                        True,
                        f"Pattern '{pattern}' is allowed in {dir_name}/ directory",
                    )

    # Check if pattern suggests a specific directory
    for dir_name, rule in context_rules.items():
        for allowed_pattern in rule["patterns"]:
            if pattern == allowed_pattern:
                return (
                    False,
                    f"This pattern should be used in {dir_name}/ directory: {rule['reason']}",
                )

    return False, None


def suggest_better_name(filepath, match_info):
    """Suggest a better filename based on the bad pattern"""
    filename = os.path.basename(filepath)
    name_without_ext = Path(filename).stem
    ext = Path(filename).suffix

    # Remove bad prefixes/suffixes
    cleaned_name = name_without_ext
    pattern = match_info["pattern"]

    # Remove the pattern from the name
    if pattern.startswith("^"):
        # Remove prefix pattern using regex
        pattern_without_anchor = pattern[1:]
        match = re.match(pattern_without_anchor, name_without_ext, re.IGNORECASE)
        if match:
            cleaned_name = name_without_ext[match.end() :]
    elif pattern.endswith("$"):
        # Remove suffix pattern using regex
        pattern_without_anchor = pattern[:-1]
        match = re.search(
            pattern_without_anchor + r"$", name_without_ext, re.IGNORECASE
        )
        if match:
            cleaned_name = name_without_ext[: match.start()]

    cleaned_name = cleaned_name.strip("_")

    # If name becomes empty or too short, suggest generic improvement
    if not cleaned_name or len(cleaned_name) < 3:
        suggestions = [
            f"module{ext}",
            f"service{ext}",
            f"handler{ext}",
            f"processor{ext}",
            f"manager{ext}",
        ]
        cleaned_name = f"<descriptive_name>{ext}"
    else:
        cleaned_name = f"{cleaned_name}{ext}"

    return cleaned_name


def generate_backup_path(original_path):
    """Generate a backup path with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(original_path)
    return f"backup/{timestamp}_{filename}"


def check_markdown_restrictions(filepath):
    """Check if markdown file is allowed"""
    filename = os.path.basename(filepath)

    # Not a markdown file? Allow it
    if not filename.lower().endswith(".md"):
        return {"allowed": True}

    # Allowed markdown files
    ALLOWED_MARKDOWN_FILES = [
        "CLAUDE.md",
        "TODO.md",
        "README.md",
        "INSTALL.md",
        "DESIGN.md",
        "QUALITY.md",
    ]

    # Check if it's an allowed markdown file (case-insensitive)
    if filename.upper() in [f.upper() for f in ALLOWED_MARKDOWN_FILES]:
        return {"allowed": True}

    # Check if it's in docs directory
    parts = Path(filepath).parts
    if "docs" in [part.lower() for part in parts]:
        return {"allowed": True}

    # Otherwise, block it
    return {
        "allowed": False,
        "reason": "Unnecessary markdown file",
        "suggestion": f"Place documentation in docs/ directory or use one of: {', '.join(ALLOWED_MARKDOWN_FILES)}",
    }


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
    tool_name = data.get("tool_name", "")

    if not file_path:
        print("[OK] No file path to check", file=sys.stderr)
        sys.exit(0)

    # Only check new file creation (Write tool with new files)
    # Allow editing existing files even with bad names
    if tool_name in ["Edit", "MultiEdit"] or os.path.exists(file_path):
        print(f"[OK] Allowing edit of existing file: {file_path}", file=sys.stderr)
        sys.exit(0)

    # Check if in special directory (temp/, backup/ etc)
    if is_in_special_dir(file_path):
        print(
            f"[OK] File in special directory, relaxed rules: {file_path}",
            file=sys.stderr,
        )
        sys.exit(0)

    # Check markdown restrictions first
    markdown_check = check_markdown_restrictions(file_path)
    if not markdown_check["allowed"]:
        filename = os.path.basename(file_path)

        error_message = f"""
[ERROR] {markdown_check['reason']}: '{filename}'

{markdown_check['suggestion']}

Allowed markdown files:
- CLAUDE.md (Claude Code configuration)
- TODO.md (Task tracking)
- README.md (Project documentation)
- INSTALL.md (Installation guide)
- DESIGN.md (Architecture and design documentation)
- QUALITY.md (Issue found in implementation)

All other documentation should go in the docs/ directory.
"""
        print(error_message, file=sys.stderr)

        # Return JSON decision to block
        decision = {
            "decision": "block",
            "reason": f"{markdown_check['reason']}. {markdown_check['suggestion']}",
        }
        print(json.dumps(decision))
        sys.exit(2)  # Block operation

    # Check for bad patterns
    filename = os.path.basename(file_path)
    match_result = check_bad_patterns(filename)

    if match_result["matched"]:
        # Check if pattern is appropriate for the directory context
        is_appropriate, context_message = is_context_appropriate(
            file_path, match_result
        )

        if is_appropriate:
            print(f"[OK] {context_message}: {file_path}", file=sys.stderr)
            sys.exit(0)

        better_name = suggest_better_name(file_path, match_result)

        error_message = f"""
[ERROR] Poor filename detected: '{filename}'

Pattern matched: {match_result['pattern']}
Category: {match_result['category']}
Reason: {match_result['reason']}

{match_result['suggestion']}

Suggested alternatives:
1. Use a descriptive name: {better_name}
2. If this is temporary code, place it in: temp/{filename}
3. If this is a backup, use: {generate_backup_path(file_path)}

Example good names:
- user_authentication.py
- payment_processor.js  
- data_validator.py
- customer_service.py
"""

        print(error_message, file=sys.stderr)

        # Return JSON decision to block with concise suggestion
        # Check if there's a context-specific suggestion
        _, context_msg = is_context_appropriate(file_path, match_result)
        if context_msg and "should be used in" in context_msg:
            # Extract directory suggestion from context message
            if "tests/" in context_msg:
                suggestion = f"tests/{filename}"
            elif "examples/" in context_msg:
                suggestion = f"examples/{filename}"
            elif "demos/" in context_msg:
                suggestion = f"demos/{filename}"
            else:
                suggestion = f"temp/{filename}"
        else:
            suggestion = f"temp/{filename}"

        decision = {
            "decision": "block",
            "reason": f"{match_result['reason']}. Try: {better_name} or {suggestion}",
        }
        print(json.dumps(decision))
        sys.exit(2)  # Block operation

    # Check for typos
    typo_result = check_typos(filename)
    if typo_result["matched"]:
        error_message = f"""
[ERROR] Typo detected in filename: '{filename}'

Typos found: {', '.join(f"{t}→{c}" for t, c in zip(typo_result['typos'], typo_result['corrections']))}

Suggested filename: {typo_result['suggested_name']}
"""
        print(error_message, file=sys.stderr)

        # Return JSON decision to block with concise suggestion
        decision = {
            "decision": "block",
            "reason": f"{typo_result['reason']}. Try: {typo_result['suggested_name']} or temp/{filename}",
        }
        print(json.dumps(decision))
        sys.exit(2)  # Block operation

    # Check if it's a standard test file in a test directory
    if is_in_test_dir(file_path) and is_test_file(file_path):
        print(
            f"[OK] Standard test file in test directory: {file_path}", file=sys.stderr
        )
    else:
        print(f"[OK] Good filename: {file_path}", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()

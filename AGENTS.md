# Repository Guidelines

## Project Structure & Module Organization
- `hooks/` — Claude Code hooks used pre/post tool runs (e.g., `filename_ban_hook.py`, `check_chinese_hook.py`, `no_show_in_python_hook.py`, `formatting.sh`, `formatting_hook.sh`).
- `local_hooks/` — Deployable 5‑phase workflow: `phase_manager.py`, `templates/commands/phase_*.md`, `templates/hooks/*.py` (e.g., `phase.py`, `check_phase.py`, `protect_phase_file.py`).
- `macos/`, `ubuntu/` — Setup scripts that create `~/.claude/settings.json` and make hooks executable.
- Generated (in target repos): `.claude/commands`, `.claude/hooks`, `.claude/current_phase`.

## Build, Test, and Development Commands
- Setup (macOS/Linux): `bash macos/setup_macos.sh` or `bash ubuntu/setup_ubuntu.sh` — installs hooks and writes `~/.claude/settings.json`.
- Deploy 5‑phase workflow to a project: `python3 local_hooks/phase_manager.py --target /path/to/project [--force]`.
- Switch phase in a deployed project: `python3 .claude/hooks/phase.py -s code` (use `explore|plan|testdesign|code|sandbox`).
- Format files: `CLAUDE_FILE_PATHS="file1.py file2.sh" bash hooks/formatting.sh`.
- Quick hook check: `echo '{"tool_name":"Write","tool_input":{"file_path":"fix_bug.py"}}' | python3 hooks/filename_ban_hook.py`.

## Coding Style & Naming Conventions
- Python: black (line length 88), 4‑space indent.
- Shell: shfmt with 2 spaces (`shfmt -i 2 -ci -w`).
- C/C++: clang‑format, 3‑space indent, column limit 100.
- JS/TS/MD/YAML/JSON: Prettier (jq fallback for JSON).
- Filenames: use descriptive names; avoid patterns like `temp`, `tmp`, `final`, `copy`, `v1`. Test files: `test_*.py`, `*.test.ts`.
- Root docs allowed: `README.md`, `TODO.md`, `DESIGN.md`, `CLAUDE.md`, `INSTALL.md`, `QUALITY.md`. Put other docs in `docs/`.

## Testing Guidelines
- No formal test suite. Validate hooks by piping JSON; exit `0` allows, `2` blocks. Example above (filename ban). Use `CHECK_MODE=comments` for `check_chinese_hook.py` as needed.

## Commit & Pull Request Guidelines
- Use Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`. Example: `feat(hooks): add .show() guard`.
- PRs: include purpose, linked issues, sample command/output, and OS tested (macOS/Ubuntu).

## Agent‑Specific Instructions
- Follow the 5‑phase flow. In `explore`, only edit `TODO.md`, `QUALITY.md`, `DESIGN.md`, `CLAUDE.md`. In `plan`, only Markdown. In `sandbox`, write under `temp/`.
- Never edit `.claude/current_phase` directly; use `phase.py` or the provided phase commands.

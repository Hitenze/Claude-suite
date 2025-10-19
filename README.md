## Claude Suite: Hooks and 5‑Phase TDD Workflow
Claude Suite provides plug‑and‑play engineering hooks and a deployable local 5‑phase TDD workflow for Claude Code.
为 Claude Code 提供可插拔工程化 hooks 与可部署的本地 5 阶段 TDD 流程。

## Purpose
This suite was developed with assistance from Claude Code and aims to standardize team workflows through hooks and a phase‑based TDD process. For issues or suggestions, contact Tianshi Xu <txu41@emory.edu>.
该套件在开发阶段使用了 Claude Code 辅助，目标是通过 hooks 与阶段化 TDD 流程规范团队协作。如有问题或建议，请联系 Tianshi Xu <txu41@emory.edu>。

## Status & Disclaimer
Provided as‑is under the MIT License (see LICENSE). Issues are welcome.
本项目按现状（as‑is）提供，采用 MIT 许可（见 LICENSE）。欢迎提交 issues。

## Feature Overview
- hooks/filename_ban_hook.py: Prevents poor filename patterns and suggests alternatives; includes a root Markdown allowlist.
  约束不良文件命名并给出替代建议；包含根目录 Markdown 白名单。
- hooks/check_chinese_hook.py: Detects Chinese/non‑ASCII content with configurable scope and block/warn modes.
  检测中文/非 ASCII 内容，支持配置检查范围与阻断/警告模式。
- hooks/no_show_in_python_hook.py: Blocks `.show()` in Python to avoid blocking execution (e.g., matplotlib).
  阻止 Python 中的 `.show()`，避免运行阻塞（如 matplotlib）。
- hooks/formatting.sh + hooks/formatting_hook.sh: Unified multi‑language formatting (black/prettier/shfmt/clang‑format with graceful fallback).
  多语言统一格式化（black/prettier/shfmt/clang‑format 等，带降级策略）。
- local_hooks/templates/hooks/check_phase.py: Enforces write permissions based on the current phase (file types/paths).
  基于当前阶段限制可写的文件类型与目录。
- local_hooks/templates/hooks/protect_phase_file.py: Prevents direct edits to `.claude/current_phase`.
  Note that this is a lightweight safeguard, as claude code might still modify the file directly or with python scripts. You could improve it by adding more sophisticated checks.
  禁止直接修改 `.claude/current_phase`。注意这是一个轻量级的安全措施，因为 Claude Code 可能仍然直接或通过 Python 脚本修改文件。你可以通过添加更复杂的检查来改进它。
- local_hooks/phase_manager.py: One‑command deployer to install the 5‑phase workflow and hooks into a target project.
  一条命令将 5 阶段工作流与 hooks 部署到目标项目。
  - Commands installed: 
    - use `/phase_01_explore`, `/phase_02_plan`, `/phase_03_testdesign`, `/phase_04_code`, `/phase_05_sandbox` inside Claude Code; or run `python3 .claude/hooks/phase.py -s <phase>`.
    - 在 Claude Code 中使用 `/phase_01_explore`、`/phase_02_plan`、`/phase_03_testdesign`、`/phase_04_code`、`/phase_05_sandbox`；或运行 `python3 .claude/hooks/phase.py -s <phase>`。
  - Phase overview
    - **explore**: read‑only, only update TODO/QUALITY/DESIGN/CLAUDE; 只读，仅允许更新 TODO/QUALITY/DESIGN/CLAUDE。
    - **plan**: markdown‑only, update and backup TODO/QUALITY/DESIGN to agentlogs/archive/; 仅 Markdown，更新并备份 TODO/QUALITY/DESIGN 到 agentlogs/archive/。
    - **testdesign**: tests + markdown (`tests/`, `temp/` allowed), write failing tests and update DESIGN; 测试 + Markdown（允许 `tests/`、`temp/`），编写失败测试并更新 DESIGN。
    - **code**: implement/refactor, normal code writes allowed, refactor allowed; 实现/重构，解除代码写入限制，允许重构。
    - **sandbox**: temp‑only integration, only allowed to write to temp/ directory, integration tests allowed; 仅 temp 目录内集成验证，仅允许写入 temp/ 目录，允许集成测试。

## Quick Start
Global setup installs shared hooks configuration under your home directory.
全局安装会在你的用户目录下写入共享的 hooks 配置。

- macOS: `bash macos/setup_macos.sh`
  macOS：`bash macos/setup_macos.sh`
- Ubuntu/Linux: `bash ubuntu/setup_ubuntu.sh`
  Ubuntu/Linux：`bash ubuntu/setup_ubuntu.sh`

Project‑level setup deploys the 5‑phase workflow into a target repository.
项目级安装会把 5 阶段工作流部署到目标仓库中。

- Deploy: `python3 local_hooks/phase_manager.py --target /path/to/project [--force]`
  部署：`python3 local_hooks/phase_manager.py --target /path/to/project [--force]`
- After deploy, switch phase inside the target project: `python3 .claude/hooks/phase.py -s plan`
  部署完成后在目标项目内切换阶段：`python3 .claude/hooks/phase.py -s plan`

Customize as needed for your project or team.
根据项目/团队需要进行自定义。

- Edit project overrides at `.claude/settings.local.json` in the target repo.
  在目标仓库的 `.claude/settings.local.json` 覆盖配置。
- Update hook allowlists/rules if your docs or naming differ.
  若文档或命名策略不同，可更新 hook 的白名单/规则。

#!/usr/bin/env python3
"""
Deploy 5-phase TDD workflow to target project

Usage: python3 phase_manager.py --target /path/to/project [--force]
"""

import argparse
import json
import os
import shutil
from pathlib import Path


class PhaseDeployer:
    def __init__(self, source_dir=None):
        """Initialize deployer with source template directory"""
        if source_dir:
            self.source_dir = Path(source_dir)
        else:
            # Look for templates in the same directory as this script, or in local_hooks
            script_parent = Path(__file__).parent
            if (script_parent / "templates").exists():
                self.source_dir = script_parent / "templates"
            else:
                # Fallback to local_hooks/templates (common case when script is in temp/)
                self.source_dir = script_parent.parent / "local_hooks" / "templates"

    def validate_target(self, target_dir):
        """Validate target directory exists and is writable"""
        target_path = Path(target_dir)
        if not target_path.exists():
            raise ValueError(f"Target directory does not exist: {target_dir}")
        if not target_path.is_dir():
            raise ValueError(f"Target path is not a directory: {target_dir}")
        if not os.access(target_path, os.W_OK):
            raise ValueError(f"Target directory is not writable: {target_dir}")

    def create_directory_structure(self, target_dir):
        """Create .claude directory structure in target"""
        claude_dir = Path(target_dir) / ".claude"
        commands_dir = claude_dir / "commands"
        hooks_dir = claude_dir / "hooks"

        # Create directories
        claude_dir.mkdir(exist_ok=True)
        commands_dir.mkdir(exist_ok=True)
        hooks_dir.mkdir(exist_ok=True)

        return claude_dir, commands_dir, hooks_dir

    def copy_templates(self, target_dir, force=False):
        """Copy all template files to target directory"""
        claude_dir, commands_dir, hooks_dir = self.create_directory_structure(
            target_dir
        )

        # Copy hook templates
        hooks_source = self.source_dir / "hooks"
        for hook_file in hooks_source.glob("*.py"):
            target_file = hooks_dir / hook_file.name
            if target_file.exists() and not force:
                print(
                    f"Warning: {target_file} already exists, use --force to overwrite"
                )
                continue
            shutil.copy2(hook_file, target_file)
            print(f"Copied {hook_file.name} to {target_file}")

        # Copy command templates and replace {root} placeholder
        commands_source = self.source_dir / "commands"
        target_root = str(Path(target_dir).resolve())

        for command_file in commands_source.glob("*.md"):
            target_file = commands_dir / command_file.name
            if target_file.exists() and not force:
                print(
                    f"Warning: {target_file} already exists, use --force to overwrite"
                )
                continue

            # Read template and replace {root} placeholder
            with open(command_file, "r") as f:
                content = f.read()
            content = content.replace("{root}", target_root)

            # Write to target
            with open(target_file, "w") as f:
                f.write(content)
            print(f"Copied {command_file.name} to {target_file}")

        return claude_dir

    def update_settings_local(self, target_dir):
        """Update or create settings.local.json with hook configuration"""
        settings_file = Path(target_dir) / ".claude" / "settings.local.json"
        target_root = str(Path(target_dir).resolve())

        # Hook configuration
        hooks_config = {
            "hooks": {
                "PreToolUse": [
                    {
                        "matcher": "Edit|Write|MultiEdit",
                        "hooks": [
                            {
                                "type": "command",
                                "command": f"python3 {target_root}/.claude/hooks/check_phase.py",
                            },
                            {
                                "type": "command",
                                "command": f"python3 {target_root}/.claude/hooks/protect_phase_file.py",
                            },
                        ],
                    }
                ]
            }
        }

        # Read existing settings if present
        if settings_file.exists():
            with open(settings_file, "r") as f:
                existing_config = json.load(f)
        else:
            existing_config = {}

        # Merge configurations
        existing_config.update(hooks_config)

        # Write updated settings
        with open(settings_file, "w") as f:
            json.dump(existing_config, f, indent=2)

        print(f"Updated {settings_file}")
        return settings_file

    def initialize_phase_file(self, target_dir):
        """Initialize current_phase file"""
        phase_file = Path(target_dir) / ".claude" / "current_phase"
        with open(phase_file, "w") as f:
            f.write("explore\n")
        print(f"Initialized {phase_file} with 'explore' phase")
        return phase_file

    def deploy(self, target_dir, force=False):
        """Main deployment method"""
        print(f"Deploying 5-phase TDD workflow to: {target_dir}")
        print("=" * 60)

        # Validate target
        self.validate_target(target_dir)

        # Copy templates
        claude_dir = self.copy_templates(target_dir, force)

        # Update settings
        settings_file = self.update_settings_local(target_dir)

        # Initialize phase
        phase_file = self.initialize_phase_file(target_dir)

        # Success message
        print("=" * 60)
        print("✅ Phase system deployed successfully!")
        print()
        print("Generated 5-phase TDD workflow:")
        print("  1. EXPLORE   - Read-only analysis")
        print("  2. PLAN      - Design and planning (markdown only)")
        print("  3. TESTDESIGN - Write failing tests (TDD Red step)")
        print("  4. CODE      - Implement code (TDD Green/Refactor steps)")
        print("  5. SANDBOX   - Integration testing (temp/ directory only)")
        print()
        print("🔧 Configuration:")
        print(f"  Settings: {settings_file}")
        print(f"  Phase file: {phase_file}")
        print(f"  Commands: {claude_dir}/commands/")
        print(f"  Hooks: {claude_dir}/hooks/")
        print()
        print("📝 Next steps:")
        print("  1. Restart Claude Code to load new settings")
        print("  2. Use /phase_01_explore, /phase_02_plan, etc. commands")
        print("  3. Current phase: EXPLORE")
        print()
        print("Both hooks ensure:")
        print("  • check_phase.py     - Enforces file editing permissions per phase")
        print(
            "  • protect_phase_file.py - Prevents direct modification of current_phase"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Deploy 5-phase TDD workflow system to target project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--target", "-t", required=True, help="Target project directory"
    )
    parser.add_argument(
        "--force", "-f", action="store_true", help="Overwrite existing files"
    )

    args = parser.parse_args()

    try:
        deployer = PhaseDeployer()
        deployer.deploy(args.target, args.force)
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()

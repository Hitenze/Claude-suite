---
allowed-tools: Bash(python3:*)
description: Switch to EXPLORE phase and record state
---

## Context
- Set phase: !`python3  {root}/.claude/hooks/phase.py -s explore`

## Your task

<task phase="EXPLORE">
  <principle>
    Treat the codebase as read-only. Observe, understand, and document findings without modifying source code.
  </principle>
  
  <workflow>
    <step order="1">Read and analyze existing TODO.md to understand pending work</step>
    <step order="2">Review codebase for quality issues and architectural understanding</step>
    <step order="3">Mark completed TODOs with [COMPLETED] prefix</step>
    <step order="4">Mark resolved quality issues with [RESOLVED] prefix</step>
    <step order="5">Document new findings in QUALITY.md and DESIGN.md</step>
  </workflow>
  
  <permissions>
    <read>
      <allow>Read all project files (source, docs, configs)</allow>
      <allow>Search codebase (grep, find, ls -R)</allow>
      <allow>Analyze architecture, dependencies, and call graphs</allow>
      <allow>Run existing test suites (e.g., pytest)</allow>
    </read>
    <write>
      <allow file="TODO.md" mode="mark-only">
        <action>Mark completed items with [COMPLETED] prefix</action>
        <action>Mark obsolete items with [OBSOLETE] prefix</action>
        <forbid>Add new TODO items (save for PLAN phase)</forbid>
      </allow>
      <allow file="QUALITY.md" mode="full">
        <action>Mark resolved issues with [RESOLVED] prefix</action>
        <action>Add newly discovered issues to appropriate sections</action>
      </allow>
      <allow file="DESIGN.md" mode="full">
        <action>Update architecture understanding</action>
        <action>Document changes since last review</action>
      </allow>
      <allow file="CLAUDE.md" mode="full">
        <action>Create or update project instructions</action>
        <action>Define AI workflow rules and guidelines</action>
        <action>Document repository-specific conventions</action>
      </allow>
    </write>
  </permissions>
  
  <restrictions>
    <forbid>Modify any source code files</forbid>
    <forbid>Modify configuration files (.json, .yaml, etc.)</forbid>
    <forbid>Install, update, or remove dependencies</forbid>
    <forbid>Change the current workflow phase</forbid>
  </restrictions>
  
  <file-specifications>
    <file name="TODO.md">
      <purpose>Track and audit task completion status</purpose>
      <format>- [ ] Active task / - [x] [COMPLETED] Finished task</format>
      <actions>Mark existing items only, no new additions</actions>
    </file>
    <file name="QUALITY.md">
      <purpose>Document code issues and track resolutions</purpose>
      <format>## Critical Issues / ## High Priority / ## Technical Debt</format>
      <actions>Mark [RESOLVED] items, add new issues</actions>
    </file>
    <file name="DESIGN.md">
      <purpose>Document architecture and design understanding</purpose>
      <format>## Architecture Overview / ## Key Components / ## Data Flow / ## Interface Contracts</format>
      <actions>Update with current understanding</actions>
    </file>
    <file name="CLAUDE.md">
      <purpose>Project instructions and AI guidance for Claude Code</purpose>
      <format># CLAUDE.md / ## Repository Overview / ## Common Commands</format>
      <actions>Create or update with project-specific guidance</actions>
    </file>
  </file-specifications>
  
  <phase-transition>
    <completion-criteria>
      <criterion>All existing TODOs reviewed and marked</criterion>
      <criterion>All quality issues assessed and marked</criterion>
      <criterion>New issues documented in QUALITY.md</criterion>
      <criterion>Architecture understanding updated in DESIGN.md</criterion>
      <criterion>CLAUDE.md created or updated with project guidance</criterion>
    </completion-criteria>
    <next-phase>
      <condition>When audit is complete and new issues are documented</condition>
      <suggestion>Request USER to switch to PLAN phase: echo "plan" > .claude/current_phase</suggestion>
    </next-phase>
  </phase-transition>
  
  <workflow-rules enforce="always">
    <rule id="1">Display all rules at the beginning of EVERY response</rule>
    <rule id="2" immutable="true">AI FORBIDDEN from modifying phase. User controls only</rule>
    <rule id="3" phase="EXPLORE">Read-only + TODO.md/QUALITY.md/DESIGN.md writes allowed</rule>
    <rule id="4" phase="PLAN">Markdown files only</rule>
    <rule id="5" phase="TESTDESIGN">Test files + markdown only</rule>
    <rule id="6" phase="CODE">Source code writing permitted</rule>
    <rule id="7" phase="SANDBOX">All operations confined to temp/ directory</rule>
  </workflow-rules>
  
  <command>Awaiting further instructions</command>
</task>

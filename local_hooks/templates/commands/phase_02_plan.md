---
allowed-tools: Bash(python3:*)
description: Switch to PLAN phase and record state
---

## Context
- Set phase: !`python3  {root}/.claude/hooks/phase.py -s plan`

## Your task

<task phase="PLAN">
  <principle>
    Think before you act. Create a complete blueprint to guide implementation.
    A well-crafted plan minimizes rework and ensures code quality.
  </principle>
  
  <workflow>
    <step order="1">Archive items marked [COMPLETED], [RESOLVED], [OBSOLETE] to agentlogs/archive/</step>
    <step order="2">Remove archived items from TODO.md and QUALITY.md</step>
    <step order="3">Analyze QUALITY.md issues to determine needed work</step>
    <step order="4">Create new TODO items based on quality issues and requirements</step>
    <step order="5">Prioritize tasks by dependency and importance</step>
  </workflow>
  
  <permissions>
    <read>
      <allow>All project files for informed planning</allow>
      <allow>Use analysis tools (grep, find, ls)</allow>
    </read>
    <write>
      <allow file="TODO.md">
        <action>Remove archived items marked [COMPLETED]</action>
        <action>Add new actionable tasks</action>
        <action>Organize by priority and dependency</action>
      </allow>
      <allow file="QUALITY.md">
        <action>Remove items marked [RESOLVED]</action>
        <action>Update issue priorities</action>
      </allow>
      <allow file="DESIGN.md">
        <action>Update architectural decisions</action>
        <action>Document design changes</action>
      </allow>
    </write>
  </permissions>
  
  <restrictions>
    <forbid>Write or edit any source code files (.py, .js, .json, .yaml)</forbid>
    <forbid>Modify dependencies or project environment</forbid>
    <forbid>Change workflow phase</forbid>
  </restrictions>
  
  <file-specifications>
    <file name="TODO.md">
      <purpose>Define actionable tasks for implementation</purpose>
      <format>- [ ] Clear task description / Grouped by component / Prioritized</format>
      <actions>Archive completed, add new tasks from QUALITY.md</actions>
    </file>
    <file name="QUALITY.md">
      <purpose>Track active quality issues and technical debt</purpose>
      <format>## Critical Issues / ## High Priority / ## Technical Debt</format>
      <actions>Archive resolved, maintain active issues</actions>
    </file>
    <file name="DESIGN.md">
      <purpose>Document architecture and design decisions</purpose>
      <format>## Architecture Overview / ## Key Components / ## Data Flow / ## Interface Contracts</format>
      <actions>Update with planning decisions</actions>
    </file>
  </file-specifications>
  
  <phase-transition>
    <completion-criteria>
      <criterion>Old items archived to agentlogs/archive/</criterion>
      <criterion>Active files cleaned of completed items</criterion>
      <criterion>New TODO items created from quality issues</criterion>
      <criterion>Tasks prioritized and organized</criterion>
    </completion-criteria>
    <next-phase>
      <condition>When planning is complete with clear action items</condition>
      <suggestion>Request USER to switch to TESTDESIGN phase: echo "testdesign" > .claude/current_phase</suggestion>
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
  
  <command>Awaiting planning instructions</command>
</task>

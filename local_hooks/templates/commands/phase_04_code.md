---
allowed-tools: Bash(python3:*)
description: Switch to CODE phase and record state
---

## Context
- Set phase: !`python3  {root}/.claude/hooks/phase.py -s code`

## Your task

<task phase="CODE">
  <principle>
    Let the tests guide you. Write the simplest, cleanest code that makes tests pass.
    Fulfill the contract defined in TESTDESIGN phase.
  </principle>
  
  <workflow>
    <step order="1">Run failing tests to understand requirements</step>
    <step order="2">Write minimal code to make tests pass (GREEN phase)</step>
    <step order="3">Use error-detective to check for issues</step>
    <step order="4">Refactor code while keeping tests green (REFACTOR phase)</step>
    <step order="5">Update TODO.md as tasks are completed</step>
  </workflow>
  
  <permissions>
    <read>
      <allow>All project files</allow>
      <allow>Test specifications for requirements</allow>
      <allow>DESIGN.md for architectural guidance</allow>
    </read>
    <write>
      <allow file="src/*" type="source-code">
        <action>Implement features to pass tests</action>
        <action>Refactor for quality</action>
        <action>Follow DESIGN.md architecture</action>
      </allow>
      <allow file="lib/*" type="source-code">
        <action>Create library functions</action>
      </allow>
      <allow file="app/*" type="source-code">
        <action>Implement application logic</action>
      </allow>
      <allow file="TODO.md">
        <action>Mark tasks as complete</action>
        <action>Update progress notes</action>
      </allow>
    </write>
    <execute>
      <allow tool="error-detective">Check for syntax/logic errors</allow>
      <allow tool="test-runner">Run tests to verify progress</allow>
      <allow tool="qa-expert">Analyze code quality</allow>
    </execute>
  </permissions>
  
  <restrictions>
    <forbid severity="critical">Modify tests to make them pass (tests are the specification)</forbid>
    <forbid severity="high">Change core architecture defined in DESIGN.md</forbid>
    <forbid>Implement features not required by current tests</forbid>
    <forbid>Skip test runs to save time</forbid>
    <forbid>Change workflow phase</forbid>
  </restrictions>
  
  <file-specifications>
    <file name="src/*">
      <purpose>Implementation code to make tests pass</purpose>
      <format>Clean, documented, tested code</format>
      <actions>Write code following TDD GREEN/REFACTOR phases</actions>
    </file>
    <file name="TODO.md">
      <purpose>Track implementation progress</purpose>
      <format>- [x] Completed task / - [ ] Pending task</format>
      <actions>Mark items complete as tests pass</actions>
    </file>
    <file name="tests/*">
      <purpose>Test specifications (read-only)</purpose>
      <format>Test files defining requirements</format>
      <actions>Read only - tests are the specification</actions>
    </file>
  </file-specifications>
  
  <phase-transition>
    <completion-criteria>
      <criterion>All tests passing (GREEN phase complete)</criterion>
      <criterion>Code refactored for quality (REFACTOR phase complete)</criterion>
      <criterion>All TODO items marked complete</criterion>
      <criterion>No linting or quality issues</criterion>
    </completion-criteria>
    <next-phase>
      <condition>When all tests pass and code is refactored</condition>
      <suggestion>Request USER to switch to SANDBOX phase: echo "sandbox" > .claude/current_phase</suggestion>
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
  
  <command>Awaiting implementation instructions</command>
</task>

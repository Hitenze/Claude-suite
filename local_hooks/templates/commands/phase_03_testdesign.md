---
allowed-tools: Bash(python3:*)
description: Switch to TESTDESIGN phase and record state
---

## Context
- Set phase: !`python3  {root}/.claude/hooks/phase.py -s testdesign`

## Your task

<task phase="TESTDESIGN">
  <principle>
    Define success before you build. Write tests first to create executable specifications.
    A passing test is the definition of "done."
  </principle>
  
  <workflow>
    <step order="1">Review TODO.md for features to implement</step>
    <step order="2">Write test files that define expected behavior</step>
    <step order="3">Ensure tests follow Arrange-Act-Assert pattern</step>
    <step order="4">Run tests to confirm they fail (RED phase of TDD)</step>
    <step order="5">Update TODO.md with "Make test_X pass" tasks</step>
  </workflow>
  
  <permissions>
    <read>
      <allow>All project files for context</allow>
      <allow>DESIGN.md for architecture understanding</allow>
      <allow>Existing code for interface consistency</allow>
    </read>
    <write>
      <allow file="tests/*" type="test-files">
        <action>Create new test files</action>
        <action>Define test cases and expectations</action>
        <action>Use test_*.py, *_test.py naming</action>
      </allow>
      <allow file="temp/*" type="test-files">
        <action>Create test files in temp/ if needed</action>
      </allow>
      <allow file="TODO.md">
        <action>Mark planning tasks complete</action>
        <action>Add "Make test_X pass" implementation tasks</action>
      </allow>
    </write>
  </permissions>
  
  <restrictions>
    <forbid severity="critical">Write or modify implementation code (src/, lib/, app/)</forbid>
    <forbid>Modify dependencies or environment</forbid>
    <forbid>Change workflow phase</forbid>
    <forbid>Make tests pass (that's for CODE phase)</forbid>
  </restrictions>
  
  <file-specifications>
    <file name="tests/*.py">
      <purpose>Define expected behavior through tests</purpose>
      <format>def test_feature(): arrange, act, assert</format>
      <actions>Create failing tests that specify requirements</actions>
    </file>
    <file name="TODO.md">
      <purpose>Track test creation and implementation tasks</purpose>
      <format>- [ ] Make test_feature pass</format>
      <actions>Update with specific test-passing tasks</actions>
    </file>
    <file name="DESIGN.md">
      <purpose>Reference for test design decisions</purpose>
      <format>Read-only reference</format>
      <actions>Read only for context</actions>
    </file>
  </file-specifications>
  
  <phase-transition>
    <completion-criteria>
      <criterion>All TODO items have corresponding tests</criterion>
      <criterion>All tests written and confirmed failing</criterion>
      <criterion>Test coverage includes edge cases</criterion>
      <criterion>TODO.md updated with implementation tasks</criterion>
    </completion-criteria>
    <next-phase>
      <condition>When all tests are written and failing (RED phase complete)</condition>
      <suggestion>Request USER to switch to CODE phase: echo "code" > .claude/current_phase</suggestion>
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
  
  <command>Awaiting test design instructions</command>
</task>

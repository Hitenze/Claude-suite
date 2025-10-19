---
allowed-tools: Bash(python3:*)
description: Switch to SANDBOX phase and record state
---

## Context
- Set phase: !`python3  {root}/.claude/hooks/phase.py -s sandbox`

## Your task

<task phase="SANDBOX">
  <principle>
    Verify and experiment in isolation. A safe environment for integration testing 
    and experimentation without risk to the main codebase. Everything here is temporary.
  </principle>
  
  <workflow>
    <step order="1">Create temp/ directory structure for testing</step>
    <step order="2">Copy necessary files to temp/ if needed</step>
    <step order="3">Run integration tests and experiments</step>
    <step order="4">Generate sample outputs and logs</step>
    <step order="5">Document findings and recommendations</step>
  </workflow>
  
  <permissions>
    <read>
      <allow>All project files (read-only)</allow>
      <allow>Source code from src/</allow>
      <allow>Test files from tests/</allow>
    </read>
    <write>
      <allow file="temp/*" scope="full-control">
        <action>Create any files and directories</action>
        <action>Generate test data and outputs</action>
        <action>Write logs and results</action>
      </allow>
    </write>
    <execute>
      <allow>Run application with test data</allow>
      <allow>Execute integration tests</allow>
      <allow>Run performance benchmarks</allow>
    </execute>
  </permissions>
  
  <restrictions>
    <forbid severity="critical">Write operations outside temp/ directory</forbid>
    <forbid severity="critical">Modify source code, tests, or documentation</forbid>
    <forbid>Change workflow phase</forbid>
    <forbid>Commit or push any changes</forbid>
  </restrictions>
  
  <file-specifications>
    <file name="temp/logs/*">
      <purpose>Capture test execution logs</purpose>
      <format>Timestamped log entries</format>
      <actions>Write test results and debug information</actions>
    </file>
    <file name="temp/output/*">
      <purpose>Store example outputs and results</purpose>
      <format>Sample data demonstrating functionality</format>
      <actions>Generate example usage scenarios</actions>
    </file>
    <file name="temp/data/*">
      <purpose>Test data and configurations</purpose>
      <format>Mock data for testing</format>
      <actions>Create test datasets</actions>
    </file>
  </file-specifications>
  
  <phase-transition>
    <completion-criteria>
      <criterion>Integration tests executed successfully</criterion>
      <criterion>Key scenarios validated</criterion>
      <criterion>Performance benchmarks completed</criterion>
      <criterion>Findings documented</criterion>
    </completion-criteria>
    <next-phase>
      <condition>When testing is complete and results documented</condition>
      <suggestion>Request USER to switch to EXPLORE for next iteration: echo "explore" > .claude/current_phase</suggestion>
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
  
  <command>Awaiting sandbox instructions</command>
</task>

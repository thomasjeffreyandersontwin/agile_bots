# 📄 Generate Command Definitions

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Generator
**Path:** [🎯 Build Agile Bots](../..) / [⚙️ Generate CLI](.)  
**Sequential Order:** 0.0
**Story Type:** user

## Story Description

Generate Command Definitions functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** generator runs,
  **then** Orchestrator walks all bot behaviors

- **When** behaviors are walked,
  **then** ActionDataCollector gathers action metadata for each behavior

- **When** actions are gathered,
  **then** generator extracts parameters from each action's context_class

- **When** metadata is collected,
  **then** ReplCommandVisitor generates navigate commands for all behaviors and actions

- **When** commands are generated,
  **then** scope commands are created for scope.type, scope.value, scope.exclude

- **When** all commands are defined,
  **then** generator outputs command definition file

## Scenarios

### Scenario: Generate Command Definitions (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```

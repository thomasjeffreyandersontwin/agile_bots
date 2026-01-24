# 📄 Get Action Instructions Through CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Prepare Common Instructions For Behavior, Action, and Scope](.)  
**Sequential Order:** 1.0
**Story Type:** user

## Story Description

Get Action Instructions Through CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** user navigates to behavior.action.instructions
  **then** CLI displays formatted instructions for that action

- **When** user enters action name only as shortcut
  **then** CLI executes instructions on current behavior's action

## Scenarios

<a id="scenario-user-gets-instructions-using-full-path"></a>
### Scenario: [User gets instructions using full path](#scenario-user-gets-instructions-using-full-path) ()

**Steps:**
```gherkin
GIVEN: CLI is at shape.build.instructions
WHEN: user enters 'shape.build.instructions'
THEN: CLI displays formatted instructions
```


<a id="scenario-user-calls-action-by-name-shortcut"></a>
### Scenario: [User calls action by name shortcut](#scenario-user-calls-action-by-name-shortcut) ()

**Steps:**
```gherkin
GIVEN: CLI is at shape.build.instructions
WHEN: user enters just 'build'
THEN: CLI executes instructions operation on current behavior's build action
```


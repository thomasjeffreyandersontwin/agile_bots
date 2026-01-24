# 📄 Display Current Position in CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** CLI
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Navigate Behavior Actions](..) / [⚙️ Display Behavior Action State](.)  
**Sequential Order:** 2.0
**Story Type:** system

## Story Description

Display Current Position in CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** user views status
  **then** CLI displays current behavior, action, and operation

- **When** user navigates to different action
  **then** CLI updates current position display

- **When** displaying position
  **then** CLI shows behavior.action.operation format

- **When** position is at first action
  **then** CLI indicates start of workflow

## Scenarios

<a id="scenario-user-views-current-position-in-status"></a>
### Scenario: [User views current position in status](#scenario-user-views-current-position-in-status) ()

**Steps:**
```gherkin
GIVEN: CLI is at <behavior>.<action>.<operation>
WHEN: user enters 'status'
THEN: CLI displays current position
```


<a id="scenario-current-position-updates-after-navigation"></a>
### Scenario: [Current position updates after navigation](#scenario-current-position-updates-after-navigation) ()

**Steps:**
```gherkin
GIVEN: CLI is at shape.clarify.instructions
WHEN: user navigates to discovery behavior
THEN: CLI updates current position display to show discovery
```


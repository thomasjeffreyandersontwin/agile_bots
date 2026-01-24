# 📄 Display Action Help Using CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Get Help](.)  
**Sequential Order:** 2.0
**Story Type:** user

## Story Description

Display Action Help Using CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** user enters help command
  **then** CLI displays available commands
  **and** their descriptions

- **When** user requests help for specific action
  **then** CLI displays detailed help for that action

- **When** displaying help
  **then** CLI shows command syntax
  **and** parameter descriptions

- **When** help is requested for non-existent command
  **then** CLI displays error message with available commands

## Scenarios

<a id="scenario-user-views-all-available-commands"></a>
### Scenario: [User views all available commands](#scenario-user-views-all-available-commands) ()

**Steps:**
```gherkin
GIVEN: CLI is running
WHEN: user enters 'help'
THEN: CLI displays help menu with commands
```


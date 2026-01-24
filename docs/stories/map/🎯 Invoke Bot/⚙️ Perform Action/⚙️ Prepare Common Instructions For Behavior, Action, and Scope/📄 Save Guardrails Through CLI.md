# 📄 Save Guardrails Through CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Prepare Common Instructions For Behavior, Action, and Scope](.)  
**Sequential Order:** 8.0
**Story Type:** user

## Story Description

Save Guardrails Through CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** user runs save command with answers parameter

  **then** CLI saves answers to clarification.json under current behavior

  **and** CLI merges with existing answers

- **When** user runs save command with decisions parameter

  **then** CLI saves decisions to strategy.json under current behavior

## Scenarios

<a id="scenario-save-answers-via-cli-command"></a>
### Scenario: [Save answers via CLI command](#scenario-save-answers-via-cli-command) ()

**Steps:**
```gherkin
GIVEN: CLI is at shape.clarify
WHEN: user runs 'save --answers {"What is the scope?": "Bot system"}'
THEN: CLI shows success message
AND: clarification.json is updated
```


<a id="scenario-save-decisions-via-cli-command"></a>
### Scenario: [Save decisions via CLI command](#scenario-save-decisions-via-cli-command) ()

**Steps:**
```gherkin
GIVEN: CLI is at shape.strategy
WHEN: user runs 'save --decisions {"drill_down": "Deep"}'
THEN: CLI shows success message
AND: strategy.json is updated
```


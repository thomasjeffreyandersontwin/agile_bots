# 📄 Confirm Action Completion Through CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through REPL](..) / [⚙️ Display Action Instructions Using REPL](..) / [⚙️ Display Common Instructions Through REPL](.)  
**Sequential Order:** 2
**Story Type:** user

## Story Description

Confirm Action Completion Through CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-user-confirms-action-completion"></a>
### Scenario: [User confirms action completion](#scenario-user-confirms-action-completion) (happy_path)

**Steps:**
```gherkin
GIVEN: CLI is at shape.build.instructions
WHEN: user enters 'confirm'
THEN: CLI advances to next action
```


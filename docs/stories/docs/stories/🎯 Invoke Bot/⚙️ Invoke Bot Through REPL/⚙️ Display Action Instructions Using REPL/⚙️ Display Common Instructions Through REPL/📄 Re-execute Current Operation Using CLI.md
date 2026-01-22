# 📄 Re-execute Current Operation Using CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through REPL](..) / [⚙️ Display Action Instructions Using REPL](..) / [⚙️ Display Common Instructions Through REPL](.)  
**Sequential Order:** 3
**Story Type:** user

## Story Description

Re-execute Current Operation Using CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-user-re-executes-current-instructions"></a>
### Scenario: [User re-executes current instructions](#scenario-user-re-executes-current-instructions) (happy_path)

**Steps:**
```gherkin
GIVEN: CLI is at shape.build.instructions
WHEN: user enters 'current'
THEN: CLI re-executes current instructions
```


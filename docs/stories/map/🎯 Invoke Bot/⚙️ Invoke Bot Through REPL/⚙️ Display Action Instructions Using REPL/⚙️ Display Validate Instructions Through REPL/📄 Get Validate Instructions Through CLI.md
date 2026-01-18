# 📄 Get Validate Instructions Through CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through REPL](..) / [⚙️ Display Action Instructions Using REPL](..) / [⚙️ Display Validate Instructions Through REPL](.)  
**Sequential Order:** 3
**Story Type:** user

## Story Description

Get Validate Instructions Through CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-get-validate-instructions-with-rules"></a>
### Scenario: [Get validate instructions with rules](#scenario-get-validate-instructions-with-rules) (happy_path)

**Steps:**
```gherkin
GIVEN: CLI is at shape.validate.instructions
WHEN: user enters 'shape.validate.instructions'
THEN: CLI displays validation rules and scanners
```


# 📄 Display Validation Results Through CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through REPL](..) / [⚙️ Display Action Instructions Using REPL](..) / [⚙️ Display Validate Instructions Through REPL](.)  
**Sequential Order:** 2
**Story Type:** user

## Story Description

Display Validation Results Through CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-display-validation-violations"></a>
### Scenario: [Display validation violations](#scenario-display-validation-violations) (happy_path)

**Steps:**
```gherkin
GIVEN: Validation has run
WHEN: user views validate instructions
THEN: CLI displays violation report
```


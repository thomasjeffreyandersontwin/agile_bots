# 📄 Get Clarify Instructions Through CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through REPL](..) / [⚙️ Display Action Instructions Using REPL](..) / [⚙️ Display Clarify Instructions Through REPL](.)  
**Sequential Order:** 3
**Story Type:** user

## Story Description

Get Clarify Instructions Through CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-get-clarify-instructions-with-questions"></a>
### Scenario: [Get clarify instructions with questions](#scenario-get-clarify-instructions-with-questions) (happy_path)

**Steps:**
```gherkin
GIVEN: CLI is at shape.clarify.instructions
WHEN: user enters 'shape.clarify.instructions'
THEN: CLI displays key questions and required evidence
```


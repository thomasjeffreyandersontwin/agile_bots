# 📄 Display Guardrails Through CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through REPL](..) / [⚙️ Display Action Instructions Using REPL](..) / [⚙️ Display Clarify Instructions Through REPL](.)  
**Sequential Order:** 2
**Story Type:** user

## Story Description

Display Guardrails Through CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-display-key-questions-from-guardrails"></a>
### Scenario: [Display key questions from guardrails](#scenario-display-key-questions-from-guardrails) (happy_path)

**Steps:**
```gherkin
GIVEN: CLI is at shape.clarify.instructions
WHEN: instructions are displayed
THEN: CLI shows key questions from guardrails
```


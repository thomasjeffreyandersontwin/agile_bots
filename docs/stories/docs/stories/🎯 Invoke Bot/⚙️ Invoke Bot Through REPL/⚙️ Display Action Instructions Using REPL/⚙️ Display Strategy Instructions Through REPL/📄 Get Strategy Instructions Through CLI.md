# 📄 Get Strategy Instructions Through CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through REPL](..) / [⚙️ Display Action Instructions Using REPL](..) / [⚙️ Display Strategy Instructions Through REPL](.)  
**Sequential Order:** 2
**Story Type:** user

## Story Description

Get Strategy Instructions Through CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-get-strategy-instructions-with-criteria"></a>
### Scenario: [Get strategy instructions with criteria](#scenario-get-strategy-instructions-with-criteria) (happy_path)

**Steps:**
```gherkin
GIVEN: CLI is at shape.strategy.instructions
WHEN: user enters 'shape.strategy.instructions'
THEN: CLI displays planning criteria and assumptions
```


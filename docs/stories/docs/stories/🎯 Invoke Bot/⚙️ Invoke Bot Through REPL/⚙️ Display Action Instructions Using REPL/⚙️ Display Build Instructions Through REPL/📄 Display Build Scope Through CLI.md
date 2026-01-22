# 📄 Display Build Scope Through CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through REPL](..) / [⚙️ Display Action Instructions Using REPL](..) / [⚙️ Display Build Instructions Through REPL](.)  
**Sequential Order:** 2
**Story Type:** user

## Story Description

Display Build Scope Through CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-display-active-build-scope"></a>
### Scenario: [Display active build scope](#scenario-display-active-build-scope) (happy_path)

**Steps:**
```gherkin
GIVEN: Build scope is set
WHEN: user views build instructions
THEN: CLI displays active scope filter
```


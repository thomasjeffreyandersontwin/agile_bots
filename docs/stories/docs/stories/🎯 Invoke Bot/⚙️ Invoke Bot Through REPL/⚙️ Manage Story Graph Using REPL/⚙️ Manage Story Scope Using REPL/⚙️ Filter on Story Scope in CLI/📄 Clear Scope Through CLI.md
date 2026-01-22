# 📄 Clear Scope Through CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through REPL](..) / [⚙️ Manage Story Graph Using REPL](../..) / [⚙️ Manage Story Scope Using REPL](..) / [⚙️ Filter on Story Scope in CLI](.)  
**Sequential Order:** 5
**Story Type:** user

## Story Description

Clear Scope Through CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-user-clears-all-scope-filters"></a>
### Scenario: [User clears all scope filters](#scenario-user-clears-all-scope-filters) (happy_path)

**Steps:**
```gherkin
GIVEN: CLI is at shape.build.instructions
AND: active scope filters are story="Story1" AND files="docs/**/*.md"
WHEN: user enters 'scope clear'
THEN: REPLSession clears all scope filters from context
AND: CLI displays 'All scope filters cleared'
AND: StatusDisplay shows no active scope
```


<a id="scenario-user-executes-build-after-clearing-scope"></a>
### Scenario: [User executes build after clearing scope](#scenario-user-executes-build-after-clearing-scope) (happy_path)

**Steps:**
```gherkin
GIVEN: CLI is at shape.build.instructions
AND: user has cleared all scope filters
WHEN: user enters 'shape.build.instructions'
THEN: CLIAction passes no scope filters to action
AND: CLI displays unfiltered instructions
```


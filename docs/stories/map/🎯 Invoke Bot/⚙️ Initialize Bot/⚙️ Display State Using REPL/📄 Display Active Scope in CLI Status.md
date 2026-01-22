# 📄 Display Active Scope in CLI Status

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** CLI
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Initialize Bot](..) / [⚙️ Display State Using REPL](.)  
**Sequential Order:** 4.0
**Story Type:** system

## Story Description

Display Active Scope in CLI Status functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** user views status with active scope
  **then** CLI displays active scope section

- **When** no scope is active
  **then** CLI displays no active scope filters message

- **When** multiple scope filters are active
  **then** CLI displays all active filters

- **When** scope is cleared
  **then** CLI updates status to show no active scope

## Scenarios

<a id="scenario-user-views-active-scope-in-status"></a>
### Scenario: [User views active scope in status](#scenario-user-views-active-scope-in-status) ()

**Steps:**
```gherkin
GIVEN: CLI is at shape.build.instructions
WHEN: user enters 'status'
THEN: CLI displays active scope section
```


<a id="scenario-status-shows-no-active-scope-when-cleared"></a>
### Scenario: [Status shows no active scope when cleared](#scenario-status-shows-no-active-scope-when-cleared) ()

**Steps:**
```gherkin
GIVEN: CLI is at shape.build.instructions
WHEN: user enters 'status'
THEN: CLI displays 'No active scope filters'
```


<a id="scenario-status-shows-combined-scope-filters"></a>
### Scenario: [Status shows combined scope filters](#scenario-status-shows-combined-scope-filters) ()

**Steps:**
```gherkin
GIVEN: CLI is at code.validate.instructions
WHEN: user enters 'status'
THEN: CLI displays both knowledge graph and files scope
```


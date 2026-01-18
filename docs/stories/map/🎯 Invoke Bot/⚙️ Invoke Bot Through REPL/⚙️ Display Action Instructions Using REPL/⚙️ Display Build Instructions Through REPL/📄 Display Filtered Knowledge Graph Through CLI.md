# 📄 Display Filtered Knowledge Graph Through CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through REPL](..) / [⚙️ Display Action Instructions Using REPL](..) / [⚙️ Display Build Instructions Through REPL](.)  
**Sequential Order:** 3
**Story Type:** user

## Story Description

Display Filtered Knowledge Graph Through CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-display-knowledge-graph-with-scope-filter"></a>
### Scenario: [Display knowledge graph with scope filter](#scenario-display-knowledge-graph-with-scope-filter) (happy_path)

**Steps:**
```gherkin
GIVEN: Scope filter is active
WHEN: user views build instructions
THEN: CLI displays filtered knowledge graph
```


# 📄 View Current Scope in CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Manage Story Graph](..) / [⚙️ Manage Story Graph Using REPL](../..) / [⚙️ Manage Story Scope Using REPL](..) / [⚙️ Filter on Story Scope in CLI](.)  
**Sequential Order:** 4.0
**Story Type:** user

## Story Description

View Current Scope in CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** user enters 'scope' command with no filters set
  **then** CLI displays "No scope filters active"

- **When** user enters 'scope' command with story scope set
  **then** CLI displays active story scope filter

- **When** user enters 'scope' command with file scope set
  **then** CLI displays active file scope filter

## Scenarios

<a id="scenario-view-scope-with-no-filters-set"></a>
### Scenario: [View scope with no filters set](#scenario-view-scope-with-no-filters-set) ()

**Steps:**
```gherkin
GIVEN: CLI is initialized with no scope filters
WHEN: user enters 'scope' command
THEN: CLI displays "No scope filters active"
```


<a id="scenario-view-story-scope-filter"></a>
### Scenario: [View story scope filter](#scenario-view-story-scope-filter) ()

**Steps:**
```gherkin
GIVEN: Story scope filter is set to "Story1"
WHEN: user enters 'scope' command
THEN: CLI displays active story scope filter
```


<a id="scenario-view-file-scope-filter"></a>
### Scenario: [View file scope filter](#scenario-view-file-scope-filter) ()

**Steps:**
```gherkin
GIVEN: File scope filter is set to "*.py"
WHEN: user enters 'scope' command
THEN: CLI displays active file scope filter
```


# 📄 Filter Scope By Stories Using CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Work With Story Map](..) / [⚙️ Scope Stories](..) / [⚙️ Filter Scope of Stories](.)  
**Sequential Order:** 1.0
**Story Type:** user

## Story Description

Filter Scope By Stories Using CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-scope-all-returns-all-stories-via-cli"></a>
### Scenario: [Scope 'all' returns all stories via CLI](#scenario-scope-all-returns-all-stories-via-cli) (happy_path)

**Steps:**
```gherkin
GIVEN: CLI session with story graph
WHEN: scope set to 'all'
THEN: All stories accessible
```


<a id="scenario-scope-single-story-via-cli"></a>
### Scenario: [Scope single story via CLI](#scenario-scope-single-story-via-cli) (happy_path)

**Steps:**
```gherkin
GIVEN: CLI session
WHEN: scope set to single story
THEN: Only specified story in scope
```


<a id="scenario-scope-single-epic-via-cli"></a>
### Scenario: [Scope single epic via CLI](#scenario-scope-single-epic-via-cli) (happy_path)

**Steps:**
```gherkin
GIVEN: CLI session
WHEN: scope set to single epic
THEN: Only specified epic in scope
```


<a id="scenario-scope-by-increment-priority-via-cli"></a>
### Scenario: [Scope by increment priority via CLI](#scenario-scope-by-increment-priority-via-cli) (happy_path)

**Steps:**
```gherkin
GIVEN: CLI session
WHEN: scope set to increment priority
THEN: Only specified increment in scope
```


<a id="scenario-scope-by-increment-name-via-cli"></a>
### Scenario: [Scope by increment name via CLI](#scenario-scope-by-increment-name-via-cli) (happy_path)

**Steps:**
```gherkin
GIVEN: CLI session
WHEN: scope set to increment name
THEN: Only specified increment in scope
```


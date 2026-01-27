# 📄 Filter Story Scope By Stories

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Work With Story Map](..) / [⚙️ Scope Stories](..) / [⚙️ Filter Scope of Stories](.)  
**Sequential Order:** 0.0
**Story Type:** user

## Story Description

Filter Story Scope By Stories functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-filter-returns-all-when-scope-is-all"></a>
### Scenario: [Filter returns all when scope is all](#scenario-filter-returns-all-when-scope-is-all) (happy_path)

**Steps:**
```gherkin
Given Story graph with multiple epics and increments
When Filter with scope type 'all'
Then Story graph contains all epics and increments
```


<a id="scenario-filter-by-single-story-name-returns-matching-story"></a>
### Scenario: [Filter by single story name returns matching story](#scenario-filter-by-single-story-name-returns-matching-story) (happy_path)

**Steps:**
```gherkin
Given Story graph with multiple stories
When Filter with single story name
Then Story graph contains only matching story and its parent epic
```


<a id="scenario-filter-by-single-epic-name-returns-matching-epic"></a>
### Scenario: [Filter by single epic name returns matching epic](#scenario-filter-by-single-epic-name-returns-matching-epic) (happy_path)

**Steps:**
```gherkin
Given Story graph with multiple epics
When Filter with single epic name
Then Story graph contains only matching epic and its increments
```


<a id="scenario-filter-by-increment-priorities-returns-matching-increments"></a>
### Scenario: [Filter by increment priorities returns matching increments](#scenario-filter-by-increment-priorities-returns-matching-increments) (happy_path)

**Steps:**
```gherkin
Given Story graph with increments having different priorities
When Filter with increment priorities
Then Story graph contains only matching increments and their stories
```


<a id="scenario-filter-by-increment-names-returns-matching-increments"></a>
### Scenario: [Filter by increment names returns matching increments](#scenario-filter-by-increment-names-returns-matching-increments) (happy_path)

**Steps:**
```gherkin
Given Story graph with increments having different names
When Filter with increment names
Then Story graph contains only matching increments and their stories
```


<a id="scenario-filter-returns-parent-epic-when-child-story-matches"></a>
### Scenario: [Filter returns parent epic when child story matches](#scenario-filter-returns-parent-epic-when-child-story-matches) (happy_path)

**Steps:**
```gherkin
Given Story graph with epic containing story
When Scope set to story name
Then Story and parent epic are both returned
```


# 📄 Clear Scope

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Work With Story Map](..) / [⚙️ Scope Stories](..) / [⚙️ Manage Story Scope](.)  
**Sequential Order:** 3.0
**Story Type:** user

## Story Description

Clear Scope functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-clear-scope-with-show_all-parameter"></a>
### Scenario: [Clear scope with show_all parameter](#scenario-clear-scope-with-show_all-parameter) (happy_path)

**Steps:**
```gherkin
Given Bot with scope set
When Scope cleared with show_all=True
Then Scope is cleared and all content is shown
```


<a id="scenario-clear-scope-without-show_all-parameter"></a>
### Scenario: [Clear scope without show_all parameter](#scenario-clear-scope-without-show_all-parameter) (happy_path)

**Steps:**
```gherkin
Given Bot with scope set
When Scope cleared without show_all parameter
Then Scope is cleared
```


<a id="scenario-actions-after-clear-process-all-content"></a>
### Scenario: [Actions after clear process all content](#scenario-actions-after-clear-process-all-content) (happy_path)

**Steps:**
```gherkin
Given Bot had scope set, then cleared
When Action executes
Then Action processes all content without filtering
```


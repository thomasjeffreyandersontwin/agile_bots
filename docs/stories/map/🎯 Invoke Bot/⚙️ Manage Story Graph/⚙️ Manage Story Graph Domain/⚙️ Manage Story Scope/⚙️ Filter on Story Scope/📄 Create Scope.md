# 📄 Create Scope

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Manage Story Graph](..) / [⚙️ Manage Story Graph Domain](../..) / [⚙️ Manage Story Scope](..) / [⚙️ Filter on Story Scope](.)  
**Sequential Order:** 999.0
**Story Type:** user

## Story Description

Create Scope functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-scope-created-with-different-parameter-combinations"></a>
### Scenario: [Scope created with different parameter combinations](#scenario-scope-created-with-different-parameter-combinations) (happy_path)

**Steps:**
```gherkin
Given Parameters dict with scope configuration
When ActionScope instantiated with parameters
Then ActionScope scope property returns expected configuration
```


<a id="scenario-scope-defaults-to-all-when-no-parameters-provided"></a>
### Scenario: [Scope defaults to 'all' when no parameters provided](#scenario-scope-defaults-to-all-when-no-parameters-provided) (happy_path)

**Steps:**
```gherkin
Given Empty parameters dict
When ActionScope instantiated
Then Scope defaults to 'all'
```


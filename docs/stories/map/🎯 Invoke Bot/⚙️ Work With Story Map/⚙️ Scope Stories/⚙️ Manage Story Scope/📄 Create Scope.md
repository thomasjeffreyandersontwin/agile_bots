# 📄 Create Scope

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L149)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Work With Story Map](..) / [⚙️ Scope Stories](..) / [⚙️ Manage Story Scope](.)  
**Sequential Order:** 0.0
**Story Type:** user

## Story Description

Create Scope functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-scope-created-with-different-parameter-combinations"></a>
### Scenario: [Scope created with different parameter combinations](#scenario-scope-created-with-different-parameter-combinations) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L171)

**Steps:**
```gherkin
GIVEN: Parameters dict with scope configuration
WHEN: ActionScope instantiated with parameters
THEN: ActionScope scope property returns expected configuration
```


<a id="scenario-scope-defaults-to-all-when-no-parameters-provided"></a>
### Scenario: [Scope defaults to 'all' when no parameters provided](#scenario-scope-defaults-to-all-when-no-parameters-provided) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L184)

**Steps:**
```gherkin
GIVEN: Empty parameters dict
WHEN: ActionScope instantiated
THEN: Scope defaults to 'all'
```


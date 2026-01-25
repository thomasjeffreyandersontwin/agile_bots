# 📄 Clear Scope

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L82)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Filter Scope](../..) / [⚙️ Scope Stories](..) / [⚙️ Manage Story Scope](.)  
**Sequential Order:** 3.0
**Story Type:** user

## Story Description

Clear Scope functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-clear-scope-with-show_all-parameter"></a>
### Scenario: [Clear scope with show_all parameter](#scenario-clear-scope-with-show_all-parameter) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L84)

**Steps:**
```gherkin
Given Bot with scope set
When Scope cleared with show_all=True
Then Scope is cleared and all content is shown
```


<a id="scenario-clear-scope-without-show_all-parameter"></a>
### Scenario: [Clear scope without show_all parameter](#scenario-clear-scope-without-show_all-parameter) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L94)

**Steps:**
```gherkin
Given Bot with scope set
When Scope cleared without show_all parameter
Then Scope is cleared
```


<a id="scenario-actions-after-clear-process-all-content"></a>
### Scenario: [Actions after clear process all content](#scenario-actions-after-clear-process-all-content) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L104)

**Steps:**
```gherkin
Given Bot had scope set, then cleared
When Action executes
Then Action processes all content without filtering
```


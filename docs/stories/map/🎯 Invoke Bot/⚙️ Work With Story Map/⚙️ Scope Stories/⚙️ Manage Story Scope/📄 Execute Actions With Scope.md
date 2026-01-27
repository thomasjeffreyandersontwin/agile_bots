# 📄 Execute Actions With Scope

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L203)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Work With Story Map](..) / [⚙️ Scope Stories](..) / [⚙️ Manage Story Scope](.)  
**Sequential Order:** 8.0
**Story Type:** user

## Story Description

Execute Actions With Scope functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-build-action-includes-scope-in-instructions"></a>
### Scenario: [Build action includes scope in instructions](#scenario-build-action-includes-scope-in-instructions) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L205)

**Steps:**
```gherkin
Given Build action with story scope
When Instructions are retrieved
Then Instructions contain scope configuration
```


<a id="scenario-validate-action-accepts-scope-context"></a>
### Scenario: [Validate action accepts scope context](#scenario-validate-action-accepts-scope-context) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L230)

**Steps:**
```gherkin
Given Validate action with story scope and story graph file
When Instructions are retrieved
Then No errors occur and scope is processed
```


<a id="scenario-render-action-accepts-scope-context"></a>
### Scenario: [Render action accepts scope context](#scenario-render-action-accepts-scope-context) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L261)

**Steps:**
```gherkin
Given Render action with story scope
When Instructions are retrieved
Then No errors occur (render supports ScopeActionContext)
```


<a id="scenario-clarify-action-does-not-support-scope"></a>
### Scenario: [Clarify action does not support scope](#scenario-clarify-action-does-not-support-scope) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L283)

**Steps:**
```gherkin
Given Clarify action
When Context is checked
Then Uses ClarifyActionContext (not ScopeActionContext)
```


<a id="scenario-strategy-action-does-not-support-scope"></a>
### Scenario: [Strategy action does not support scope](#scenario-strategy-action-does-not-support-scope) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L300)

**Steps:**
```gherkin
Given Strategy action
When Context is checked
Then Uses StrategyActionContext (not ScopeActionContext)
```


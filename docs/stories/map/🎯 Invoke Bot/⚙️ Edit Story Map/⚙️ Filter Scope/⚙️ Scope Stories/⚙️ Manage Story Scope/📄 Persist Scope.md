# 📄 Persist Scope

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L60)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Filter Scope](../..) / [⚙️ Scope Stories](..) / [⚙️ Manage Story Scope](.)  
**Sequential Order:** 5.0
**Story Type:** user

## Story Description

Persist Scope functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-scope-persists-across-bot-invocations"></a>
### Scenario: [Scope persists across bot invocations](#scenario-scope-persists-across-bot-invocations) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L62)

**Steps:**
```gherkin
Given Bot with scope set
When Bot is reloaded
Then Scope is restored from workflow state
```


<a id="scenario-scope-persists-after-action-execution"></a>
### Scenario: [Scope persists after action execution](#scenario-scope-persists-after-action-execution) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L72)

**Steps:**
```gherkin
Given Bot with scope set
When Action executes and completes
Then Scope remains active for next action
```


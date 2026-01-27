# 📄 Persist Scope

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Work With Story Map](..) / [⚙️ Scope Stories](..) / [⚙️ Manage Story Scope](.)  
**Sequential Order:** 6.0
**Story Type:** user

## Story Description

Persist Scope functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-scope-persists-across-bot-invocations"></a>
### Scenario: [Scope persists across bot invocations](#scenario-scope-persists-across-bot-invocations) (happy_path)

**Steps:**
```gherkin
Given Bot with scope set
When Bot is reloaded
Then Scope is restored from workflow state
```


<a id="scenario-scope-persists-after-action-execution"></a>
### Scenario: [Scope persists after action execution](#scenario-scope-persists-after-action-execution) (happy_path)

**Steps:**
```gherkin
Given Bot with scope set
When Action executes and completes
Then Scope remains active for next action
```


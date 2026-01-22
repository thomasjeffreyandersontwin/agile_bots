# 📄 Track Activity For Workspace

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke MCP](.)  
**Sequential Order:** 5.0
**Story Type:** user

## Story Description

Track Activity For Workspace functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Activity is tracked

  **then** Activity is logged to workspace area not bot area

## Scenarios

<a id="scenario-activity-logged-to-workspace_area-not-bot-area"></a>
### Scenario: [Activity logged to workspace_area not bot area](#scenario-activity-logged-to-workspace_area-not-bot-area) ()

**Steps:**
```gherkin
Given WORKING_AREA environment variable specifies workspace_area
And action 'gather_context' executes
When Activity logger creates entry
Then Activity log file is at: workspace_area/activity_log.json
And Activity log is NOT at: agile_bot/bots/story_bot/activity_log.json
And Activity log location matches workspace_area from WORKING_AREA environment variable
```


<a id="scenario-activity-log-contains-correct-entry"></a>
### Scenario: [Activity log contains correct entry](#scenario-activity-log-contains-correct-entry) ()

**Steps:**
```gherkin
Given action 'gather_context' executes in behavior 'discovery'
When Activity logger creates entry
Then Activity log entry includes:
- action_state='test_bot.discovery.gather_context'
- timestamp
- Full path includes bot_name.behavior.action
```


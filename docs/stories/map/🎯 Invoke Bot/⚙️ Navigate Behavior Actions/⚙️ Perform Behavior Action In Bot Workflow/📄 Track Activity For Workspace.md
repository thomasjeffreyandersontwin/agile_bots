# 📄 Track Activity For Workspace

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/navigate_behavior_actions/test_perform_behavior_action_in_bot_workflow.py#L149)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Navigate Behavior Actions](..) / [⚙️ Perform Behavior Action In Bot Workflow](.)  
**Sequential Order:** 4.0
**Story Type:** user

## Story Description

Track Activity For Workspace functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-activity-logged-to-workspace_area-not-bot-area"></a>
### Scenario: [Activity logged to workspace_area not bot area](#scenario-activity-logged-to-workspace_area-not-bot-area) (happy_path)  | [Test](/test/invoke_bot/navigate_behavior_actions/test_perform_behavior_action_in_bot_workflow.py#L151)

**Steps:**
```gherkin
Given WORKING_AREA environment variable specifies workspace_area
When Activity logger creates entry
Then Activity log file is at: workspace_area/activity_log.json
Then And action 'gather_context' executes
Then And Activity log is NOT at: agile_bot/bots/story_bot/activity_log.json
Then And Activity log location matches workspace_area from WORKING_AREA environment variable
```


<a id="scenario-activity-log-contains-correct-entry"></a>
### Scenario: [Activity log contains correct entry](#scenario-activity-log-contains-correct-entry) (happy_path)  | [Test](/test/invoke_bot/navigate_behavior_actions/test_perform_behavior_action_in_bot_workflow.py#L179)

**Steps:**
```gherkin
Given action 'gather_context' executes in behavior 'discovery'
When Activity logger creates entry
Then Activity log entry includes:
Then - action_state='story_bot.discovery.gather_context'
Then - timestamp
Then - Full path includes bot_name.behavior.action
```


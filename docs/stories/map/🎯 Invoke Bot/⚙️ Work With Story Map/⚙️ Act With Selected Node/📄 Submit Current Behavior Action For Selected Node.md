# 📄 Submit Current Behavior Action For Selected Node

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_submit_scoped_action.py)

**User:** System
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Work With Story Map](..) / [⚙️ Act With Selected Node](.)  
**Sequential Order:** 2.0
**Story Type:** user

## Story Description

Submit Current Behavior Action For Selected Node functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes
  **then** action completes successfully

## Scenarios

<a id="scenario-submit-current-behavior-action-for-selected-node"></a>
### Scenario: [Submit Current Behavior Action For Selected Node](#scenario-submit-current-behavior-action-for-selected-node) (happy_path)

**Steps:**
```gherkin
Given Bot has story map loaded with node <node_name>
And Bot has current behavior <behavior>
And Bot has current action <action>
When User calls bot.story_graph."<node_path>".submit_current_instructions
Then Bot submits instructions using current behavior <behavior> and action <action>
And Scope is set to node <node_name>
```

**Examples:**
| node_name | node_path | behavior | action |
| --- | --- | --- | --- |
| Upload File | File Management.Upload File | code | build |


<a id="scenario-panel-submit-button-uses-current-behavior-action-and-submits-instructions"></a>
### Scenario: [Panel submit button uses current behavior action and submits instructions](#scenario-panel-submit-button-uses-current-behavior-action-and-submits-instructions) (happy_path)

**Steps:**
```gherkin
Given User has selected a <node_type> <node_name> in the panel
And Bot has current behavior <behavior>
And Bot has current action <action>
And Panel displays behavior <behavior> and action <action> for selected node
When Panel renders the submit button
Then Submit button displays <icon_file> icon indicating <behavior> behavior
When User hovers over the submit button
Then Submit button shows tooltip <tooltip_text>
When User clicks the submit button
Then Panel calls node.get_required_behavior_instructions with action <action>
And Instructions for <behavior> behavior and <action> action are returned
And Panel sets scope to selected <node_type> <node_name>
And Scope is set to <node_type> <node_name>
```

**Examples:**
| node_type | node_name | behavior | action | icon_file | tooltip_text | node_path |
| --- | --- | --- | --- | --- | --- | --- |
| epic | Product Catalog | shape | build | submit_subepic.png | Submit shape instructions for epic | Product Catalog |
| sub-epic | Report Export | explore | build | submit_story.png | Submit exploration instructions for sub-epic | Test Epic.Report Export |
| story | Create User | scenario | build | submit_ac.png | Submit scenario instructions for story | Test Epic.Test SubEpic.Create User |
| story | Delete File | test | validate | submit_tests.png | Submit test instructions for story | Test Epic.Test SubEpic.Delete File |
| story | Upload File | code | build | submit_code.png | Submit code instructions for story | Test Epic.Test SubEpic.Upload File |


<a id="scenario-submit-current-instructions-via-cli-json-format"></a>
### Scenario: [Submit Current Instructions Via CLI JSON Format](#scenario-submit-current-instructions-via-cli-json-format) (happy_path)

**Steps:**
```gherkin
Given CLI has story map loaded with node <node_name>
And Bot has current behavior <behavior>
And Bot has current action <action>
When User executes CLI command story_graph."<node_path>".submit_current_instructions
Then CLI returns JSON with submit result
And Bot submits instructions using current behavior <behavior> and action <action>
And Scope is set to node <node_name>
```

**Examples:**
| node_name | node_path | behavior | action |
| --- | --- | --- | --- |
| Upload File | File Management.Upload File | code | build |

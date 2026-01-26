# 📄 Execute Action Scoped To Story Node

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1347)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Edit Story Nodes](.)  
**Sequential Order:** 17.0
**Story Type:** user

## Story Description

Execute Action Scoped To Story Node functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-execute-action-on-node-with-valid-parameters"></a>
### Scenario: [Execute action on node with valid parameters](#scenario-execute-action-on-node-with-valid-parameters) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1356)

**Steps:**
```gherkin
GIVEN: Node exists and bot has registered actions
WHEN: Node executes action with valid parameters
THEN: Action completes successfully
```


<a id="scenario-execute-action-with-invalid-parameters-returns-error"></a>
### Scenario: [Execute action with invalid parameters returns error](#scenario-execute-action-with-invalid-parameters-returns-error) (error)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1386)

**Steps:**
```gherkin
GIVEN: Node exists and bot has registered actions
WHEN: Node executes action with invalid parameters
THEN: Bot validates parameters and returns error
```


<a id="scenario-execute-non-existent-action-returns-error"></a>
### Scenario: [Execute non-existent action returns error](#scenario-execute-non-existent-action-returns-error) (error)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1414)

**Steps:**
```gherkin
GIVEN: Node exists and bot has registered actions
WHEN: Node attempts to execute non-existent action
THEN: Bot validates action exists and returns error
```


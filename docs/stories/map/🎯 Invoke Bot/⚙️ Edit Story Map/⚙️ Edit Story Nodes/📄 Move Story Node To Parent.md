# 📄 Move Story Node To Parent

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L702)

**User:** System
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Edit Story Nodes](.)  
**Sequential Order:** 8.0
**Story Type:** user

## Story Description

Move Story Node To Parent functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-move-node-to-new-parent-with-default-position"></a>
### Scenario: [Move node to new parent with default position](#scenario-move-node-to-new-parent-with-default-position) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L711)

**Steps:**
```gherkin
Given Node exists under source parent
When Node moves to target parent
Then Node is removed from source and added to target at last position
```


<a id="scenario-move-node-to-new-parent-with-specified-position"></a>
### Scenario: [Move node to new parent with specified position](#scenario-move-node-to-new-parent-with-specified-position) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L746)

**Steps:**
```gherkin
Given Node exists under source parent, target parent has children
When Node moves to target parent at specific position
Then Node is inserted at position and target children shift
```


<a id="scenario-move-node-with-invalid-position-adjusts-to-last"></a>
### Scenario: [Move node with invalid position adjusts to last](#scenario-move-node-with-invalid-position-adjusts-to-last) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L771)

**Steps:**
```gherkin
Given Node exists under source parent
When Moving to target with invalid position
Then Position is adjusted to last valid position
```


<a id="scenario-move-node-to-same-parent-at-different-position"></a>
### Scenario: [Move node to same parent at different position](#scenario-move-node-to-same-parent-at-different-position) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L796)

**Steps:**
```gherkin
Given Parent has children in order
When Node moves to different position within same parent
Then Children are reordered correctly
```


<a id="scenario-move-node-to-parent-where-it-already-exists-returns-error"></a>
### Scenario: [Move node to parent where it already exists returns error](#scenario-move-node-to-parent-where-it-already-exists-returns-error) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L824)

**Steps:**
```gherkin
Given Node is already child of parent
When Attempting to move node to same parent
Then System identifies duplicate and returns error
```


<a id="scenario-move-subepic-to-subepic-with-stories-returns-error"></a>
### Scenario: [Move SubEpic to SubEpic with Stories returns error](#scenario-move-subepic-to-subepic-with-stories-returns-error) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L851)

**Steps:**
```gherkin
Given Source has SubEpic, target has Stories
When Attempting to move SubEpic to target with Stories
Then System identifies hierarchy violation and returns error
```


<a id="scenario-move-story-to-subepic-with-subepics-returns-error"></a>
### Scenario: [Move Story to SubEpic with SubEpics returns error](#scenario-move-story-to-subepic-with-subepics-returns-error) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L875)

**Steps:**
```gherkin
Given Source has Story, target has SubEpics
When Attempting to move Story to target with SubEpics
Then System identifies hierarchy violation and returns error
```


<a id="scenario-move-node-to-create-circular-reference-returns-error"></a>
### Scenario: [Move node to create circular reference returns error](#scenario-move-node-to-create-circular-reference-returns-error) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L899)

**Steps:**
```gherkin
Given Parent has descendant
When Attempting to move parent to its descendant
Then System identifies circular reference and returns error
```


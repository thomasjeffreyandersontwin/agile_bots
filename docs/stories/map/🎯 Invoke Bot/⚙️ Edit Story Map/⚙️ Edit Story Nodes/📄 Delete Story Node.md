# 📄 Delete Story Node

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L787)

**User:** System
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Edit Story Nodes](.)  
**Sequential Order:** 8.0
**Story Type:** user

## Story Description

Delete Story Node functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-delete-node-without-children"></a>
### Scenario: [Delete node without children](#scenario-delete-node-without-children) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L796)

**Steps:**
```gherkin
Given Story Graph has parent node with children
When Node with no children is deleted
Then Node is removed and siblings are resequenced
```


<a id="scenario-delete-node-including-children-cascade-delete"></a>
### Scenario: [Delete node including children (cascade delete)](#scenario-delete-node-including-children-cascade-delete) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L826)

**Steps:**
```gherkin
Given Node has descendants
When Node is deleted with cascade option
Then Node and all descendants are deleted
```


<a id="scenario-delete-node-at-different-positions-verifies-resequencing"></a>
### Scenario: [Delete node at different positions verifies resequencing](#scenario-delete-node-at-different-positions-verifies-resequencing) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L855)

**Steps:**
```gherkin
Given Parent has children in order
When Node at specific position is deleted
Then Remaining children are resequenced properly
```


# 📄 Delete Story Node

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** System
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Edit Story Nodes](.)  
**Sequential Order:** 5.0
**Story Type:** user

## Story Description

Delete Story Node functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-delete-node-without-children"></a>
### Scenario: [Delete node without children](#scenario-delete-node-without-children) (happy_path)

**Steps:**
```gherkin
Given Story Graph has parent node with children
When Node with no children is deleted
Then Node is removed and siblings are resequenced
```


<a id="scenario-delete-node-including-children-cascade-delete"></a>
### Scenario: [Delete node including children (cascade delete)](#scenario-delete-node-including-children-cascade-delete) (happy_path)

**Steps:**
```gherkin
Given Node has descendants
When Node is deleted with cascade option
Then Node and all descendants are deleted
```


<a id="scenario-delete-node-at-different-positions-verifies-resequencing"></a>
### Scenario: [Delete node at different positions verifies resequencing](#scenario-delete-node-at-different-positions-verifies-resequencing) (happy_path)

**Steps:**
```gherkin
Given Parent has children in order
When Node at specific position is deleted
Then Remaining children are resequenced properly
```


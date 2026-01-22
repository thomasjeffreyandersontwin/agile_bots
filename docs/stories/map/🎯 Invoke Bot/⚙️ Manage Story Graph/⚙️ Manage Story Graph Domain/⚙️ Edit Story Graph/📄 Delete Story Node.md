# 📄 Delete Story Node

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Story Graph Node
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Manage Story Graph](..) / [⚙️ Manage Story Graph Domain](..) / [⚙️ Edit Story Graph](.)  
**Sequential Order:** 3.0
**Story Type:** user

## Story Description

Delete Story Node functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Story Graph Node deletes itself without children
  **then** node removes itself from parent
  **and** resequences remaining siblings

- **When** Story Graph Node deletes itself with children
  **then** node moves all children to node's parent as last children
  **and** removes itself from parent
  **and** resequences siblings

- **When** Story Graph Node deletes itself including children
  **then** node recursively deletes all children
  **and** removes itself from parent
  **and** resequences siblings

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Story Graph is initialized
```

## Scenarios

<a id="scenario-delete-node-without-children"></a>
### Scenario: [Delete node without children](#scenario-delete-node-without-children) (happy_path)

**Steps:**
```gherkin
Given Story Graph has "<parent_type>" named "<parent_name>" with children: <initial_children>
And node "<node_name>" is at position <node_position> with <child_count> children
When node "<node_name>" is deleted
Then node "<node_name>" is removed from "<parent_name>"
And "<parent_name>" children are: <remaining_children>
And "<parent_name>" children are resequenced
And "<parent_name>" has <final_count> children
```

**Examples:**
| parent_type | parent_name | initial_children | node_name | node_position | child_count | remaining_children | final_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Epic | User Management | SubEpic A, SubEpic B, SubEpic C | SubEpic B | 1 | 0 | SubEpic A, SubEpic C | 2 |
| SubEpic | Authentication | Story A, Story B | Story A | 0 | 0 | Story B | 1 |
| Story | Login Form | Scenario A, Scenario B, Scenario C | Scenario C | 2 | 0 | Scenario A, Scenario B | 2 |


<a id="scenario-delete-node-with-children-promotes-children-to-grandparent"></a>
### Scenario: [Delete node with children promotes children to grandparent](#scenario-delete-node-with-children-promotes-children-to-grandparent) (happy_path)

**Steps:**
```gherkin
Given Story Graph has "<grandparent_type>" named "<grandparent>" with child "<node_name>"
And node "<node_name>" has children: <node_children>
And "<grandparent>" has <initial_child_count> children
When node "<node_name>" is deleted
Then node "<node_name>" is removed from "<grandparent>"
And children <node_children> are moved to "<grandparent>" as last children
And "<grandparent>" has <final_child_count> children
```

**Examples:**
| grandparent_type | grandparent | node_name | node_children | initial_child_count | final_child_count |
| --- | --- | --- | --- | --- | --- |
| Epic | User Management | Authentication | Login Flow, Password Reset | 3 | 4 |
| SubEpic | Authentication | OAuth Flow | Google Auth, GitHub Auth | 2 | 3 |


<a id="scenario-delete-node-including-children-cascade-delete"></a>
### Scenario: [Delete node including children (cascade delete)](#scenario-delete-node-including-children-cascade-delete) (happy_path)

**Steps:**
```gherkin
Given Story Graph has "<parent_type>" named "<parent_name>" with children: <initial_children>
And node "<node_name>" has <child_count> children
And node "<node_name>" has <total_descendants> total descendants
When node "<node_name>" is deleted with cascade option
Then node "<node_name>" and all descendants are deleted
And "<parent_name>" children are: <remaining_children>
And "<parent_name>" has <final_count> children
```

**Examples:**
| parent_type | parent_name | initial_children | node_name | child_count | total_descendants | remaining_children | final_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Epic | User Management | SubEpic A, SubEpic B, SubEpic C, SubEpic D | SubEpic B | 2 | 5 | SubEpic A, SubEpic C, SubEpic D | 3 |
| SubEpic | Authentication | SubEpic A, SubEpic B | SubEpic A | 3 | 8 | SubEpic B | 1 |


<a id="scenario-delete-node-at-different-positions-verifies-resequencing"></a>
### Scenario: [Delete node at different positions verifies resequencing](#scenario-delete-node-at-different-positions-verifies-resequencing) (edge_case)

**Steps:**
```gherkin
Given Story Graph has "<parent_type>" named "<parent_name>" with children in order: <initial_order>
And node "<node_name>" is at position <delete_position>
When node "<node_name>" is deleted
Then "<parent_name>" children are in order: <final_order>
And all remaining children have sequential positions
```

**Examples:**
| parent_type | parent_name | initial_order | node_name | delete_position | final_order |
| --- | --- | --- | --- | --- | --- |
| Epic | User Management | SubEpic A, SubEpic B, SubEpic C, SubEpic D | SubEpic A | 0 | SubEpic B, SubEpic C, SubEpic D |
| Epic | User Management | SubEpic A, SubEpic B, SubEpic C, SubEpic D | SubEpic C | 2 | SubEpic A, SubEpic B, SubEpic D |
| Epic | User Management | SubEpic A, SubEpic B, SubEpic C, SubEpic D | SubEpic D | 3 | SubEpic A, SubEpic B, SubEpic C |


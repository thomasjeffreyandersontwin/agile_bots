# 📄 Move Story Node To Parent

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Story Graph Node
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Directly](..) / [⚙️ Manage Story Graph](..) / [⚙️ Edit Story Graph](.)  
**Sequential Order:** 2
**Story Type:** user

## Story Description

Move Story Node To Parent functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Story Graph Node moves to new parent
  **then** node removes itself from current parent
  **and** node adds itself to target parent as last child
  **and** resequences original siblings on or after original location

- **When** Story Graph Node moves to new parent with position specified
  **then** node removes itself from current parent
  **and** node adds itself to target parent at specified position
  **and** resequences all children at or after position in both locations

- **When** Story Graph Node moves with invalid position specified
  **then** adjusts position to last if exceeds children count
  **and** moves node to adjusted position

- **When** Story Graph Node moves to same parent different position
  **then** node removes itself from current position
  **and** node adds itself at new position
  **and** resequences siblings

- **When** Story Graph Node moves to parent where it already exists
  **then** Story Graph Node identifies child already under parent
  **and** returns error

- **When** SubEpic moves to SubEpic that has Stories
  **then** target SubEpic identifies it already contains Stories
  **and** returns error indicating cannot move SubEpic to SubEpic with Stories

- **When** Story moves to SubEpic that has SubEpic children
  **then** target SubEpic identifies it already contains Sub-Epics
  **and** returns error indicating cannot move Story to SubEpic with Sub-Epics

- **When** Story Graph Node moves to create circular reference
  **then** node identifies target parent is descendant of itself
  **and** returns error indicating circular reference

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Story Graph is initialized
```

## Scenarios

<a id="scenario-move-node-to-new-parent-with-default-position"></a>
### Scenario: [Move node to new parent with default position](#scenario-move-node-to-new-parent-with-default-position) (happy_path)

**Steps:**
```gherkin
Given Story Graph has "<source_parent_type>" named "<source_parent>" with child "<node_name>" at position <original_position>
And Story Graph has "<target_parent_type>" named "<target_parent>" with <target_child_count> children
When node "<node_name>" moves to parent "<target_parent>"
Then node "<node_name>" is removed from "<source_parent>"
And node "<node_name>" is added to "<target_parent>" at position <new_position>
And "<source_parent>" children are resequenced
And "<target_parent>" has <final_child_count> children
```

**Examples:**
| source_parent_type | source_parent | node_name | original_position | target_parent_type | target_parent | target_child_count | new_position | final_child_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Epic | User Management | Authentication | 1 | Epic | System Admin | 2 | 2 | 3 |
| SubEpic | Authentication | Login Flow | 0 | SubEpic | Authorization | 1 | 1 | 2 |
| SubEpic | Authentication | User Login | 1 | SubEpic | Session Management | 0 | 0 | 1 |


<a id="scenario-move-node-to-new-parent-with-specified-position"></a>
### Scenario: [Move node to new parent with specified position](#scenario-move-node-to-new-parent-with-specified-position) (happy_path)

**Steps:**
```gherkin
Given Story Graph has "<source_parent>" with child "<node_name>"
And Story Graph has "<target_parent>" with children: <target_children>
When node "<node_name>" moves to "<target_parent>" at position <target_position>
Then "<target_parent>" children are in order: <final_order>
And node "<node_name>" is at position <target_position>
```

**Examples:**
| source_parent | node_name | target_parent | target_children | target_position | final_order |
| --- | --- | --- | --- | --- | --- |
| Epic A | SubEpic X | Epic B | SubEpic A, SubEpic B, SubEpic C | 1 | SubEpic A, SubEpic X, SubEpic B, SubEpic C |
| SubEpic A | Story X | SubEpic B | Story A, Story B | 0 | Story X, Story A, Story B |
| SubEpic A | Story X | SubEpic B | Story A, Story B | 2 | Story A, Story B, Story X |


<a id="scenario-move-node-with-invalid-position-adjusts-to-last"></a>
### Scenario: [Move node with invalid position adjusts to last](#scenario-move-node-with-invalid-position-adjusts-to-last) (edge_case)

**Steps:**
```gherkin
Given Story Graph has "<source_parent>" with child "<node_name>"
And Story Graph has "<target_parent>" with <target_child_count> children
When node "<node_name>" moves to "<target_parent>" at position <invalid_position>
Then system adjusts position to <adjusted_position>
And node "<node_name>" is at position <adjusted_position>
And "<target_parent>" has <final_count> children
```

**Examples:**
| source_parent | node_name | target_parent | target_child_count | invalid_position | adjusted_position | final_count |
| --- | --- | --- | --- | --- | --- | --- |
| Epic A | SubEpic X | Epic B | 3 | 99 | 3 | 4 |
| SubEpic A | Story X | SubEpic B | 0 | 5 | 0 | 1 |


<a id="scenario-move-node-to-same-parent-at-different-position"></a>
### Scenario: [Move node to same parent at different position](#scenario-move-node-to-same-parent-at-different-position) (happy_path)

**Steps:**
```gherkin
Given Story Graph has "<parent_type>" named "<parent_name>" with children: <initial_order>
And node "<node_name>" is at position <current_position>
When node "<node_name>" moves to position <new_position> within "<parent_name>"
Then "<parent_name>" children are in order: <final_order>
And node "<node_name>" is at position <new_position>
```

**Examples:**
| parent_type | parent_name | initial_order | node_name | current_position | new_position | final_order |
| --- | --- | --- | --- | --- | --- | --- |
| Epic | User Management | SubEpic A, SubEpic B, SubEpic C | SubEpic C | 2 | 0 | SubEpic C, SubEpic A, SubEpic B |
| SubEpic | Authentication | Story A, Story B, Story C, Story D | Story B | 1 | 3 | Story A, Story C, Story D, Story B |


<a id="scenario-move-node-to-parent-where-it-already-exists-returns-error"></a>
### Scenario: [Move node to parent where it already exists returns error](#scenario-move-node-to-parent-where-it-already-exists-returns-error) (error_case)

**Steps:**
```gherkin
Given Story Graph has "<parent_type>" named "<parent_name>"
And "<parent_name>" has child "<node_name>"
When node "<node_name>" attempts to move to "<parent_name>"
Then system identifies child already under parent
And returns error "Node '<node_name>' already exists under parent '<parent_name>'"
And move operation is prevented
```

**Examples:**
| parent_type | parent_name | node_name |
| --- | --- | --- |
| Epic | User Management | Authentication |
| SubEpic | Authentication | Login Form |


<a id="scenario-move-subepic-to-subepic-with-stories-returns-error"></a>
### Scenario: [Move SubEpic to SubEpic with Stories returns error](#scenario-move-subepic-to-subepic-with-stories-returns-error) (error_case)

**Steps:**
```gherkin
Given Story Graph has SubEpic "<source_parent>" with child SubEpic "<node_name>"
And Story Graph has SubEpic "<target_parent>" with child Story "<existing_story>"
When SubEpic "<node_name>" attempts to move to "<target_parent>"
Then system identifies target SubEpic contains Stories
And returns error "Cannot move SubEpic to SubEpic with Stories"
And move operation is prevented
```

**Examples:**
| source_parent | node_name | target_parent | existing_story |
| --- | --- | --- | --- |
| User Management | OAuth Flow | Authentication | Login Form |
| Administration | Audit Logging | User Profile | Edit Profile |


<a id="scenario-move-story-to-subepic-with-subepics-returns-error"></a>
### Scenario: [Move Story to SubEpic with SubEpics returns error](#scenario-move-story-to-subepic-with-subepics-returns-error) (error_case)

**Steps:**
```gherkin
Given Story Graph has SubEpic "<source_parent>" with child Story "<node_name>"
And Story Graph has SubEpic "<target_parent>" with child SubEpic "<existing_subepic>"
When Story "<node_name>" attempts to move to "<target_parent>"
Then system identifies target SubEpic contains SubEpics
And returns error "Cannot move Story to SubEpic with SubEpics"
And move operation is prevented
```

**Examples:**
| source_parent | node_name | target_parent | existing_subepic |
| --- | --- | --- | --- |
| Authentication | Login Form | User Management | Authorization |
| User Profile | Edit Profile | Administration | Audit Logging |


<a id="scenario-move-node-to-create-circular-reference-returns-error"></a>
### Scenario: [Move node to create circular reference returns error](#scenario-move-node-to-create-circular-reference-returns-error) (error_case)

**Steps:**
```gherkin
Given Story Graph has "<parent_type>" named "<parent_name>" with descendant "<child_name>"
When "<parent_name>" attempts to move to "<child_name>"
Then system identifies target is descendant of node
And returns error "Cannot move node to its own descendant - circular reference"
And move operation is prevented
```

**Examples:**
| parent_type | parent_name | child_name |
| --- | --- | --- |
| Epic | User Management | Authentication |
| SubEpic | Authentication | Login Flow |


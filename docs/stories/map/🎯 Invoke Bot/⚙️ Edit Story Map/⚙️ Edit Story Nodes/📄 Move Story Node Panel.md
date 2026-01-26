# 📄 Move Story Node Panel

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1930)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Edit Story Nodes](.)  
**Sequential Order:** 13.0
**Story Type:** user

## Story Description

Move Story Node Panel functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User drags node
  **then** Panel shows drag cursor with node icon

- **When** User drags over compatible parent
  **then** Panel highlights parent as valid drop target

- **When** User drags over incompatible parent or descendant
  **then** Panel shows no-drop cursor

- **When** User drops on compatible parent
  **then** Panel removes node from source
  **and** inserts node under target at position
  **and** resequences nodes in both locations
  **and** refreshes Story Tree

- **When** User drops on incompatible parent
  **then** Panel ignores drop
  **and** node returns to original position

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Story Graph is loaded in Panel
```

## Scenarios

<a id="scenario-user-drags-node-and-panel-shows-drag-cursor"></a>
### Scenario: [User drags node and Panel shows drag cursor](#scenario-user-drags-node-and-panel-shows-drag-cursor) (happy_path)

**Steps:**
```gherkin
And Story Graph has SubEpic "Authentication"
And SubEpic "Authentication" is selected
When User starts dragging node "Authentication"
Then Panel shows drag cursor
And Panel shows node icon next to cursor
And Panel indicates node is being moved
```


<a id="scenario-user-drags-over-compatible-parent-and-panel-highlights-as-valid-target"></a>
### Scenario: [User drags over compatible parent and Panel highlights as valid target](#scenario-user-drags-over-compatible-parent-and-panel-highlights-as-valid-target) (happy_path)

**Steps:**
```gherkin
And Story Graph has Epic "User Management" and Epic "System Admin"
And Epic "User Management" has SubEpic "Authentication"
And User is dragging SubEpic "Authentication"
When User drags over Epic "System Admin"
Then Panel validates Epic "System Admin" can accept SubEpic children
And Panel highlights Epic "System Admin" as valid drop target
And Panel shows drop indicator at target position
```


<a id="scenario-user-drags-over-incompatible-parent-and-panel-shows-no-drop-cursor"></a>
### Scenario: [User drags over incompatible parent and Panel shows no-drop cursor](#scenario-user-drags-over-incompatible-parent-and-panel-shows-no-drop-cursor) (error_case)

**Steps:**
```gherkin
And Story Graph has SubEpic "Authentication" with Story "Login Form"
And Story Graph has SubEpic "Authorization" with SubEpic "Roles"
And User is dragging SubEpic "Roles"
When User drags over SubEpic "Authentication" that contains Stories
Then Panel validates SubEpic "Authentication" cannot accept SubEpic children
And Panel shows no-drop cursor
And Panel does not highlight "Authentication" as target
```


<a id="scenario-user-drags-over-descendant-and-panel-shows-no-drop-cursor"></a>
### Scenario: [User drags over descendant and Panel shows no-drop cursor](#scenario-user-drags-over-descendant-and-panel-shows-no-drop-cursor) (error_case)

**Steps:**
```gherkin
And Story Graph has Epic "User Management" with SubEpic "Authentication"
And SubEpic "Authentication" has SubEpic "Login Flow"
And User is dragging Epic "User Management"
When User drags over SubEpic "Authentication" which is descendant
Then Panel detects circular reference would occur
And Panel shows no-drop cursor
And Panel does not highlight "Authentication" as target
```


<a id="scenario-user-drops-on-compatible-parent-and-panel-moves-node"></a>
### Scenario: [User drops on compatible parent and Panel moves node](#scenario-user-drops-on-compatible-parent-and-panel-moves-node) (happy_path)

**Steps:**
```gherkin
And Story Graph has Epic "User Management" with SubEpics: "SubEpic A", "Authentication", "SubEpic B"
And Story Graph has Epic "System Admin" with SubEpic "SubEpic C"
And User is dragging SubEpic "Authentication"
And User has dragged over Epic "System Admin"
And Panel shows "System Admin" as valid drop target
When User drops node on Epic "System Admin" at position 1
Then Panel removes "Authentication" from Epic "User Management"
And Panel inserts "Authentication" under Epic "System Admin" at position 1
And Panel resequences children in "User Management" to show: "SubEpic A", "SubEpic B"
And Panel resequences children in "System Admin" to show: "SubEpic C", "Authentication"
And Panel refreshes Story Tree
```


<a id="scenario-user-drops-on-incompatible-parent-and-panel-ignores-drop"></a>
### Scenario: [User drops on incompatible parent and Panel ignores drop](#scenario-user-drops-on-incompatible-parent-and-panel-ignores-drop) (error_case)

**Steps:**
```gherkin
And Story Graph has SubEpic "Authentication" with Story "Login Form"
And Story Graph has SubEpic "Authorization" with SubEpic "Roles"
And User is dragging SubEpic "Roles"
When User drops on SubEpic "Authentication" that contains Stories
Then Panel ignores drop operation
And SubEpic "Roles" returns to original position under "Authorization"
And Panel does not modify Story Graph structure
```


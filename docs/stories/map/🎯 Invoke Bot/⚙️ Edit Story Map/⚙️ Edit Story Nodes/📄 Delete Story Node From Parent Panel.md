# 📄 Delete Story Node From Parent Panel

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1730)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Edit Story Nodes](.)  
**Sequential Order:** 10.0
**Story Type:** user

## Story Description

Delete Story Node From Parent Panel functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User selects node
  **then** Panel shows "Delete" button

- **When** User selects node with children
  **then** Panel shows "Delete" and "Delete Including Children" buttons

- **When** User clicks "Delete" button
  **then** Panel shows confirmation inline
  **and** shows confirm and cancel buttons

- **When** User confirms delete without children
  **then** Panel removes node from parent
  **and** resequences siblings
  **and** refreshes Story Tree

- **When** User confirms delete with children
  **then** Panel moves children to node's parent
  **and** removes node
  **and** resequences siblings

- **When** User confirms "Delete Including Children"
  **then** Panel recursively removes all children
  **and** removes node

- **When** User cancels
  **then** Panel hides confirmation
  **and** node remains unchanged

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Story Graph is loaded in Panel
```

## Scenarios

<a id="scenario-panel-shows-delete-button-for-node-without-children"></a>
### Scenario: [Panel shows delete button for node without children](#scenario-panel-shows-delete-button-for-node-without-children) (happy_path)

**Steps:**
```gherkin
And Story Graph has SubEpic "Authentication" without children
When User selects SubEpic "Authentication"
Then Panel displays "Delete" button
And Panel does not display "Delete Including Children" button
```


<a id="scenario-panel-shows-both-delete-buttons-for-node-with-children"></a>
### Scenario: [Panel shows both delete buttons for node with children](#scenario-panel-shows-both-delete-buttons-for-node-with-children) (happy_path)

**Steps:**
```gherkin
And Story Graph has SubEpic "Authentication" with child Story "Login Form"
When User selects SubEpic "Authentication"
Then Panel displays "Delete" button
And Panel displays "Delete Including Children" button
```


<a id="scenario-user-clicks-delete-button-and-panel-shows-confirmation"></a>
### Scenario: [User clicks delete button and Panel shows confirmation](#scenario-user-clicks-delete-button-and-panel-shows-confirmation) (happy_path)

**Steps:**
```gherkin
And Story Graph has SubEpic "Authentication"
And SubEpic "Authentication" is selected
When User clicks "Delete" button
Then Panel displays confirmation message inline
And Panel displays "Confirm" button
And Panel displays "Cancel" button
And Panel hides "Delete" button
```


<a id="scenario-user-confirms-delete-for-node-without-children"></a>
### Scenario: [User confirms delete for node without children](#scenario-user-confirms-delete-for-node-without-children) (happy_path)

**Steps:**
```gherkin
And Story Graph has Epic "User Management" with SubEpics: "SubEpic A", "Authentication", "SubEpic B"
And SubEpic "Authentication" has no children
And Delete confirmation is displayed on panel for "Authentication"
When User clicks "Confirm" button
Then Panel removes SubEpic "Authentication" from parent
And Panel resequences siblings
And Panel refreshes Story Tree
And Epic "User Management" shows children: "SubEpic A", "SubEpic B"
```


<a id="scenario-user-confirms-delete-for-node-with-children-and-children-move-to-parent"></a>
### Scenario: [User confirms delete for node with children and children move to parent](#scenario-user-confirms-delete-for-node-with-children-and-children-move-to-parent) (happy_path)

**Steps:**
```gherkin
And Story Graph has Epic "User Management" with SubEpic "Authentication"
And SubEpic "Authentication" has children Stories: "Login Form", "Password Reset"
And Delete confirmation is displayed on panel for "Authentication"
When User clicks "Confirm" button
Then Panel moves children "Login Form" and "Password Reset" to Epic "User Management"
And Panel removes SubEpic "Authentication"
And Panel resequences siblings
And Panel refreshes Story Tree
And Epic "User Management" shows children including "Login Form" and "Password Reset"
```


<a id="scenario-user-confirms-delete-including-children-and-panel-recursively-deletes-all"></a>
### Scenario: [User confirms delete including children and Panel recursively deletes all](#scenario-user-confirms-delete-including-children-and-panel-recursively-deletes-all) (happy_path)

**Steps:**
```gherkin
And Story Graph has Epic "User Management" with SubEpic "Authentication"
And SubEpic "Authentication" has child Story "Login Form"
And Story "Login Form" has child Scenario "Valid Login"
And Delete Including Children confirmation is displayed on panel for "Authentication"
When User clicks "Confirm" button
Then Panel recursively removes Scenario "Valid Login"
And Panel recursively removes Story "Login Form"
And Panel removes SubEpic "Authentication"
And Panel refreshes Story Tree
And Epic "User Management" no longer shows "Authentication"
```


<a id="scenario-user-cancels-delete-and-node-remains-unchanged"></a>
### Scenario: [User cancels delete and node remains unchanged](#scenario-user-cancels-delete-and-node-remains-unchanged) (happy_path)

**Steps:**
```gherkin
And Story Graph has SubEpic "Authentication" with child Story "Login Form"
And Delete confirmation is displayed on panel for "Authentication"
When User clicks "Cancel" button
Then Panel hides confirmation
And Panel shows "Delete" button again
And SubEpic "Authentication" remains in Story Graph
And Story "Login Form" remains under "Authentication"
```


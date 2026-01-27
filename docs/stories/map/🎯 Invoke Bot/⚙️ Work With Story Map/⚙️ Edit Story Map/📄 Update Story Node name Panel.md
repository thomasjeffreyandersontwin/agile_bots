# 📄 Update Story Node name Panel

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1699)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Work With Story Map](..) / [⚙️ Edit Story Map](.)  
**Sequential Order:** 16.0
**Story Type:** user

## Story Description

Update Story Node name Panel functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User clicks node name
  **then** Panel enables inline editing

- **When** User types in name field
  **and** User presses Tab or Enter clicks away from the name field.
  **then** Panel validates name in real-time
  **and** saves Name change

- **When** User types empty name
  **then** Panel shows "Name required" message

- **When** User types duplicate name
  **then** Panel shows "Name already exists" message

- **When** User types invalid characters
  **then** Panel shows "Invalid characters" message

- **When** User saves valid name
  **then** Panel updates node name
  **and** exits editing mode
  **and** refreshes Story Tree

- **When** User cancels By pressing Escape
  **then** Panel retains previous name
  **and** exits editing mode

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Story Graph is loaded in Panel
```

## Scenarios

<a id="scenario-user-clicks-node-name-and-panel-enables-inline-editing"></a>
### Scenario: [User clicks node name and Panel enables inline editing](#scenario-user-clicks-node-name-and-panel-enables-inline-editing) (happy_path)

**Steps:**
```gherkin
And Story Graph has SubEpic "Authentication"
And SubEpic "Authentication" is selected
When User clicks node name "Authentication"
Then Panel enables inline editing mode
And Panel shows text input field with current name
And Panel selects all text in name field
```


<a id="scenario-user-types-valid-name-and-saves-by-pressing-tab"></a>
### Scenario: [User types valid name and saves by pressing Tab](#scenario-user-types-valid-name-and-saves-by-pressing-tab) (happy_path)

**Steps:**
```gherkin
And Story Graph has SubEpic "Authentication"
And User has clicked node name "Authentication" to edit
And Panel is in inline editing mode
When User types "User Authentication"
And User presses Tab
Then Panel validates name in real-time
And Panel updates node name to "User Authentication"
And Panel exits editing mode
And Panel refreshes Story Tree
And Story Tree shows "User Authentication"
```


<a id="scenario-user-types-valid-name-and-saves-by-pressing-enter"></a>
### Scenario: [User types valid name and saves by pressing Enter](#scenario-user-types-valid-name-and-saves-by-pressing-enter) (happy_path)

**Steps:**
```gherkin
And Story Graph has Story "Login Form"
And User has clicked node name "Login Form" to edit
And Panel is in inline editing mode
When User types "User Login Interface"
And User presses Enter
Then Panel validates name in real-time
And Panel updates node name to "User Login Interface"
And Panel exits editing mode
And Panel refreshes Story Tree
```


<a id="scenario-user-types-empty-name-and-panel-shows-required-message"></a>
### Scenario: [User types empty name and Panel shows required message](#scenario-user-types-empty-name-and-panel-shows-required-message) (error_case)

**Steps:**
```gherkin
And Story Graph has SubEpic "Authentication"
And User has clicked node name to edit
And Panel is in inline editing mode
When User clears all text from name field
And User presses Tab
Then Panel validates name in real-time
And Panel shows error message "Name required"
And Panel remains in editing mode
And Panel does not save empty name
```


<a id="scenario-user-types-duplicate-name-and-panel-shows-exists-message"></a>
### Scenario: [User types duplicate name and Panel shows exists message](#scenario-user-types-duplicate-name-and-panel-shows-exists-message) (error_case)

**Steps:**
```gherkin
And Story Graph has Epic "User Management" with SubEpics: "Authentication", "Authorization"
And User has clicked node name "Authorization" to edit
And Panel is in inline editing mode
When User types "Authentication"
And User presses Tab
Then Panel validates name against siblings
And Panel shows error message "Name already exists"
And Panel remains in editing mode
And Panel does not save duplicate name
```


<a id="scenario-user-types-invalid-characters-and-panel-shows-invalid-message"></a>
### Scenario: [User types invalid characters and Panel shows invalid message](#scenario-user-types-invalid-characters-and-panel-shows-invalid-message) (error_case)

**Steps:**
```gherkin
And Story Graph has SubEpic "Authentication"
And User has clicked node name to edit
And Panel is in inline editing mode
When User types "Auth<>|*"
And User presses Tab
Then Panel validates characters in name
And Panel shows error message "Invalid characters"
And Panel remains in editing mode
And Panel does not save name with invalid characters
```


<a id="scenario-user-cancels-editing-by-pressing-escape-and-panel-retains-original-name"></a>
### Scenario: [User cancels editing by pressing Escape and Panel retains original name](#scenario-user-cancels-editing-by-pressing-escape-and-panel-retains-original-name) (happy_path)

**Steps:**
```gherkin
And Story Graph has SubEpic "Authentication"
And User has clicked node name to edit
And Panel is in inline editing mode
When User types "New Name"
And User presses Escape
Then Panel exits editing mode
And Panel retains original name "Authentication"
And Panel does not save name change
And Story Tree still shows "Authentication"
```


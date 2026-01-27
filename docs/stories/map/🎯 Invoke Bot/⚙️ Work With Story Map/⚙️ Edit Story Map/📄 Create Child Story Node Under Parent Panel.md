# 📄 Create Child Story Node Under Parent Panel

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1462)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Work With Story Map](..) / [⚙️ Edit Story Map](.)  
**Sequential Order:** 4.0
**Story Type:** user

## Story Description

Create Child Story Node Under Parent Panel functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User selects Epic node
  **then** Panel shows "Create Sub-Epic" button

- **When** User selects SubEpic without children
  **then** Panel shows "Create Sub-Epic" and "Create Story" buttons

- **When** User selects SubEpic with Sub-Epic children
  **then** Panel shows "Create Sub-Epic" button

- **When** User selects SubEpic with Stories
  **then** Panel shows "Create Story" button

- **When** User selects Story node
  **then** Panel shows "Create Scenario", "Create Scenario Outline", and "Create Acceptance Criteria" buttons

- **When** User creates child node
  **then** Panel creates child with unique generic name
  **and** puts node name in edit mode with text selected
  **and** refreshes Story Tree

- **When** User enters duplicate name
  **and** user presses Tab or Enter or clicks anywhere away from the name field.
  **then** Panel shows warning in real-time
  **and** leaves node name in edit mode with head selected.

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Story Graph is loaded in Panel
```

## Scenarios

<a id="scenario-panel-shows-appropriate-create-button-for-epic-node"></a>
### Scenario: [Panel shows appropriate create button for Epic node](#scenario-panel-shows-appropriate-create-button-for-epic-node) (happy_path)

**Steps:**
```gherkin
And Story Graph has Epic named "User Management"
When User selects Epic "User Management"
Then Panel displays "Create Sub-Epic" button
And Panel does not display "Create Story" button
```


<a id="scenario-panel-shows-both-create-buttons-for-subepic-without-children"></a>
### Scenario: [Panel shows both create buttons for SubEpic without children](#scenario-panel-shows-both-create-buttons-for-subepic-without-children) (happy_path)

**Steps:**
```gherkin
And Story Graph has Epic "User Management" with SubEpic "Authentication"
And SubEpic "Authentication" has no children
When User selects SubEpic "Authentication"
Then Panel displays "Create Sub-Epic" button
And Panel displays "Create Story" button
```


<a id="scenario-panel-shows-only-create-subepic-button-for-subepic-with-subepic-children"></a>
### Scenario: [Panel shows only create SubEpic button for SubEpic with SubEpic children](#scenario-panel-shows-only-create-subepic-button-for-subepic-with-subepic-children) (happy_path)

**Steps:**
```gherkin
And Story Graph has SubEpic "User Management" with child SubEpic "Authentication"
When User selects SubEpic "User Management"
Then Panel displays "Create Sub-Epic" button
And Panel does not display "Create Story" button
```


<a id="scenario-panel-shows-only-create-story-button-for-subepic-with-stories"></a>
### Scenario: [Panel shows only create Story button for SubEpic with Stories](#scenario-panel-shows-only-create-story-button-for-subepic-with-stories) (happy_path)

**Steps:**
```gherkin
And Story Graph has SubEpic "Authentication" with child Story "Login Form"
When User selects SubEpic "Authentication"
Then Panel displays "Create Story" button
And Panel does not display "Create Sub-Epic" button
```


<a id="scenario-panel-shows-scenario-create-buttons-for-story-node"></a>
### Scenario: [Panel shows scenario create buttons for Story node](#scenario-panel-shows-scenario-create-buttons-for-story-node) (happy_path)

**Steps:**
```gherkin
And Story Graph has Story "Validate Password"
When User selects Story "Validate Password"
Then Panel displays "Create Scenario" button
And Panel displays "Create Scenario Outline" button
And Panel displays "Create Acceptance Criteria" button
```


<a id="scenario-user-creates-child-node-with-auto-generated-name-in-edit-mode"></a>
### Scenario: [User creates child node with auto-generated name in edit mode](#scenario-user-creates-child-node-with-auto-generated-name-in-edit-mode) (happy_path)

**Steps:**
```gherkin
And Story Graph has Epic "User Management" with two SubEpic children
And Epic "User Management" is selected
When User clicks "Create Sub-Epic" button
Then Panel creates new SubEpic with name "SubEpic3"
And Panel puts node name in edit mode
And Panel selects all text in name field
And Panel refreshes Story Tree showing new child
And new SubEpic appears as last child of "User Management"
```


<a id="scenario-user-enters-duplicate-name-and-panel-shows-warning"></a>
### Scenario: [User enters duplicate name and Panel shows warning](#scenario-user-enters-duplicate-name-and-panel-shows-warning) (error_case)

**Steps:**
```gherkin
And Story Graph has Epic "User Management" with SubEpic "Authentication"
And new SubEpic exists under "User Management" with name in edit mode
When User types "Authentication" in name field
And User presses Tab
Then Panel validates name in real-time
And Panel shows warning message "Child with name 'Authentication' already exists"
And Panel keeps node name in edit mode
And Panel keeps text selected
And Panel does not save the duplicate name
```


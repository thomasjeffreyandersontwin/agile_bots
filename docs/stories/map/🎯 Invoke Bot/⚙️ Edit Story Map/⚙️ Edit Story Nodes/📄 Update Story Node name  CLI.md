# 📄 Update Story Node name  CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1796)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Edit Story Nodes](.)  
**Sequential Order:** 14.0
**Story Type:** user

## Story Description

Update Story Node name  CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User renames node with dot notation
  **then** CLI parses notation to node
  **and** resolves and validates node exists
  **and** validates name not empty and unique among siblings
  **and** updates node name
  **and** outputs success message

- **When** User enters non-existent node path
  **then** CLI identifies node does not exist [ - see previous acceptance criteria]
  **and** outputs error with valid paths

- **When** User enters empty name
  **then** CLI outputs error

- **When** User enters duplicate name
  **then** CLI identifies duplicate
  **and** outputs error

- **When** User enters invalid characters
  **then** CLI identifies invalid characters
  **and** outputs error

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Story Graph is initialized
```

## Scenarios

<a id="scenario-user-renames-node-with-valid-name-using-dot-notation"></a>
### Scenario: [User renames node with valid name using dot notation](#scenario-user-renames-node-with-valid-name-using-dot-notation) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1809)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot" with SubEpic "Old Name"
When User executes CLI command: story_graph."Invoke Bot"."Old Name".rename name:"New Name"
Then CLI parses dot notation to node "Old Name"
And CLI resolves node "Old Name" successfully
And CLI validates node exists
And CLI validates name "New Name" is not empty
And CLI validates name "New Name" is unique among siblings
And CLI updates node name to "New Name"
And CLI outputs success message: "Renamed SubEpic 'Old Name' to 'New Name'"
And Story Graph shows SubEpic "New Name" under Epic "Invoke Bot"
```


<a id="scenario-user-enters-non-existent-node-path-and-cli-outputs-error"></a>
### Scenario: [User enters non-existent node path and CLI outputs error](#scenario-user-enters-non-existent-node-path-and-cli-outputs-error) (error_case)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1836)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot" with SubEpic "Manage Bot"
And Story Graph does not have SubEpic "Non-existent Node"
When User executes CLI command: story_graph."Invoke Bot"."Non-existent Node".rename name:"New Name"
Then CLI parses dot notation to node "Non-existent Node"
And CLI attempts to resolve node "Non-existent Node"
And CLI identifies node does not exist
And CLI outputs error: "Node 'Non-existent Node' not found. Valid paths under 'Invoke Bot': 'Manage Bot'"
And CLI does not modify Story Graph
```


<a id="scenario-user-enters-empty-name-and-cli-outputs-error"></a>
### Scenario: [User enters empty name and CLI outputs error](#scenario-user-enters-empty-name-and-cli-outputs-error) (error_case)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1860)

**Steps:**
```gherkin
And Story Graph has SubEpic "Manage Bot"
When User executes CLI command: story_graph."Invoke Bot"."Manage Bot".rename name:""
Then CLI parses dot notation to node "Manage Bot"
And CLI resolves node "Manage Bot" successfully
And CLI validates new name
And CLI identifies name is empty
And CLI outputs error: "Name cannot be empty"
And CLI does not update node name
```


<a id="scenario-user-enters-duplicate-name-and-cli-outputs-error"></a>
### Scenario: [User enters duplicate name and CLI outputs error](#scenario-user-enters-duplicate-name-and-cli-outputs-error) (error_case)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1883)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot" with SubEpics: "Manage Bot", "Other SubEpic"
When User executes CLI command: story_graph."Invoke Bot"."Other SubEpic".rename name:"Manage Bot"
Then CLI parses dot notation to node "Other SubEpic"
And CLI resolves node "Other SubEpic" successfully
And CLI validates name "Manage Bot" against siblings
And CLI identifies duplicate name
And CLI outputs error: "Child with name 'Manage Bot' already exists under parent 'Invoke Bot'"
And CLI does not update node name
```


<a id="scenario-user-enters-invalid-characters-and-cli-outputs-error"></a>
### Scenario: [User enters invalid characters and CLI outputs error](#scenario-user-enters-invalid-characters-and-cli-outputs-error) (error_case)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1908)

**Steps:**
```gherkin
And Story Graph has SubEpic "Manage Bot"
When User executes CLI command: story_graph."Invoke Bot"."Manage Bot".rename name:"Name<>|*"
Then CLI parses dot notation to node "Manage Bot"
And CLI resolves node "Manage Bot" successfully
And CLI validates characters in name "Name<>|*"
And CLI identifies invalid characters: <, >, |, *
And CLI outputs error: "Name contains invalid characters: < > | *"
And CLI does not update node name
```


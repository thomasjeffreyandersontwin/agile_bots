# 📄 Move Story Node  CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1922)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Edit Story Nodes](.)  
**Sequential Order:** 12.0
**Story Type:** user

## Story Description

Move Story Node  CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User moves node with dot notation
  **then** CLI parses notation to source and target
  **and** resolves and validates both exist
  **and** validates type compatibility
  **and** adjusts position if exceeds children count
  **and** removes node from source
  **and** inserts node at target position
  **and** resequences both locations
  **and** outputs success message

- **When** User moves node to same parent different position
  **then** CLI parses notation and position [ - see previous acceptance criteria]
  **and** removes node from current position
  **and** inserts at new position

- **When** User enters non-existent source path
  **then** CLI identifies source does not exist [ - see previous acceptance criteria]
  **and** outputs error

- **When** User enters non-existent target path
  **then** CLI identifies target does not exist [ - see previous acceptance criteria]
  **and** outputs error

- **When** User moves incompatible type
  **then** CLI identifies type incompatibility [ - see previous acceptance criteria]
  **and** outputs error with allowed types

- **When** User moves to create circular reference
  **then** CLI identifies circular reference
  **and** outputs error

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Story Graph is initialized
```

## Scenarios

<a id="scenario-user-moves-node-to-different-parent-with-position-using-dot-notation"></a>
### Scenario: [User moves node to different parent with position using dot notation](#scenario-user-moves-node-to-different-parent-with-position-using-dot-notation) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1935)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot" with SubEpics: "SubEpic A", "Manage Bot", "SubEpic B"
And Story Graph has Epic "Other Epic" with SubEpics: "SubEpic C", "SubEpic D"
When User executes CLI command: story_graph."Invoke Bot"."Manage Bot".move_to target:"Other Epic" at_position:1
Then CLI parses dot notation to source node "Manage Bot"
And CLI parses dot notation to target parent "Other Epic"
And CLI resolves both nodes successfully
And CLI validates "Other Epic" can accept SubEpic children
And CLI validates position 1 is valid
And CLI removes "Manage Bot" from Epic "Invoke Bot"
And CLI inserts "Manage Bot" under Epic "Other Epic" at position 1
And CLI resequences children in "Invoke Bot" to show: "SubEpic A", "SubEpic B"
And CLI resequences children in "Other Epic" to show: "SubEpic C", "Manage Bot", "SubEpic D"
And CLI outputs success message: "Moved SubEpic 'Manage Bot' from 'Invoke Bot' to 'Other Epic' at position 1"
```


<a id="scenario-user-moves-node-to-same-parent-different-position"></a>
### Scenario: [User moves node to same parent different position](#scenario-user-moves-node-to-same-parent-different-position) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1963)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot" with SubEpics: "SubEpic A", "Manage Bot", "SubEpic B", "SubEpic C"
And SubEpic "Manage Bot" is at position 1
When User executes CLI command: story_graph."Invoke Bot"."Manage Bot".move_to_position position:3
Then CLI parses dot notation to node "Manage Bot"
And CLI parses position parameter as 3
And CLI resolves node "Manage Bot" successfully
And CLI removes "Manage Bot" from position 1
And CLI inserts "Manage Bot" at position 3
And CLI resequences children to show: "SubEpic A", "SubEpic B", "SubEpic C", "Manage Bot"
And CLI outputs success message: "Moved SubEpic 'Manage Bot' to position 3 within 'Invoke Bot'"
```


<a id="scenario-user-enters-non-existent-source-path-and-cli-outputs-error"></a>
### Scenario: [User enters non-existent source path and CLI outputs error](#scenario-user-enters-non-existent-source-path-and-cli-outputs-error) (error_case)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1993)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot"
And Story Graph has Epic "Other Epic"
And Story Graph does not have SubEpic "Non-existent Node"
When User executes CLI command: story_graph."Invoke Bot"."Non-existent Node".move_to target:"Other Epic"
Then CLI parses dot notation to source node "Non-existent Node"
And CLI attempts to resolve source node
And CLI identifies source node does not exist
And CLI outputs error: "Source node 'Non-existent Node' not found. Valid paths under 'Invoke Bot': (empty)"
And CLI does not modify Story Graph
```


<a id="scenario-user-enters-non-existent-target-path-and-cli-outputs-error"></a>
### Scenario: [User enters non-existent target path and CLI outputs error](#scenario-user-enters-non-existent-target-path-and-cli-outputs-error) (error_case)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L2018)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot" with SubEpic "Manage Bot"
And Story Graph does not have Epic "Non-existent Epic"
When User executes CLI command: story_graph."Invoke Bot"."Manage Bot".move_to target:"Non-existent Epic"
Then CLI parses dot notation to source node "Manage Bot"
And CLI resolves source node "Manage Bot" successfully
And CLI parses dot notation to target parent "Non-existent Epic"
And CLI attempts to resolve target parent
And CLI identifies target parent does not exist
And CLI outputs error: "Target parent 'Non-existent Epic' not found. Valid paths: 'Invoke Bot'"
And CLI does not modify Story Graph
```


<a id="scenario-user-moves-incompatible-type-and-cli-outputs-error"></a>
### Scenario: [User moves incompatible type and CLI outputs error](#scenario-user-moves-incompatible-type-and-cli-outputs-error) (error_case)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L2042)

**Steps:**
```gherkin
And Story Graph has SubEpic "Authentication" with Story "Login Form"
And Story Graph has SubEpic "Authorization" with SubEpic "Roles"
When User executes CLI command: story_graph."Authorization"."Roles".move_to target:"Authentication"
Then CLI parses notation to source "Roles" and target "Authentication"
And CLI resolves both nodes successfully
And CLI validates type compatibility
And CLI identifies SubEpic "Authentication" already contains Stories
And CLI identifies SubEpic "Roles" is incompatible with SubEpic containing Stories
And CLI outputs error: "Cannot move SubEpic 'Roles' to SubEpic 'Authentication' that contains Stories. Allowed child types: Story"
And CLI does not modify Story Graph
```


<a id="scenario-user-moves-to-create-circular-reference-and-cli-outputs-error"></a>
### Scenario: [User moves to create circular reference and CLI outputs error](#scenario-user-moves-to-create-circular-reference-and-cli-outputs-error) (error_case)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L2068)

**Steps:**
```gherkin
And Story Graph has Epic "User Management" with SubEpic "Authentication"
And SubEpic "Authentication" has SubEpic "Login Flow"
When User executes CLI command: story_graph."User Management".move_to target:"Authentication"
Then CLI parses notation to source "User Management" and target "Authentication"
And CLI resolves both nodes successfully
And CLI detects target "Authentication" is descendant of source "User Management"
And CLI identifies circular reference would occur
And CLI outputs error: "Cannot move 'User Management' to 'Authentication': target is a descendant of source (circular reference)"
And CLI does not modify Story Graph
```


# 📄 Create Child Story Node Under Parent CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1551)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Edit Story Nodes](.)  
**Sequential Order:** 6.0
**Story Type:** user

## Story Description

Create Child Story Node Under Parent CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User creates new child with dot notation
  **then** CLI parses dot notation to parent
  **and** resolves and validates parent exists
  **and** sets the child type based on the command used
  **and** creates child as last child
  **and** outputs success message with node path

- **When** User creates child with position
  **then** CLI parses notation and position [ - see previous acceptance criteria]
  **and** adjusts position if exceeds children count
  **and** creates child at position
  **and** resequences children

- **When** User enters non-existent parent path
  **then** CLI identifies parent does not exist
  **and** outputs error with valid paths

- **When** User enters incompatible child type
  **then** CLI identifies type incompatibility
  **and** outputs error with allowed child types

- **When** User enters duplicate name
  **then** CLI identifies duplicate
  **and** outputs error

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Story Graph is initialized
```

## Scenarios

<a id="scenario-user-creates-child-with-dot-notation-at-default-position"></a>
### Scenario: [User creates child with dot notation at default position](#scenario-user-creates-child-with-dot-notation-at-default-position) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1564)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot" with two SubEpic children
When User executes CLI command: story_graph."Invoke Bot".create_sub_epic."Manage Bot Information"
Then CLI parses dot notation to parent "Invoke Bot"
And CLI resolves parent "Invoke Bot" successfully
And CLI validates parent exists
And CLI creates SubEpic "Manage Bot Information" as last child of "Invoke Bot"
And CLI outputs success message: "Created SubEpic 'Manage Bot Information' under 'Invoke Bot' at position 2"
And Story Graph shows "Manage Bot Information" at position 2 under "Invoke Bot"
```


<a id="scenario-user-creates-child-with-position-specified"></a>
### Scenario: [User creates child with position specified](#scenario-user-creates-child-with-position-specified) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1593)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot" with children: "SubEpic A", "SubEpic B", "SubEpic C"
When User executes CLI command: story_graph."Invoke Bot".create_sub_epic name:"Info" at_position:1
Then CLI parses dot notation to parent "Invoke Bot"
And CLI parses position parameter as 1
And CLI creates SubEpic "Info" at position 1
And CLI resequences children
And CLI outputs success message: "Created SubEpic 'Info' under 'Invoke Bot' at position 1"
And Story Graph shows children in order: "SubEpic A", "Info", "SubEpic B", "SubEpic C"
```


<a id="scenario-user-creates-child-with-invalid-position-and-cli-adjusts"></a>
### Scenario: [User creates child with invalid position and CLI adjusts](#scenario-user-creates-child-with-invalid-position-and-cli-adjusts) (edge_case)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L607)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot" with two SubEpic children
When User executes CLI command: story_graph."Invoke Bot".create_sub_epic name:"Info" at_position:99
Then CLI parses position parameter as 99
And CLI detects position 99 exceeds children count of 2
And CLI adjusts position to 2
And CLI creates SubEpic "Info" at adjusted position 2
And CLI outputs success message: "Created SubEpic 'Info' under 'Invoke Bot' at position 2 (adjusted from 99)"
And Story Graph shows "Info" as last child
```


<a id="scenario-user-enters-non-existent-parent-path-and-cli-outputs-error"></a>
### Scenario: [User enters non-existent parent path and CLI outputs error](#scenario-user-enters-non-existent-parent-path-and-cli-outputs-error) (error_case)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1649)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot"
And Story Graph does not have Epic "Non-existent Epic"
When User executes CLI command: story_graph."Non-existent Epic".create_sub_epic name:"New SubEpic"
Then CLI parses dot notation to parent "Non-existent Epic"
And CLI attempts to resolve parent "Non-existent Epic"
And CLI identifies parent does not exist
And CLI outputs error: "Parent 'Non-existent Epic' not found. Valid paths: 'Invoke Bot'"
And CLI does not create SubEpic
```


<a id="scenario-user-enters-incompatible-child-type-and-cli-outputs-error"></a>
### Scenario: [User enters incompatible child type and CLI outputs error](#scenario-user-enters-incompatible-child-type-and-cli-outputs-error) (error_case)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1673)

**Steps:**
```gherkin
And Story Graph has SubEpic "Authentication" with child Story "Login Form"
When User executes CLI command: story_graph."Authentication".create_sub_epic name:"OAuth Flow"
Then CLI parses dot notation to parent "Authentication"
And CLI resolves parent "Authentication" successfully
And CLI identifies parent "Authentication" already contains Stories
And CLI identifies SubEpic is incompatible child type for SubEpic with Stories
And CLI outputs error: "Cannot create SubEpic under SubEpic 'Authentication' that contains Stories. Allowed child types: Story"
And CLI does not create SubEpic "OAuth Flow"
```


<a id="scenario-user-enters-duplicate-name-and-cli-outputs-error"></a>
### Scenario: [User enters duplicate name and CLI outputs error](#scenario-user-enters-duplicate-name-and-cli-outputs-error) (error_case)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1697)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot" with SubEpic "Manage Bot Information"
When User executes CLI command: story_graph."Invoke Bot".create_sub_epic."Manage Bot Information"
Then CLI parses dot notation to parent "Invoke Bot"
And CLI resolves parent "Invoke Bot" successfully
And CLI validates child name "Manage Bot Information"
And CLI identifies duplicate name among siblings
And CLI outputs error: "Child with name 'Manage Bot Information' already exists under parent 'Invoke Bot'"
And CLI does not create duplicate SubEpic
```


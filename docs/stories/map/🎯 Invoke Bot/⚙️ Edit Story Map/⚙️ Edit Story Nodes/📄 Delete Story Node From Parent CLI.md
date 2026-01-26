# 📄 Delete Story Node From Parent CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1730)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Edit Story Nodes](.)  
**Sequential Order:** 9.0
**Story Type:** user

## Story Description

Delete Story Node From Parent CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User deletes node with dot notation
  **then** CLI parses notation to node
  **and** resolves and validates node exists
  **and** removes node from parent
  **and** resequences siblings
  **and** outputs success message

- **When** User deletes node with children
  **then** CLI moves children to node's parent [ - see previous acceptance criteria]
  **and** removes node

- **When** User enters non-existent node path
  **then** CLI identifies node does not exist
  **and** outputs error with valid paths

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Story Graph is initialized
```

## Scenarios

<a id="scenario-user-deletes-node-without-children-using-dot-notation"></a>
### Scenario: [User deletes node without children using dot notation](#scenario-user-deletes-node-without-children-using-dot-notation) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L796)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot" with SubEpics: "SubEpic A", "Manage Bot", "SubEpic B"
And SubEpic "Manage Bot" has no children
When User executes CLI command: story_graph."Invoke Bot"."Manage Bot".delete
Then CLI parses dot notation to node "Manage Bot"
And CLI resolves node "Manage Bot" successfully
And CLI validates node exists
And CLI removes node "Manage Bot" from parent "Invoke Bot"
And CLI resequences siblings
And CLI outputs success message: "Deleted SubEpic 'Manage Bot' from 'Invoke Bot'"
And Epic "Invoke Bot" shows children: "SubEpic A", "SubEpic B"
```


<a id="scenario-user-deletes-node-with-children-and-cli-moves-children-to-parent"></a>
### Scenario: [User deletes node with children and CLI moves children to parent](#scenario-user-deletes-node-with-children-and-cli-moves-children-to-parent) (happy_path)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot" with SubEpic "Manage Bot"
And SubEpic "Manage Bot" has children Stories: "Story A", "Story B"
When User executes CLI command: story_graph."Invoke Bot"."Manage Bot".delete
Then CLI parses dot notation to node "Manage Bot"
And CLI resolves node "Manage Bot" successfully
And CLI moves children "Story A" and "Story B" to Epic "Invoke Bot"
And CLI removes node "Manage Bot"
And CLI resequences siblings
And CLI outputs success message: "Deleted SubEpic 'Manage Bot' from 'Invoke Bot'. Moved 2 children to parent."
And Epic "Invoke Bot" shows children including "Story A" and "Story B"
```


<a id="scenario-user-enters-non-existent-node-path-and-cli-outputs-error"></a>
### Scenario: [User enters non-existent node path and CLI outputs error](#scenario-user-enters-non-existent-node-path-and-cli-outputs-error) (error_case)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1773)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot" with SubEpic "Manage Bot"
And Story Graph does not have SubEpic "Non-existent Node"
When User executes CLI command: story_graph."Invoke Bot"."Non-existent Node".delete
Then CLI parses dot notation to node "Non-existent Node"
And CLI attempts to resolve node "Non-existent Node"
And CLI identifies node does not exist
And CLI outputs error: "Node 'Non-existent Node' not found. Valid paths under 'Invoke Bot': 'Manage Bot'"
And CLI does not modify Story Graph
```


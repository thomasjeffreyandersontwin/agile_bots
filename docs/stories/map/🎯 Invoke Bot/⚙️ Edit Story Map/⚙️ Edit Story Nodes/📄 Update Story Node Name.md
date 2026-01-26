# 📄 Update Story Node Name

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L878)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Edit Story Nodes](.)  
**Sequential Order:** 16.0
**Story Type:** user

## Story Description

Update Story Node Name functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-rename-node-with-valid-name-across-hierarchy-levels"></a>
### Scenario: [Rename node with valid name across hierarchy levels](#scenario-rename-node-with-valid-name-across-hierarchy-levels) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L888)

**Steps:**
```gherkin
GIVEN: Node exists with old name
WHEN: Node is renamed to new valid name
THEN: Node name is updated and accessible by new name
```


<a id="scenario-rename-node-with-empty-or-whitespace-name-returns-error"></a>
### Scenario: [Rename node with empty or whitespace name returns error](#scenario-rename-node-with-empty-or-whitespace-name-returns-error) (error)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L919)

**Steps:**
```gherkin
GIVEN: Node exists with current name
WHEN: Attempting to rename to empty or whitespace name
THEN: System identifies invalid name and returns error
```


<a id="scenario-rename-node-with-duplicate-sibling-name-returns-error"></a>
### Scenario: [Rename node with duplicate sibling name returns error](#scenario-rename-node-with-duplicate-sibling-name-returns-error) (error)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L949)

**Steps:**
```gherkin
GIVEN: Parent has multiple children including target node
WHEN: Attempting to rename node to existing sibling name
THEN: System identifies duplicate and returns error
```


<a id="scenario-rename-node-with-valid-special-characters"></a>
### Scenario: [Rename node with valid special characters](#scenario-rename-node-with-valid-special-characters) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L982)

**Steps:**
```gherkin
GIVEN: Node exists with old name
WHEN: Renaming to name with valid special characters
THEN: Name is updated and special characters are preserved
```


<a id="scenario-rename-node-with-invalid-special-characters-returns-error"></a>
### Scenario: [Rename node with invalid special characters returns error](#scenario-rename-node-with-invalid-special-characters-returns-error) (error)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L1014)

**Steps:**
```gherkin
GIVEN: Node exists with current name
WHEN: Attempting to rename with invalid special characters
THEN: System identifies invalid characters and returns error
```


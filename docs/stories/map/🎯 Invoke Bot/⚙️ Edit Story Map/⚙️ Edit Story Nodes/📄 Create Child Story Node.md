# 📄 Create Child Story Node

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L543)

**User:** System
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Edit Story Nodes](.)  
**Sequential Order:** 3.0
**Story Type:** user

## Story Description

Create Child Story Node functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-create-child-node-at-any-hierarchy-level-with-default-position"></a>
### Scenario: [Create child node at any hierarchy level with default position](#scenario-create-child-node-at-any-hierarchy-level-with-default-position) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L555)

**Steps:**
```gherkin
Given Story Graph has parent node with existing children
When Parent creates child node of specified type
Then Child is added at last position with correct total count
```


<a id="scenario-create-child-node-with-specified-position"></a>
### Scenario: [Create child node with specified position](#scenario-create-child-node-with-specified-position) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L585)

**Steps:**
```gherkin
Given Story Graph has parent node with existing children
When Parent creates child node at specific position
Then Child is inserted at position and existing children shift
```


<a id="scenario-create-child-node-with-invalid-position-adjusts-to-last-position"></a>
### Scenario: [Create child node with invalid position adjusts to last position](#scenario-create-child-node-with-invalid-position-adjusts-to-last-position) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L615)

**Steps:**
```gherkin
Given Story Graph has parent node with existing children
When Parent creates child node at invalid position (exceeds child count)
Then System adjusts position to last valid position
```


<a id="scenario-create-child-node-with-duplicate-name-returns-error"></a>
### Scenario: [Create child node with duplicate name returns error](#scenario-create-child-node-with-duplicate-name-returns-error) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L645)

**Steps:**
```gherkin
Given Story Graph has parent node with existing child
When Parent attempts to create child with duplicate name
Then System identifies duplicate and returns error
```


<a id="scenario-create-child-node-without-name-generates-unique-name"></a>
### Scenario: [Create child node without name generates unique name](#scenario-create-child-node-without-name-generates-unique-name) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L674)

**Steps:**
```gherkin
Given Story Graph has parent node with existing children
When Parent creates child without providing name
Then System generates unique name (Child1, Child2, etc.)
```


<a id="scenario-subepic-creates-story-and-auto-creates-storygroup-on-first-story"></a>
### Scenario: [SubEpic creates Story and auto-creates StoryGroup on first Story](#scenario-subepic-creates-story-and-auto-creates-storygroup-on-first-story) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L703)

**Steps:**
```gherkin
Given SubEpic has existing Story count (0 or more)
When SubEpic creates new Story
Then StoryGroup is created (if first) or existing StoryGroup is used
```


<a id="scenario-subepic-with-stories-cannot-create-subepic-child"></a>
### Scenario: [SubEpic with Stories cannot create SubEpic child](#scenario-subepic-with-stories-cannot-create-subepic-child) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L727)

**Steps:**
```gherkin
Given SubEpic has existing Story children
When SubEpic attempts to create SubEpic child
Then System identifies hierarchy violation and returns error
```


<a id="scenario-subepic-with-subepics-cannot-create-story-child"></a>
### Scenario: [SubEpic with SubEpics cannot create Story child](#scenario-subepic-with-subepics-cannot-create-story-child) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L749)

**Steps:**
```gherkin
Given SubEpic has existing SubEpic children
When SubEpic attempts to create Story child
Then System identifies hierarchy violation and returns error
```


<a id="scenario-story-creates-child-and-adds-to-correct-collection"></a>
### Scenario: [Story creates child and adds to correct collection](#scenario-story-creates-child-and-adds-to-correct-collection) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L772)

**Steps:**
```gherkin
Given Story exists in story graph
When Story creates child of specific type (Scenario, ScenarioOutline, AcceptanceCriteria)
Then Child is added to correct collection and not to others
```


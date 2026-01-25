# 📄 Create Epic

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L362)

**User:** System
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Edit Story Nodes](.)  
**Sequential Order:** 7.0
**Story Type:** user

## Story Description

Create Epic functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-create-epic-with-name-at-default-position"></a>
### Scenario: [Create Epic with name at default position](#scenario-create-epic-with-name-at-default-position) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L365)

**Steps:**
```gherkin
Given Story Map is initialized
When Story Map creates Epic with name
Then Epic is added at last position
```


<a id="scenario-create-epic-with-position-specified"></a>
### Scenario: [Create Epic with position specified](#scenario-create-epic-with-position-specified) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L383)

**Steps:**
```gherkin
Given Story Map has existing Epics
When Story Map creates Epic at specific position
Then Epic is inserted at position and existing Epics shift
```


<a id="scenario-create-epic-with-invalid-position-adjusts-to-last"></a>
### Scenario: [Create Epic with invalid position adjusts to last](#scenario-create-epic-with-invalid-position-adjusts-to-last) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L404)

**Steps:**
```gherkin
Given Story Map has 2 Epics
When Story Map creates Epic at position 99
Then Position is adjusted to last (position 2)
```


<a id="scenario-create-epic-without-name-generates-unique-name"></a>
### Scenario: [Create Epic without name generates unique name](#scenario-create-epic-without-name-generates-unique-name) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L422)

**Steps:**
```gherkin
Given Story Map has existing Epics
When Story Map creates Epic without name
Then System generates unique name (Epic1, Epic2, etc.)
```


<a id="scenario-create-epic-with-duplicate-name-returns-error"></a>
### Scenario: [Create Epic with duplicate name returns error](#scenario-create-epic-with-duplicate-name-returns-error) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L446)

**Steps:**
```gherkin
Given Story Map has Epic "User Management"
When Story Map attempts to create Epic with duplicate name
Then System identifies duplicate and returns error
```


<a id="scenario-create-epic-updates-epics-collection"></a>
### Scenario: [Create Epic updates epics collection](#scenario-create-epic-updates-epics-collection) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L461)

**Steps:**
```gherkin
Given Story Map has existing Epics
When Story Map creates new Epic
Then Epics collection is updated and new Epic is accessible
```


<a id="scenario-create-epic-updates-underlying-story_graph-dict"></a>
### Scenario: [Create Epic updates underlying story_graph dict](#scenario-create-epic-updates-underlying-story_graph-dict) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L478)

**Steps:**
```gherkin
Given Story Map has existing Epics
When Story Map creates new Epic
Then story_graph dict is updated with new Epic
```


<a id="scenario-create-multiple-epics-in-sequence"></a>
### Scenario: [Create multiple Epics in sequence](#scenario-create-multiple-epics-in-sequence) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L495)

**Steps:**
```gherkin
Given Story Map is initialized
When Story Map creates multiple Epics
Then All Epics are added in correct order
```


<a id="scenario-create-epic-at-beginning-position-0"></a>
### Scenario: [Create Epic at beginning (position 0)](#scenario-create-epic-at-beginning-position-0) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_edit_story_nodes.py#L517)

**Steps:**
```gherkin
Given Story Map has existing Epics
When Story Map creates Epic at position 0
Then Epic is inserted at beginning
```


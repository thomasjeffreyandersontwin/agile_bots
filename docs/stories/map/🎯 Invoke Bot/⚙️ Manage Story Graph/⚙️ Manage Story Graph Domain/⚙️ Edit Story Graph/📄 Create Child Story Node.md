# 📄 Create Child Story Node

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Story Graph Node
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Manage Story Graph](..) / [⚙️ Manage Story Graph Domain](..) / [⚙️ Edit Story Graph](.)  
**Sequential Order:** 1.0
**Story Type:** user

## Story Description

Create Child Story Node functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Story Graph Node creates new child Node
  **then** parent Story Node creates new child node of appropriate type with provided name
  **and** parent Story Node adds the child as the last child of its children

- **When** Story Graph Node creates new child with position specified
  **then** parent Story Node adds the child as the specified position
  **and** resequences all children at or after the position

- **When** Story Graph Node creates new child with invalid position specified
  **then** adjusts position to last if exceeds children count
  **and** creates new child node with provided data at adjusted position

- **When** Story Graph Node creates new child with identical name as another child of Node
  **then** Story Graph Node identifies duplicate name
  **and** returns error

- **When** Story Graph Node creates new child without a name
  **then** System populates name with unique field (eg: Child1)

- **When** Epic creates a child SubEpic
  **then** Epic adds Sub-Epic to children

- **When** SubEpic with no Story children creates a child SubEpic
  **then** SubEpic adds SubEpic to children

- **When** SubEpic creates Sub-Epic that has Stories children
  **then** SubEpic identifies SubEpic already contains Stories
  **and** returns error indicating cannot create SubEpic under SubEpic with Stories

- **When** Sub-Epic with no SubEpic children creates a child Story
  **then** Sub-Epic creates default StoryGroup under Sub-Epic
  **and** Sub-Epic adds Story to Story Group

- **When** SubEpic creates a child Story with existing Story children
  **then** SubEpic adds Story to existing SubEpic's Story Group

- **When** SubEpic creates Story that has SubEpic children
  **then** SubEpic identifies SubEpic already contains Sub-Epics
  **and** returns error indicating cannot create Story under SubEpic with Sub-Epics

- **When** Story creates Scenario
  **then** Story adds Scenario to common scenario child collection

- **When** Story creates ScenarioOutline
  **then** Story adds ScenarioOutline to common scenario child collection

- **When** Story creates AcceptanceCriteria
  **then** Story adds Acceptance Criteria to its own child collection

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Story Graph is initialized
```

## Scenarios

<a id="scenario-create-child-node-at-any-hierarchy-level-with-default-position"></a>
### Scenario: [Create child node at any hierarchy level with default position](#scenario-create-child-node-at-any-hierarchy-level-with-default-position) (happy_path)

**Steps:**
```gherkin
Given Story Graph has "<parent_type>" named "<parent_name>" with <existing_count> existing children
When "<parent_name>" creates child node "<child_name>" of type "<child_type>"
Then Story Graph contains "<child_type>" named "<child_name>" under parent "<parent_name>"
And child node "<child_name>" is at position <expected_position>
And parent "<parent_name>" has <total_children> total children
```

**Examples:**
| parent_type | parent_name | existing_count | child_type | child_name | expected_position | total_children |
| --- | --- | --- | --- | --- | --- | --- |
| Epic | User Management | 0 | SubEpic | Authentication | 0 | 1 |
| Epic | User Management | 2 | SubEpic | Authorization | 2 | 3 |
| SubEpic | Authentication | 0 | SubEpic | Login Flow | 0 | 1 |
| SubEpic | Login Flow | 1 | Story | Validate Password | 0 | 1 |
| Story | Validate Password | 0 | Scenario | Valid Password Entered | 0 | 1 |
| Story | Validate Password | 2 | Scenario | Invalid Password Entered | 2 | 3 |


<a id="scenario-create-child-node-with-specified-position"></a>
### Scenario: [Create child node with specified position](#scenario-create-child-node-with-specified-position) (happy_path)

**Steps:**
```gherkin
Given Story Graph has "<parent_type>" named "<parent_name>" with children: <existing_children>
When "<parent_name>" creates child node "<new_child_name>" at position <target_position>
Then Story Graph shows children of "<parent_name>" in order: <final_order>
And child node "<new_child_name>" is at position <target_position>
```

**Examples:**
| parent_type | parent_name | existing_children | new_child_name | target_position | final_order |
| --- | --- | --- | --- | --- | --- |
| Epic | User Management | SubEpic A, SubEpic B | SubEpic C | 0 | SubEpic C, SubEpic A, SubEpic B |
| Epic | User Management | SubEpic A, SubEpic B | SubEpic C | 1 | SubEpic A, SubEpic C, SubEpic B |
| SubEpic | Authentication | Story A, Story B, Story C | Story D | 2 | Story A, Story B, Story D, Story C |


<a id="scenario-create-child-node-with-invalid-position-adjusts-to-last-position"></a>
### Scenario: [Create child node with invalid position adjusts to last position](#scenario-create-child-node-with-invalid-position-adjusts-to-last-position) (edge_case)

**Steps:**
```gherkin
Given Story Graph has "<parent_type>" named "<parent_name>" with <child_count> children
When "<parent_name>" creates child node "<child_name>" at position <invalid_position>
Then system adjusts position to <adjusted_position>
And child node "<child_name>" is created at position <adjusted_position>
And parent "<parent_name>" has <total_children> total children
```

**Examples:**
| parent_type | parent_name | child_count | child_name | invalid_position | adjusted_position | total_children |
| --- | --- | --- | --- | --- | --- | --- |
| Epic | User Management | 3 | New SubEpic | 99 | 3 | 4 |
| Epic | User Management | 0 | First SubEpic | 5 | 0 | 1 |
| SubEpic | Authentication | 2 | New Story | 10 | 2 | 3 |


<a id="scenario-create-child-node-with-duplicate-name-returns-error"></a>
### Scenario: [Create child node with duplicate name returns error](#scenario-create-child-node-with-duplicate-name-returns-error) (error_case)

**Steps:**
```gherkin
Given Story Graph has "<parent_type>" named "<parent_name>"
And "<parent_name>" has child "<existing_child_name>" of type "<child_type>"
When "<parent_name>" attempts to create child node "<duplicate_name>" of type "<child_type>"
Then system identifies duplicate name
And returns error "<error_message>"
And child node "<duplicate_name>" is not created
```

**Examples:**
| parent_type | parent_name | child_type | existing_child_name | duplicate_name | error_message |
| --- | --- | --- | --- | --- | --- |
| Epic | User Management | SubEpic | Authentication | Authentication | Child with name 'Authentication' already exists under parent 'User Management' |
| SubEpic | Authentication | Story | Login Form | Login Form | Child with name 'Login Form' already exists under parent 'Authentication' |
| Story | Validate Password | Scenario | Valid Password | Valid Password | Child with name 'Valid Password' already exists under parent 'Validate Password' |


<a id="scenario-create-child-node-without-name-generates-unique-name"></a>
### Scenario: [Create child node without name generates unique name](#scenario-create-child-node-without-name-generates-unique-name) (edge_case)

**Steps:**
```gherkin
Given Story Graph has "<parent_type>" named "<parent_name>" with children: <existing_children>
When "<parent_name>" creates child node without name
Then system generates unique name "<generated_name>"
And child node is created with name "<generated_name>"
And "<generated_name>" is unique among siblings
```

**Examples:**
| parent_type | parent_name | existing_children | generated_name |
| --- | --- | --- | --- |
| Epic | User Management | none | Child1 |
| Epic | User Management | Child1 | Child2 |
| Epic | User Management | Child1, Child2 | Child3 |
| SubEpic | Authentication | Story1, Story2 | Story3 |


<a id="scenario-subepic-creates-story-and-auto-creates-storygroup-on-first-story"></a>
### Scenario: [SubEpic creates Story and auto-creates StoryGroup on first Story](#scenario-subepic-creates-story-and-auto-creates-storygroup-on-first-story) (happy_path)

**Steps:**
```gherkin
Given Story Graph has SubEpic "<subepic_name>" with <existing_story_count> Stories
When SubEpic "<subepic_name>" creates child Story "<story_name>"
Then SubEpic "<subepic_name>" <story_group_action>
And Story "<story_name>" is added to StoryGroup
And Story "<story_name>" is at position <story_position> in StoryGroup
```

**Examples:**
| subepic_name | existing_story_count | story_name | story_group_action | story_position |
| --- | --- | --- | --- | --- |
| Authentication | 0 | Login Form | creates default StoryGroup | 0 |
| Authentication | 1 | Password Reset | uses existing StoryGroup | 1 |
| Authentication | 3 | Two-Factor Auth | uses existing StoryGroup | 3 |


<a id="scenario-subepic-with-stories-cannot-create-subepic-child"></a>
### Scenario: [SubEpic with Stories cannot create SubEpic child](#scenario-subepic-with-stories-cannot-create-subepic-child) (error_case)

**Steps:**
```gherkin
Given Story Graph has SubEpic "<subepic_name>"
And SubEpic "<subepic_name>" has child Story "<existing_story>"
When SubEpic "<subepic_name>" attempts to create child SubEpic "<new_subepic_name>"
Then system identifies SubEpic already contains Stories
And returns error "Cannot create SubEpic under SubEpic with Stories"
And operation is prevented
And SubEpic "<new_subepic_name>" is not created
```

**Examples:**
| subepic_name | existing_story | new_subepic_name |
| --- | --- | --- |
| Authentication | Login Form | OAuth Flow |
| User Profile | Edit Profile | Profile Settings |


<a id="scenario-subepic-with-subepics-cannot-create-story-child"></a>
### Scenario: [SubEpic with SubEpics cannot create Story child](#scenario-subepic-with-subepics-cannot-create-story-child) (error_case)

**Steps:**
```gherkin
Given Story Graph has SubEpic "<subepic_name>"
And SubEpic "<subepic_name>" has child SubEpic "<existing_subepic>"
When SubEpic "<subepic_name>" attempts to create child Story "<story_name>"
Then system identifies SubEpic already contains SubEpics
And returns error "Cannot create Story under SubEpic with SubEpics"
And operation is prevented
And Story "<story_name>" is not created
```

**Examples:**
| subepic_name | existing_subepic | story_name |
| --- | --- | --- |
| User Management | Authentication | Login Form |
| User Management | Authorization | Check Permissions |


<a id="scenario-story-creates-child-and-adds-to-correct-collection"></a>
### Scenario: [Story creates child and adds to correct collection](#scenario-story-creates-child-and-adds-to-correct-collection) (happy_path)

**Steps:**
```gherkin
Given Story Graph has Story "<story_name>"
When Story "<story_name>" creates child "<child_name>" of type "<child_type>"
Then child "<child_name>" is added to "<target_collection>" collection
And child "<child_name>" is not added to "<excluded_collection>" collection
And Story "<story_name>" "<target_collection>" collection contains "<child_name>"
```

**Examples:**
| story_name | child_type | child_name | target_collection | excluded_collection |
| --- | --- | --- | --- | --- |
| Validate Password | Scenario | Valid Password Entered | scenarios | acceptance_criteria |
| Validate Password | ScenarioOutline | Invalid Password Formats | scenario_outlines | acceptance_criteria |
| Validate Password | AcceptanceCriteria | Password Must Not Be Empty | acceptance_criteria | scenarios |


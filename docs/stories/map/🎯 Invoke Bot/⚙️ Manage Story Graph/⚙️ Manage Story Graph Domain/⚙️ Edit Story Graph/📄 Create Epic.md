# 📄 Create Epic

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Story Map
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Manage Story Graph](..) / [⚙️ Manage Story Graph Domain](..) / [⚙️ Edit Story Graph](.)  
**Sequential Order:** 0.0
**Story Type:** user

## Story Description

Create Epic functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Story Map creates new Epic
  **then** Story Map creates new Epic with provided name
  **and** Story Map adds the Epic as the last Epic in the epics collection

- **When** Story Map creates new Epic with position specified
  **then** Story Map adds the Epic at the specified position
  **and** resequences all Epics at or after the position

- **When** Story Map creates new Epic with invalid position specified
  **then** adjusts position to last if exceeds Epic count
  **and** creates new Epic at adjusted position

- **When** Story Map creates new Epic with identical name as existing Epic
  **then** Story Map identifies duplicate name
  **and** returns error

- **When** Story Map creates new Epic without a name
  **then** System populates name with unique field (Epic1, Epic2, etc.)

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Story Map is initialized
```

## Scenarios

<a id="scenario-create-epic-with-name-at-default-position"></a>
### Scenario: [Create Epic with name at default position](#scenario-create-epic-with-name-at-default-position) (happy_path)

**Steps:**
```gherkin
And Story Map has two Epics: "Epic A", "Epic B"
When Story Map creates Epic with name "User Management"
Then Epic "User Management" is added at last position
And Story Map has 3 Epics total
And Epic "User Management" is at position 2
```


<a id="scenario-create-epic-with-position-specified"></a>
### Scenario: [Create Epic with position specified](#scenario-create-epic-with-position-specified) (happy_path)

**Steps:**
```gherkin
And Story Map has three Epics: "Epic A", "Epic B", "Epic C"
When Story Map creates Epic "User Management" at position 1
Then Epic "User Management" is inserted at position 1
And Epics are reordered: "Epic A", "User Management", "Epic B", "Epic C"
```


<a id="scenario-create-epic-with-invalid-position-adjusts-to-last"></a>
### Scenario: [Create Epic with invalid position adjusts to last](#scenario-create-epic-with-invalid-position-adjusts-to-last) (edge_case)

**Steps:**
```gherkin
And Story Map has two Epics
When Story Map creates Epic "User Management" at position 99
Then position is adjusted to 2
And Epic "User Management" is added at last position
```


<a id="scenario-create-epic-without-name-generates-unique-name"></a>
### Scenario: [Create Epic without name generates unique name](#scenario-create-epic-without-name-generates-unique-name) (happy_path)

**Steps:**
```gherkin
And Story Map has Epics: "User Management", "Reporting"
When Story Map creates Epic without name
Then System generates unique name "Epic1"
And Epic "Epic1" is added to Story Map
```


<a id="scenario-create-epic-with-duplicate-name-returns-error"></a>
### Scenario: [Create Epic with duplicate name returns error](#scenario-create-epic-with-duplicate-name-returns-error) (error_case)

**Steps:**
```gherkin
And Story Map has Epic "User Management"
When Story Map attempts to create Epic with name "User Management"
Then System identifies duplicate name
And returns error: "Epic with name 'User Management' already exists"
```


# 📄 Display Strategy Instructions Panel

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Decide Strategy](.)  
**Sequential Order:** 3.0
**Story Type:** user

## Story Description

Display Strategy Instructions Panel functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Current action is strategy

  **then** System displays decision criteria with radio button options

  **and** System displays assumptions textarea

- **When** Saved strategy exists

  **then** System displays selected option for each decision criterion

  **and** Assumptions textarea remains editable

  **and** Textarea is pre-filled with saved assumptions

- **When** User edits assumptions textarea

  **then** System updates assumptions

- **When** User is on non-strategy actions (clarify, build, validate, render)

  **then** System displays saved strategy decisions and criteria as read-only

## Scenarios

<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Bot is at shape.strategy
When Panel displays instructions section
Then Panel displays decision criteria with radio options
And Panel displays assumptions textarea
And User can select option for each criterion
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel displays strategy instructions
When User selects radio option for decision criterion
Then System saves selected option
And Selection persists across panel refreshes
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Bot is at shape.strategy
And User has previously saved assumptions
When Panel displays strategy instructions
Then Assumptions textarea is displayed as editable input
And Textarea is pre-filled with saved assumptions
And User can edit and update assumptions
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Bot is at shape.strategy
And User has previously answered clarify questions
When Panel displays strategy instructions
Then Panel displays Clarify section
And Clarify section shows answered questions
And Clarify data is read-only (not editable in strategy action)
```


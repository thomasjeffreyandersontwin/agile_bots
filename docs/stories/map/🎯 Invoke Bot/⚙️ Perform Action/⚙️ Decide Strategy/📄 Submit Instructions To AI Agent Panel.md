# 📄 Submit Instructions To AI Agent Panel

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Decide Strategy](.)  
**Sequential Order:** 4.0
**Story Type:** user

## Story Description

Submit Instructions To AI Agent Panel functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

  **and** User clicks submit button

  **then** System sends instructions to AI chat

- **When** User clicks submit button

  **then** Submitted instructions include scope section

  **and** Scope section includes scope type (story/files/all)

  **and** Scope section includes scope filter values

  **and** Scope section includes complete story graph tree when scope is story-based

- **When** User has answered clarify questions or made strategy decisions

  **then** Submitted instructions include all saved guardrails

## Scenarios

<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel displays instructions for current action
When User clicks submit button
Then System sends instructions to Cursor AI chat
And Panel displays success confirmation message
And AI chat receives instructions
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel displays instructions
And Cursor AI chat is not available
When User clicks submit button
Then Panel displays error message
And Error message indicates chat unavailable
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel displays instructions
When User clicks copy button
Then Instructions are copied to clipboard
When User clicks submit button
Then Instructions are also sent to AI chat
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Bot has scope set to story Open Panel
And Scope.results contains full story graph hierarchy
When User clicks submit in panel
Then Submitted instructions contain Scope section at top
And Scope section shows Story Scope: Open Panel
And Scope section shows complete epic/sub-epic/story hierarchy
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Bot is at shape.build
And User has answered clarify questions
And User has made strategy decisions
When User clicks submit in panel
Then Submitted instructions include Clarify section with answers
And Submitted instructions include Strategy section with decisions and assumptions
And All saved guardrails are visible in submitted markdown
```


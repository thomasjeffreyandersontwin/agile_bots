# 📄 Display Clarify Instructions Panel

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Clarify Requirements](.)  
**Sequential Order:** 2.0
**Story Type:** user

## Story Description

Display Clarify Instructions Panel functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Current action is clarify

  **then** System displays key questions with editable answer textareas

  **and** System displays evidence list

- **When** User edits answer textarea

  **then** System updates answer

- **When** saved key questions and answers exists

  **then** System displays saved key questions and answers

- **When** User is on non-clarify actions and has previously made strategy decisions

  **then** System displays saved strategy decisions and criteria as read-only

## Scenarios

<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Bot is at shape.clarify
And Guardrails define key questions and evidence
When Panel displays instructions section
Then Panel displays key questions list
And Panel displays evidence requirements
And Each question has editable textarea for answers
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Panel displays clarify instructions with questions
When User types answer in question textarea
Then System saves answer
And Answer persists across panel refreshes
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given User has previously answered clarify questions
And Answers are saved in clarification.json
When Panel displays clarify instructions
Then Panel displays saved answers in textareas
```


<a id="scenario-"></a>
### Scenario: [](#scenario-) ()

**Steps:**
```gherkin
Given Bot is at shape.clarify
And User has previously made strategy decisions
When Panel displays clarify instructions
Then Panel displays Strategy section
And Strategy section shows all decision criteria with selected options
And Strategy section shows saved assumptions
And Strategy data is read-only (not editable in clarify action)
```


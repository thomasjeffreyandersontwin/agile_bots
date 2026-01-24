# 📄 Get Rules Instructions Through CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Use Rules In Prompt](.)  
**Sequential Order:** 3.0
**Story Type:** user

## Story Description

Get Rules Instructions Through CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User navigates to behavior.rules

  **then** CLI displays formatted rules digest with descriptions and DO/DON'T sections

  **and** CLI includes rule names with their file paths

  **and** CLI includes all rules from the behavior

## Scenarios

<a id="scenario-user-gets-rules-instructions-for-behavior"></a>
### Scenario: [User gets rules instructions for behavior](#scenario-user-gets-rules-instructions-for-behavior) (happy_path)

**Steps:**
```gherkin
Given Production story_bot with tests behavior (has rules)
When User enters 'tests.rules' in CLI
Then CLI displays formatted rules digest with descriptions, priorities, DO/DON'T sections
And Display includes rule names with their file paths
And All rules from behavior are included in digest
```


<a id="scenario-user-gets-rules-with-message-parameter"></a>
### Scenario: [User gets rules with message parameter](#scenario-user-gets-rules-with-message-parameter) (happy_path)

**Steps:**
```gherkin
Given Production story_bot with tests behavior
When User enters 'tests.rules "explain parameterized tests"' in CLI
Then CLI displays rules digest
And Instructions include user message requesting specific rule information
```


<a id="scenario-user-gets-rules-without-message-parameter"></a>
### Scenario: [User gets rules without message parameter](#scenario-user-gets-rules-without-message-parameter) (happy_path)

**Steps:**
```gherkin
Given Production story_bot with tests behavior
When User enters 'tests.rules' without message
Then CLI displays rules digest
And Instructions do not include user message section
```


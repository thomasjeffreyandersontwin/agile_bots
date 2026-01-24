# 📄 Display Rules

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/perform_action/test_use_rules_in_prompt.py#L22)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Use Rules In Prompt](.)  
**Sequential Order:** 0.0
**Story Type:** user

## Story Description

Display Rules functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-action-loads-and-formats-rules-digest"></a>
### Scenario: [Action loads and formats rules digest](#scenario-action-loads-and-formats-rules-digest) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_use_rules_in_prompt.py#L25)

**Steps:**
```gherkin
Given Production story_bot with tests behavior (has rules)
When Rules action executes
Then Instructions contain formatted rules digest with descriptions, priorities, DO/DON'T sections
```


<a id="scenario-rules-list-includes-file-paths-for-each-rule"></a>
### Scenario: [Rules list includes file paths for each rule](#scenario-rules-list-includes-file-paths-for-each-rule) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_use_rules_in_prompt.py#L48)

**Steps:**
```gherkin
Given Production story_bot with tests behavior (has rules)
When Rules action executes
Then Display includes rule names with their file paths
```


<a id="scenario-all-behavior-rules-are-included-in-the-digest"></a>
### Scenario: [All behavior rules are included in the digest](#scenario-all-behavior-rules-are-included-in-the-digest) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_use_rules_in_prompt.py#L71)

**Steps:**
```gherkin
Given Production story_bot with tests behavior (has multiple rules)
When Rules action executes
Then All rules from behavior are included in digest
```


<a id="scenario-user-message-is-included-in-instructions-when-provided"></a>
### Scenario: [User message is included in instructions when provided](#scenario-user-message-is-included-in-instructions-when-provided) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_use_rules_in_prompt.py#L94)

**Steps:**
```gherkin
Given Production story_bot with tests behavior
When Rules action executes with message
Then Instructions include user message
Then And User message requesting specific rule information
```


<a id="scenario-no-user-message-section-when-message-is-empty"></a>
### Scenario: [No user message section when message is empty](#scenario-no-user-message-section-when-message-is-empty) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_use_rules_in_prompt.py#L122)

**Steps:**
```gherkin
Given Production story_bot with tests behavior
When Rules action executes without message
Then Instructions do not include user message section
```


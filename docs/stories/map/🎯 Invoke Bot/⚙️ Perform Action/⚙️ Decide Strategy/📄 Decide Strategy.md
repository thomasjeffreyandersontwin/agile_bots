# 📄 Decide Strategy

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Decide Strategy](.)  
**Sequential Order:** 0.0
**Story Type:** user

## Story Description

Decide Strategy functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-action-injects-decision-criteria-and-assumptions"></a>
### Scenario: [Action Injects Decision Criteria And Assumptions](#scenario-action-injects-decision-criteria-and-assumptions) (happy_path)

**Steps:**
```gherkin
Given Production story_bot with shape behavior (has guardrails)
When Action injects strategy criteria and assumptions
Then Instructions contain all required strategy fields
```


<a id="scenario-save-strategy-data-when-parameters-are-provided"></a>
### Scenario: [Save strategy data when parameters are provided](#scenario-save-strategy-data-when-parameters-are-provided) (happy_path)

**Steps:**
```gherkin
Given Production story_bot strategy action
When do_execute is called with decisions_made and assumptions_made
Then strategy.json file is created in docs/stories/ folder
Then And file contains behavior section with decisions_made and assumptions_made
```


<a id="scenario-preserve-existing-strategy-data-when-saving"></a>
### Scenario: [Preserve existing strategy data when saving](#scenario-preserve-existing-strategy-data-when-saving) (happy_path)

**Steps:**
```gherkin
Given strategy.json already exists with data for 'discovery' behavior
When do_execute is called with parameters
Then strategy.json contains both 'discovery' and 'shape' sections
Then And Production story_bot strategy action for 'shape' behavior
Then And existing 'discovery' data is preserved
```


<a id="scenario-skip-saving-when-no-strategy-parameters-are-provided"></a>
### Scenario: [Skip saving when no strategy parameters are provided](#scenario-skip-saving-when-no-strategy-parameters-are-provided) (happy_path)

**Steps:**
```gherkin
Given Production story_bot strategy action
When do_execute is called with empty parameters
Then strategy.json file is not created
```


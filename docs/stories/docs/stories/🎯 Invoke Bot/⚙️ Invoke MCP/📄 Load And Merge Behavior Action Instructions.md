# 📄 Load And Merge Behavior Action Instructions

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke MCP](.)  
**Sequential Order:** 2
**Story Type:** user

## Story Description

Load And Merge Behavior Action Instructions functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Action method is invoked

  **then** Action loads instructions from base_actions and behavior-specific locations

  **and** Instructions are merged and returned

## Scenarios

<a id="scenario-action-loads-and-merges-instructions"></a>
### Scenario: [Action Loads And Merges Instructions](#scenario-action-loads-and-merges-instructions) (happy_path)

**Steps:**
```gherkin
Given Base and behavior-specific instructions exist
When Action method is invoked
Then Instructions are loaded from both locations and merged
```


<a id="scenario-action-uses-instructions-class-to-merge-base-and-behavior-instructions"></a>
### Scenario: [Action uses Instructions class to merge base and behavior instructions](#scenario-action-uses-instructions-class-to-merge-base-and-behavior-instructions) (happy_path)

**Steps:**
```gherkin
Given Action with BaseActionConfig and Behavior
When Action initialized
Then Action uses Instructions class to merge instructions
```


<a id="scenario-action-uses-mergedinstructions-class-when-render-instructions-present"></a>
### Scenario: [Action uses MergedInstructions class when render instructions present](#scenario-action-uses-mergedinstructions-class-when-render-instructions-present) (happy_path)

**Steps:**
```gherkin
Given RenderOutputAction with render instructions
When Action initialized
Then Action uses MergedInstructions class for merging
```


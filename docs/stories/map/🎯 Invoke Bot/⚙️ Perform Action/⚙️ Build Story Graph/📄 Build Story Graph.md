# 📄 Build Story Graph

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Build Story Graph](.)  
**Sequential Order:** 0.0
**Story Type:** user

## Story Description

Build Story Graph functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-action-injects-story-graph-template"></a>
### Scenario: [Action Injects Story Graph Template](#scenario-action-injects-story-graph-template) (happy_path)

**Steps:**
```gherkin
Given Production story_bot with shape behavior (has story graph templates)
When Action injects story graph template
Then Instructions contain template_path from existing templates
```


<a id="scenario-action-loads-and-merges-instructions"></a>
### Scenario: [Action Loads And Merges Instructions](#scenario-action-loads-and-merges-instructions) (happy_path)

**Steps:**
```gherkin
Given Production story_bot with shape behavior (has story graph templates)
When Action injects story graph and instructions
Then Instructions contain all BuildStoryGraphAction-specific fields
```


<a id="scenario-all-template-variables-are-replaced-in-instructions"></a>
### Scenario: [All Template Variables Are Replaced In Instructions](#scenario-all-template-variables-are-replaced-in-instructions) (happy_path)

**Steps:**
```gherkin
Given Production story_bot with shape behavior (has story graph templates)
When Action injects all template variables
Then Instructions contain all required BuildStoryGraphAction fields
```


<a id="scenario-prioritization-behavior-updates-existing-story-graphjson"></a>
### Scenario: [Prioritization behavior updates existing story-graph.json](#scenario-prioritization-behavior-updates-existing-story-graphjson) (happy_path)

**Steps:**
```gherkin
Given Production prioritization behavior with increments templates
When Action injects story graph template for increments
Then Instructions use production template (story_graph_increments.json) that updates existing file
Then And Existing story-graph.json in workspace
```


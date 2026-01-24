# 📄 Build Story Graph Using CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/perform_action/test_build_story_graph.py#L114)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Build Story Graph](.)  
**Sequential Order:** 1.0
**Story Type:** user

## Story Description

Build Story Graph Using CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-build-action-shows-story-graph-template-in-cli-output"></a>
### Scenario: [Build action shows story graph template in CLI output](#scenario-build-action-shows-story-graph-template-in-cli-output) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_build_story_graph.py#L127)

**Steps:**
```gherkin
GIVEN: CLI is at shape.build
WHEN: user navigates to shape.build
THEN: CLI output contains template_path information
```


<a id="scenario-build-action-shows-complete-build-story-graph-instructions"></a>
### Scenario: [Build action shows complete build story graph instructions](#scenario-build-action-shows-complete-build-story-graph-instructions) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_build_story_graph.py#L153)

**Steps:**
```gherkin
GIVEN: CLI is at shape.build
WHEN: user navigates to shape.build
THEN: CLI output contains all BuildStoryGraphAction fields
```


<a id="scenario-prioritization-validate-action-shows-increments-validation"></a>
### Scenario: [Prioritization validate action shows increments validation](#scenario-prioritization-validate-action-shows-increments-validation) (happy_path)  | [Test](/test/invoke_bot/perform_action/test_build_story_graph.py#L178)

**Steps:**
```gherkin
GIVEN: CLI is at prioritization.validate
AND: Story graph exists in workspace
WHEN: user navigates to prioritization.validate
THEN: CLI output shows validation instructions for increments
```


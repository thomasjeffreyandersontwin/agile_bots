# 📄 Submit Action Scoped To Story Scope  CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Submit Scoped Action](.)  
**Sequential Order:** 2.0
**Story Type:** user

## Story Description

Submit Action Scoped To Story Scope  CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** User executes action with dot notation
  **then** CLI parses notation to scope
  **and** resolves and validates scope exists
  **and** validates action exists
  **and** executes action with scope context
  **and** outputs result

- **When** User enters non-existent scope path
  **then** CLI identifies scope does not exist [ - see previous acceptance criteria]
  **and** outputs error with valid paths

- **When** Action execution causes the story_graph to change
  **then** CLI validates graph structure
  **and** outputs success message

## Background

**Common setup steps shared across all scenarios:**

```gherkin
Given Story Graph is initialized
```

## Scenarios

<a id="scenario-user-executes-action-with-dot-notation-and-cli-executes-action"></a>
### Scenario: [User executes action with dot notation and CLI executes action](#scenario-user-executes-action-with-dot-notation-and-cli-executes-action) (happy_path)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot" with SubEpic "Manage Story Graph"
And SubEpic "Manage Story Graph" has action "build" available
When User executes CLI command: story_graph."Invoke Bot"."Manage Story Graph".build.output."docs/stories"
Then CLI parses dot notation to scope "Manage Story Graph"
And CLI resolves scope "Manage Story Graph" successfully
And CLI validates scope exists
And CLI validates action "build" exists for scope
And CLI parses parameters: output="docs/stories"
And CLI executes action "build" with scope context "Manage Story Graph"
And CLI outputs action result
And CLI outputs success message: "Action 'build' completed for scope 'Manage Story Graph'"
```


<a id="scenario-user-enters-non-existent-scope-path-and-cli-outputs-error"></a>
### Scenario: [User enters non-existent scope path and CLI outputs error](#scenario-user-enters-non-existent-scope-path-and-cli-outputs-error) (error_case)

**Steps:**
```gherkin
And Story Graph has Epic "Invoke Bot"
And Story Graph does not have SubEpic "Non-existent Scope"
When User executes CLI command: story_graph."Invoke Bot"."Non-existent Scope".build
Then CLI parses dot notation to scope "Non-existent Scope"
And CLI attempts to resolve scope "Non-existent Scope"
And CLI identifies scope does not exist
And CLI outputs error: "Scope 'Non-existent Scope' not found. Valid paths under 'Invoke Bot': (empty)"
And CLI does not execute action
```


<a id="scenario-action-execution-modifies-graph-and-cli-validates-and-outputs-success"></a>
### Scenario: [Action execution modifies graph and CLI validates and outputs success](#scenario-action-execution-modifies-graph-and-cli-validates-and-outputs-success) (happy_path)

**Steps:**
```gherkin
And Story Graph has Story "Create Scenarios" with action "generate_scenarios"
When User executes CLI command: story_graph."Create Scenarios".generate_scenarios
And CLI executes action successfully
And action modifies story graph by adding new scenarios to Story "Create Scenarios"
Then CLI validates updated graph structure
And CLI confirms graph structure is valid
And CLI outputs success message: "Action 'generate_scenarios' completed. Story graph updated with 3 new scenarios."
And Story Graph shows Story "Create Scenarios" with new scenarios added
```


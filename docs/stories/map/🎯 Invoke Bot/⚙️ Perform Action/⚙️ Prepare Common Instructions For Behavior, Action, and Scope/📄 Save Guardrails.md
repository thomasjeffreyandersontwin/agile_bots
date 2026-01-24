# 📄 Save Guardrails

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** System
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Prepare Common Instructions For Behavior, Action, and Scope](.)  
**Sequential Order:** 5.0
**Story Type:** user

## Story Description

Save Guardrails functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-save-answers-to-clarification-file"></a>
### Scenario: [Save answers to clarification file](#scenario-save-answers-to-clarification-file) ()

**Steps:**
```gherkin
Given Bot is at shape behavior
And Behavior has clarify action
When Action saves answers with question What is the scope of this work as Building bot system
Then System loads existing clarification.json for shape behavior
And System merges new answer with existing answers
And System saves updated clarification.json to workspace docs folder
And File contains shape behavior section with saved answer
```


<a id="scenario-save-evidence-to-clarification-file"></a>
### Scenario: [Save evidence to clarification file](#scenario-save-evidence-to-clarification-file) ()

**Steps:**
```gherkin
Given Bot is at shape behavior
And Behavior has clarify action
When Action saves evidence with Requirements doc as spec.md and User interviews as notes.md
Then System loads existing clarification.json for shape behavior
And System merges new evidence with existing evidence
And System saves updated clarification.json to workspace docs folder
And File contains shape behavior section with saved evidence
```


<a id="scenario-save-decisions-to-strategy-file"></a>
### Scenario: [Save decisions to strategy file](#scenario-save-decisions-to-strategy-file) ()

**Steps:**
```gherkin
Given Bot is at shape behavior
And Behavior has strategy action
When Action saves decisions with drill_down_approach as Dig deep on system interactions
Then System loads existing strategy.json for shape behavior
And System merges new decision with existing decisions
And System saves updated strategy.json to workspace docs folder
And File contains shape behavior section with saved decision
```


<a id="scenario-save-assumptions-to-strategy-file"></a>
### Scenario: [Save assumptions to strategy file](#scenario-save-assumptions-to-strategy-file) ()

**Steps:**
```gherkin
Given Bot is at shape behavior
And Behavior has strategy action
When Action saves assumptions with Focus on user flow over internal systems
Then System loads existing strategy.json for shape behavior
And System merges new assumption with existing assumptions
And System saves updated strategy.json to workspace docs folder
And File contains shape behavior section with saved assumption
```


<a id="scenario-merge-preserves-existing-answer-fields"></a>
### Scenario: [Merge preserves existing answer fields](#scenario-merge-preserves-existing-answer-fields) ()

**Steps:**
```gherkin
Given clarification.json contains existing answers for shape behavior
And Existing answers include What is the scope of this work as Building bot system
And Existing answers include Who are the target users as AI Agents
When Action saves updated answer Who are the target users as Developers and AI Agents
Then System preserves What is the scope of this work as Building bot system
And System overwrites Who are the target users to Developers and AI Agents
And clarification.json contains both answers with new value for updated field
```


<a id="scenario-merge-preserves-existing-decision-fields"></a>
### Scenario: [Merge preserves existing decision fields](#scenario-merge-preserves-existing-decision-fields) ()

**Steps:**
```gherkin
Given strategy.json contains existing decisions for shape behavior
And Existing decisions include drill_down_approach as High and wide across all epics
And Existing decisions include depth_of_shaping as Extensive
When Action saves updated decision drill_down_approach as Dig deep on system interactions
Then System preserves depth_of_shaping as Extensive
And System overwrites drill_down_approach to Dig deep on system interactions
And strategy.json contains both decisions with new value for updated field
```


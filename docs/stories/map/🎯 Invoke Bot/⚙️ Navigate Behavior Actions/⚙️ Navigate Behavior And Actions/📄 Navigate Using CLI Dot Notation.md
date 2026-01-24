# 📄 Navigate Using CLI Dot Notation

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Navigate Behavior Actions](..) / [⚙️ Navigate Behavior And Actions](.)  
**Sequential Order:** 2.0
**Story Type:** user

## Story Description

Navigate Using CLI Dot Notation functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-user-navigates-with-behavior-only-no-dots"></a>
### Scenario: [User navigates with behavior only (no dots)](#scenario-user-navigates-with-behavior-only-no-dots) ()

**Steps:**
```gherkin
GIVEN: CLI is at shape.clarify.instructions
WHEN: user enters 'discovery'
THEN: CLI navigates to discovery.clarify (first action)
```


<a id="scenario-user-navigates-with-behavioraction-one-dot"></a>
### Scenario: [User navigates with behavior.action (one dot)](#scenario-user-navigates-with-behavioraction-one-dot) ()

**Steps:**
```gherkin
GIVEN: CLI is at shape.clarify.instructions
WHEN: user enters 'discovery.build'
THEN: CLI navigates to discovery.build.instructions
```


<a id="scenario-user-navigates-with-behavioractionoperation-two-dots"></a>
### Scenario: [User navigates with behavior.action.operation (two dots)](#scenario-user-navigates-with-behavioractionoperation-two-dots) ()

**Steps:**
```gherkin
GIVEN: CLI is at shape.clarify.instructions
WHEN: user enters 'discovery.build.instructions'
THEN: CLI executes discovery.build.instructions
```


<a id="scenario-user-enters-invalid-behavior-in-dot-notation"></a>
### Scenario: [User enters invalid behavior in dot notation](#scenario-user-enters-invalid-behavior-in-dot-notation) ()

**Steps:**
```gherkin
GIVEN: CLI is at shape.clarify.instructions
WHEN: user enters 'invalid_behavior.build.instructions'
THEN: CLI displays error message
```


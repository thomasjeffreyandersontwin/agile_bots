# 📄 Navigate Sequentially Using CLI Commands

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/navigate_behavior_actions/test_navigate_behavior_and_actions.py#L355)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Navigate Behavior Actions](..) / [⚙️ Navigate Behavior And Actions](.)  
**Sequential Order:** 3.0
**Story Type:** user

## Story Description

Navigate Sequentially Using CLI Commands functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-user-navigates-with-next-command"></a>
### Scenario: [User navigates with next command](#scenario-user-navigates-with-next-command) ()

**Steps:**
```gherkin
GIVEN: CLI is at shape.clarify.instructions
WHEN: user enters 'next'
THEN: CLI navigates to shape.strategy
```


<a id="scenario-user-navigates-with-back-command"></a>
### Scenario: [User navigates with back command](#scenario-user-navigates-with-back-command) ()

**Steps:**
```gherkin
GIVEN: CLI is at shape.strategy.instructions
WHEN: user enters 'back'
THEN: CLI navigates to shape.clarify
```


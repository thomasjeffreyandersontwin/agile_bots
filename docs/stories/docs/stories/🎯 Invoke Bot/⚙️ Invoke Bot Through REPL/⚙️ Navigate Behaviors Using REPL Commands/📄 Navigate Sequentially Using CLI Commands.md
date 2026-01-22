# 📄 Navigate Sequentially Using CLI Commands

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through REPL](..) / [⚙️ Navigate Behaviors Using REPL Commands](.)  
**Sequential Order:** 2
**Story Type:** user

## Story Description

Navigate Sequentially Using CLI Commands functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-user-navigates-with-next-command"></a>
### Scenario: [User navigates with next command](#scenario-user-navigates-with-next-command) (happy_path)

**Steps:**
```gherkin
GIVEN: CLI is at shape.clarify.instructions
WHEN: user enters 'next'
THEN: CLI navigates to shape.strategy
```


<a id="scenario-user-navigates-with-back-command"></a>
### Scenario: [User navigates with back command](#scenario-user-navigates-with-back-command) (happy_path)

**Steps:**
```gherkin
GIVEN: CLI is at shape.strategy.instructions
WHEN: user enters 'back'
THEN: CLI navigates to shape.clarify
```


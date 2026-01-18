# 📄 Show Remaining Actions After Completion

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** System
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through REPL](..) / [⚙️ Navigate Behaviors Using Domain Model](.)  
**Sequential Order:** 3
**Story Type:** system

## Story Description

Show Remaining Actions After Completion functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-remaining-actions-respects-completion"></a>
### Scenario: [Remaining actions respects completion](#scenario-remaining-actions-respects-completion) (happy_path)

**Steps:**
```gherkin
GIVEN: bot.behaviors.current is at clarify action
WHEN: actions.close_current() is called
THEN: 'clarify' not in actions.remaining_actions
AND: actions.remaining_actions == ['validate', 'render']
```


# 📄 Navigate To First Behavior Action

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** System
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Navigate Behaviors](..) / [⚙️ Navigate Behaviors Using CLI Commands](.)  
**Sequential Order:** 0.0
**Story Type:** system

## Story Description

Navigate To First Behavior Action functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-navigate-sets-current-behavior-and-first-action"></a>
### Scenario: [Navigate sets current behavior and first action](#scenario-navigate-sets-current-behavior-and-first-action) ()

**Steps:**
```gherkin
GIVEN: Bot has behaviors configured
WHEN: bot.behaviors.navigate_to('shape') is called
THEN: bot.behaviors.current.name == 'shape'
AND: bot.behaviors.current.actions.current_action_name == 'clarify'
```


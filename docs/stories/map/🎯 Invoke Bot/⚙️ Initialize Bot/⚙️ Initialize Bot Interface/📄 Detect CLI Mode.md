# 📄 Detect CLI Mode

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/initialize_bot/test_initialize_bot_interface.py#L22)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Initialize Bot](..) / [⚙️ Initialize Bot Interface](.)  
**Sequential Order:** 0.0
**Story Type:** user

## Story Description

Detect CLI Mode functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-cli-detects-tty-mode"></a>
### Scenario: [CLI detects TTY mode](#scenario-cli-detects-tty-mode) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_initialize_bot_interface.py#L29)

**Steps:**
```gherkin
GIVEN: stdin/stdout are TTY
WHEN: CLISession created without explicit mode
THEN: Session uses TTY mode
```


<a id="scenario-cli-detects-pipe-mode"></a>
### Scenario: [CLI detects pipe mode](#scenario-cli-detects-pipe-mode) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_initialize_bot_interface.py#L44)

**Steps:**
```gherkin
GIVEN: stdin/stdout are piped (not TTY)
WHEN: CLISession created without explicit mode
THEN: Session uses markdown mode
```


<a id="scenario-cli-accepts-json-mode-flag"></a>
### Scenario: [CLI accepts JSON mode flag](#scenario-cli-accepts-json-mode-flag) (happy_path)  | [Test](/test/invoke_bot/initialize_bot/test_initialize_bot_interface.py#L59)

**Steps:**
```gherkin
GIVEN: JSON mode explicitly requested
WHEN: CLISession created with mode='json'
THEN: Session uses JSON mode
```


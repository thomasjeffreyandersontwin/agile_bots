# 📄 Display Piped Mode Instructions for AI Agents

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** CLI
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through REPL](..) / [⚙️ Initialize CLI Session](.)  
**Sequential Order:** 3
**Story Type:** system

## Story Description

Display Piped Mode Instructions for AI Agents functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-cli-displays-piped-mode-instructions-in-pipe-mode"></a>
### Scenario: [CLI displays piped mode instructions in pipe mode](#scenario-cli-displays-piped-mode-instructions-in-pipe-mode) (happy_path)

**Steps:**
```gherkin
GIVEN: REPLSession detects piped input
WHEN: CLI initializes
THEN: CLI displays piped mode instructions header
```


<a id="scenario-cli-omits-piped-mode-instructions-in-interactive-mode"></a>
### Scenario: [CLI omits piped mode instructions in interactive mode](#scenario-cli-omits-piped-mode-instructions-in-interactive-mode) (happy_path)

**Steps:**
```gherkin
GIVEN: REPLSession detects interactive TTY
WHEN: CLI initializes
THEN: CLI does not display piped mode instructions
```


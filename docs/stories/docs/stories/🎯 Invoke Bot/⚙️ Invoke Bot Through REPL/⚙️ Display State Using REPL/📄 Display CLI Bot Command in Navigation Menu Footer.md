# 📄 Display CLI Bot Command in Navigation Menu Footer

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** CLI
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through REPL](..) / [⚙️ Display State Using REPL](.)  
**Sequential Order:** 8
**Story Type:** system

## Story Description

Display CLI Bot Command in Navigation Menu Footer functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** CLI displays footer
  **then** CLI shows available navigation commands

- **When** displaying footer
  **then** CLI shows command syntax for navigation and actions

- **When** displaying footer
  **then** CLI includes examples of dot notation commands

- **When** displaying commands
  **then** CLI shows behavior.action.operation format examples

## Scenarios

<a id="scenario-cli-displays-bot-command-in-footer"></a>
### Scenario: [CLI displays bot command in footer](#scenario-cli-displays-bot-command-in-footer) (happy_path)

**Steps:**
```gherkin
Given: CLI displays footer
When: CLI renders footer
Then: CLI shows available navigation commands
```


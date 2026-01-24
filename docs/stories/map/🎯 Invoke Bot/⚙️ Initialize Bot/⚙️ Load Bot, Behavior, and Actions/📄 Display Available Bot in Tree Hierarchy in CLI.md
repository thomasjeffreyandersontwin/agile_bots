# 📄 Display Available Bot in Tree Hierarchy in CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** CLI
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Initialize Bot](..) / [⚙️ Load Bot, Behavior, and Actions](.)  
**Sequential Order:** 5.0
**Story Type:** system

## Story Description

Display Available Bot in Tree Hierarchy in CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** CLI displays status
  **then** CLI shows current bot name in header

- **When** displaying bot hierarchy
  **then** CLI shows bot name
  **and** available behaviors

- **When** displaying hierarchy
  **then** CLI shows behaviors with actions in tree structure

- **When** displaying hierarchy
  **then** CLI uses indentation to show structure

## Scenarios

<a id="scenario-cli-displays-bot-name-in-header"></a>
### Scenario: [CLI displays bot name in header](#scenario-cli-displays-bot-name-in-header) ()

**Steps:**
```gherkin
Given: CLI displays status
When: CLI renders bot hierarchy
Then: CLI shows current bot name in header
```


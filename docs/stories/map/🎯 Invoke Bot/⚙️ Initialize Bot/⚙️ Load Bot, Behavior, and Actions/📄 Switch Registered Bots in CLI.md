# 📄 Switch Registered Bots in CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** CLI
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Initialize Bot](..) / [⚙️ Load Bot, Behavior, and Actions](.)  
**Sequential Order:** 3.0
**Story Type:** system

## Story Description

Switch Registered Bots in CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** CLI STATUS section is displayed
  **then** CLI shows current bot name followed by pipe-separated list of all registered bots
  **and** format is: Bot: <current_bot> | Registered: <bot1> | <bot2> | <bot3>

- **When** CLI STATUS section is displayed
  **then** CLI shows bot switching instructions
  **and** format is: To change bots: bot <name>

- **When** user enters bot <name> command AND bot name is registered
  **then** CLI switches to the specified bot
  **and** updates CLI STATUS section to show new current bot

- **When** user enters bot <name> command AND bot name is not registered
  **then** CLI displays error message
  **and** shows list of available registered bots
  **and** keeps current bot active

- **When** bot is switched
  **then** CLI loads bot configuration from bot_config.json
  **and** makes bot behaviors and actions available

## Scenarios

<a id="scenario-display-registered-bots-in-cli-status"></a>
### Scenario: [Display Registered Bots in CLI STATUS](#scenario-display-registered-bots-in-cli-status) (happy_path)

**Steps:**
```gherkin

```


<a id="scenario-switch-to-valid-registered-bot"></a>
### Scenario: [Switch to Valid Registered Bot](#scenario-switch-to-valid-registered-bot) (happy_path)

**Steps:**
```gherkin

```


<a id="scenario-attempt-to-switch-to-unregistered-bot"></a>
### Scenario: [Attempt to Switch to Unregistered Bot](#scenario-attempt-to-switch-to-unregistered-bot) (error_path)

**Steps:**
```gherkin

```


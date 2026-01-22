# 📄 Enforce Mutually Exclusive Scope Types

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** CLI
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Invoke Bot Through REPL](..) / [⚙️ Manage Story Graph Using REPL](../..) / [⚙️ Manage Story Scope Using REPL](..) / [⚙️ Filter on Story Scope in CLI](.)  
**Sequential Order:** 3
**Story Type:** system

## Story Description

Enforce Mutually Exclusive Scope Types functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** user sets file scope while story scope is active
  **then** CLI replaces story scope with file scope

- **When** user sets story scope while file scope is active
  **then** CLI replaces file scope with story scope

- **When** checking stored scope
  **then** only one filter type is active

- **When** user clears scope
  **then** CLI removes all scope filters

## Scenarios

<a id="scenario-setting-file-scope-replaces-existing-story-scope"></a>
### Scenario: [Setting file scope replaces existing story scope](#scenario-setting-file-scope-replaces-existing-story-scope) (happy_path)

**Steps:**
```gherkin
GIVEN: CLI has story scope set
WHEN: user enters file scope
THEN: file scope replaces story scope (not combined)
```


<a id="scenario-setting-story-scope-replaces-existing-file-scope"></a>
### Scenario: [Setting story scope replaces existing file scope](#scenario-setting-story-scope-replaces-existing-file-scope) (happy_path)

**Steps:**
```gherkin
GIVEN: CLI has file scope set
WHEN: user enters story scope
THEN: story scope replaces file scope (not combined)
```


<a id="scenario-scope-object-can-only-have-one-type-at-a-time"></a>
### Scenario: [Scope object can only have one type at a time](#scenario-scope-object-can-only-have-one-type-at-a-time) (happy_path)

**Steps:**
```gherkin
GIVEN: Any scope is set
WHEN: checking the stored scope
THEN: only one filter type is active (knowledge_graph_filter OR file_filter, never both)
```


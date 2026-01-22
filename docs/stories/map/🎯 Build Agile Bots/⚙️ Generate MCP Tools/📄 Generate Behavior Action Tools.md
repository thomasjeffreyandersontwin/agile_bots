# 📄 Generate Behavior Action Tools

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** MCP Server Generator
**Path:** [🎯 Build Agile Bots](../..) / [⚙️ Generate MCP Tools](.)  
**Sequential Order:** 3.0
**Story Type:** user

## Story Description

Generate Behavior Action Tools functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Generator processes Bot Config

  **then** Generator creates tool code for each (behavior, action) pair

  **and** Enumerates all behaviors and actions from Bot Config

  **and** For each pair, generates tool code with unique name, trigger words, forwarding logic

  **and** Tool catalog prepared with all generated tool instances

## Scenarios

<a id="scenario-tools-generated-for-each-behavior-action"></a>
### Scenario: [Tools generated for each behavior action](#scenario-tools-generated-for-each-behavior-action) ()

**Steps:**
```gherkin
GIVEN: Bot with behaviors and actions
WHEN: Tool generation is triggered
THEN: MCP tools are created for each action
```


# 📄 Get Build Instructions Through CLI

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** User
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Build Story Graph](.)  
**Sequential Order:** 4.0
**Story Type:** user

## Story Description

Get Build Instructions Through CLI functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-get-build-instructions-without-scope"></a>
### Scenario: [Get build instructions without scope](#scenario-get-build-instructions-without-scope) ()

**Steps:**
```gherkin
GIVEN: CLI is at shape.build.instructions
WHEN: user enters 'shape.build.instructions'
THEN: CLI displays build instructions with full knowledge graph
```


<a id="scenario-get-build-instructions-with-scope"></a>
### Scenario: [Get build instructions with scope](#scenario-get-build-instructions-with-scope) ()

**Steps:**
```gherkin
GIVEN: CLI is at shape.build.instructions
WHEN: user enters 'shape.build.instructions scope="Story1"'
THEN: CLI displays build instructions filtered to Story1
```


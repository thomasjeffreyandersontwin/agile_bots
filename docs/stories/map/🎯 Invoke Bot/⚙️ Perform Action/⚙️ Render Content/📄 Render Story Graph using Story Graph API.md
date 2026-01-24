# 📄 Render Story Graph using Story Graph API

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Render Content](.)  
**Sequential Order:** 4.0
**Story Type:** user

## Story Description

Render Story Graph using Story Graph API functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** a StoryAdapter renders an StoryOutput
  **then** the StoryAdapter retrieves the StoryMap from the Bot
  **and** the StoryAdapter parses each node in StoryMap
  **and** creates a matching StoryRenderedNode for each StoryNode in the StoryMap
  **and** the StoryRenderedNode renders itself on the Diagram using the StoryAdapter
  **and** the StoryRenderedNode iterates over it's node children to render themselves in turn
  **and** every node in the StoryMap is represented in the Diagram
  **and** the StoryRenderedNodes are saved as a StoryOutput file
  **and** the StoryAdapter persists all positional data in a json file matching the rendered diagram

  **and** the original StoryMap's parent/child relationship and all original data will be accessed exactly like the original

  **then** the StoryRenderedNode will render itself again and update the StoryOutput as required

## Scenarios

### Scenario: Render Story Graph using Story Graph API (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```

# 📄 Build Story Graph Using API

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio)

**User:** Bot Behavior
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Perform Action](..) / [⚙️ Build Story Graph](.)  
**Sequential Order:** 3.0
**Story Type:** user

## Story Description

Build Story Graph Using API functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** Bot is called through StoryMap API
  **then** caller uses create_epic(), create_child(), create_story() for fine-grained construction
  **and** caller validates each node during creation
  **and** validation errors caught immediately before invalid structure created

- **When** Bot is called with large story graph structures
  **then** caller uses create_epic_from_dict() for batch operations
  **and** caller passes dictionary notation with epic/sub-epic/story hierarchy
  **and** StoryMap converts dict notation to domain objects
  **and** StoryMap validates entire structure before committing

- **When** StoryMap uses save() method
  **then** StoryMap persists story_graph dict to JSON file
  **and** file format matches existing story-graph.json structure
  **and** all nodes converted to dict representation before saving

- **When** StoryMap uses load() method
  **then** StoryMap reads JSON file
  **and** StoryMap rebuilds domain model from JSON
  **and** StoryMap reconstructs all Epic, SubEpic, Story objects with relationships

- **When** fine-grained and batch APIs implement same interface
  **then** both validate hierarchy rules (no mixing sub-epics and stories)
  **and** both handle positioning and resequencing
  **and** both update story_graph dict representation
  **and** interface enables incremental construction or bulk creation

## Scenarios

### Scenario: Build Story Graph Using API (happy_path)

**Steps:**
```gherkin
Given system is ready
When action executes
Then action completes successfully
```

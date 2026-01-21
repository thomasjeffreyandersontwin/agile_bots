# Perform Action - Increment Exploration

**Navigation:** [📋 Story Map](../map/) | [📊 Increments](../increments/)

**File Name**: `perform-action-exploration.md`
**Location**: `C:\dev\agile_bots\docs\stories\perform-action-exploration.md`

**Priority:** 5
**Relative Size:** Medium-Large

## Increment Purpose

Bot Behavior performs actions to execute workflow steps and coordinate bot behaviors so that AI agents and developers can invoke specific bot actions through CLI, API, and panel interfaces.

---

## Domain AC (Increment Level)

### Core Domain Concepts

- **Action**: Executable workflow step that performs a specific bot behavior operation
- **Story Graph**: Domain model representing epic/feature/story hierarchy with validation and persistence
- **Guardrails**: Configuration data (questions, evidence, decisions, assumptions) that guide behavior execution
- **Render Configuration**: Template or synchronizer definition that generates output artifacts
- **Scanner**: Validation component that checks files or story graphs against rules

---

### Domain Behaviors

- **Action executes workflow step**: Loads instructions, injects context, performs operation, returns result
- **Story Graph manages hierarchy**: Creates epics/stories, validates structure, persists to JSON
- **Guardrails preserve context**: Loads existing data, merges new data, saves to JSON files
- **Render generates artifacts**: Executes synchronizers automatically, provides templates for AI handling
- **Scanner validates against rules**: Receives scoped data, applies rules, returns violations

---

### Domain Rules

- **Actions must inject behavior-specific context**: Each action loads its required guardrails, templates, or rules
- **Story Graph maintains hierarchy integrity**: No mixing sub-epics and stories at same level
- **Guardrails use merge semantics**: New data preserves existing fields, overwrites matching fields
- **Synchronizers execute before templates**: Automated outputs generated first, manual templates provided to AI
- **Scanners receive filtered scope**: Only relevant files or graph nodes passed to validation

---

## Stories (10 total)

### 📝 Build Story Graph

**Acceptance Criteria:**  
- **WHEN** Action injects story graph template  
  **THEN** Instructions contain template_path from existing templates  
- **WHEN** Action loads and merges instructions  
  **THEN** Instructions contain all BuildStoryGraphAction-specific fields  
- **WHEN** Action injects all template variables  
  **THEN** Instructions contain all required BuildStoryGraphAction fields with variables replaced  
- **WHEN** Prioritization behavior updates existing story-graph.json  
  **THEN** Instructions use production template that updates existing file  
  **AND** existing story-graph.json in workspace is referenced  

---

### 📝 Render Story Graph using Story Graph API

**Acceptance Criteria:**  
- **WHEN** StoryAdapter renders a StoryOutput  
  **THEN** StoryAdapter retrieves the StoryMap from the Bot  
  **AND** StoryAdapter parses each node in StoryMap  
  **AND** creates a matching StoryRenderedNode for each StoryNode in the StoryMap  
  **AND** StoryRenderedNode renders itself on the Diagram using the StoryAdapter  
  **USING** formatting and positional rules associated with its node type from the StoryAdapter  
  **AND** StoryRenderedNode iterates over its node children to render themselves in turn  
  **AND** every node in the StoryMap is represented in the Diagram  
  **AND** StoryRenderedNodes are saved as a StoryOutput file  
  **AND** StoryAdapter persists all positional data in a json file matching the rendered diagram  

- **WHEN** StoryIODiagram is finished rendering  
  **THEN** all StoryRenderedNode are accessible using the same StoryMap API as the original object model  
  **AND** original StoryMap's parent/child relationship and all original data accessed exactly like the original  
  **AND** additional data is also accessible, including formatting data, sizing and positional information  

- **WHEN** bot, cli or another API makes a change to a StoryRenderedNode on the StoryOutput  
  **THEN** StoryRenderedNode will render itself again and update the StoryOutput as required  

---

### 📝 Build Story Graph Using API

**Acceptance Criteria:**  
- **WHEN** Bot is called through StoryMap API  
  **THEN** caller uses create_epic(), create_child(), create_story() for fine-grained construction  
  **AND** caller validates each node during creation  
  **AND** validation errors caught immediately before invalid structure created  

- **WHEN** Bot is called with large story graph structures  
  **THEN** caller uses create_epic_from_dict() for batch operations  
  **AND** caller passes dictionary notation with epic/sub-epic/story hierarchy  
  **AND** StoryMap converts dict notation to domain objects  
  **AND** StoryMap validates entire structure before committing  

- **WHEN** StoryMap uses save() method  
  **THEN** StoryMap persists story_graph dict to JSON file  
  **AND** file format matches existing story-graph.json structure  
  **AND** all nodes converted to dict representation before saving  

- **WHEN** StoryMap uses load() method  
  **THEN** StoryMap reads JSON file  
  **AND** StoryMap rebuilds domain model from JSON  
  **AND** StoryMap reconstructs all Epic, SubEpic, Story objects with relationships  

- **WHEN** fine-grained and batch APIs implement same interface  
  **THEN** both validate hierarchy rules (no mixing sub-epics and stories)  
  **AND** both handle positioning and resequencing  
  **AND** both update story_graph dict representation  
  **AND** interface enables incremental construction or bulk creation  

---

### 📝 Build Story Graph With CLI

**Acceptance Criteria:**  
- **WHEN** AI builds story graph through CLI  
  **THEN** AI calls CLI commands instead of writing raw JSON  
  **AND** AI uses create_epic, create_sub_epic, create_story commands for fine-grained construction  
  **AND** each CLI command invokes corresponding StoryMap API method  
  **AND** validation errors returned immediately to AI  

- **WHEN** AI builds large story graph structures through CLI  
  **THEN** AI uses create_from_json command for batch operations  
  **AND** AI passes dictionary notation with epic/sub-epic/story hierarchy  
  **AND** CLI accepts both inline JSON notation and file paths  
  **AND** CLI invokes StoryMap.create_epic_from_dict() with provided data  

- **WHEN** CLI wraps StoryMap API  
  **THEN** CLI exposes create_epic, create_sub_epic, create_story commands  
  **AND** CLI exposes create_from_json for batch operations  
  **AND** CLI provides save command to persist changes  
  **AND** CLI can be called from AI or human users  

- **WHEN** AI completes building story graph  
  **THEN** AI calls save command through CLI  
  **AND** CLI invokes StoryMap.save() method  
  **AND** story_graph persisted to file  
  **AND** AI receives confirmation of successful save  

---

### 📝 Clarify Requirements

**Acceptance Criteria:**  
- **WHEN** Action injects guardrails  
  **THEN** Instructions contain questions and evidence from production guardrails files  

- **WHEN** do_execute is called with key_questions_answered and evidence_provided  
  **THEN** clarification.json file is created in docs/stories/ folder  
  **AND** file contains behavior section with key_questions and evidence  

- **WHEN** clarification.json already exists with data for another behavior  
  **THEN** new save preserves existing behavior data  
  **AND** adds new behavior section  

- **WHEN** do_execute is called with empty parameters  
  **THEN** clarification.json file is not created  

- **WHEN** Behavior loads guardrails  
  **THEN** Questions and evidence are loaded correctly from workspace files  
  **AND** Strategy assumptions are loaded correctly when present  

---

### 📝 Validate Rules

**Acceptance Criteria:**  
- **WHEN** Validate action executes  
  **THEN** Instructions contain rule descriptions, DO/DON'T sections, and priorities from rule files  

- **WHEN** Validate action executes with scope  
  **THEN** Story graph scanners receive filtered story graph (only scoped epic)  
  **AND** File scanners receive filtered files (only scoped files matching pattern)  
  **AND** Scanner executes successfully with scoped data  
  **AND** Instructions contain scope description  

---

### 📝 Display Rules

**Acceptance Criteria:**  
- **WHEN** Rules action executes  
  **THEN** Instructions contain formatted rules digest with descriptions, priorities, DO/DON'T sections  
  **AND** Display includes rule names with their file paths  
  **AND** All rules from behavior are included in digest  

- **WHEN** Rules action executes with message  
  **THEN** Instructions include user message  

- **WHEN** Rules action executes without message  
  **THEN** Instructions do not include user message section  

---

### 📝 Decide Strategy

**Acceptance Criteria:**  
- **WHEN** Action injects strategy criteria and assumptions  
  **THEN** Instructions contain all required strategy fields (decision criteria, assumptions)  

- **WHEN** do_execute is called with decisions_made and assumptions_made  
  **THEN** strategy.json file is created in docs/stories/ folder  
  **AND** file contains behavior section with decisions_made and assumptions_made  

- **WHEN** strategy.json already exists with data for another behavior  
  **THEN** new save preserves existing behavior data  
  **AND** adds new behavior section  

- **WHEN** do_execute is called with empty parameters  
  **THEN** strategy.json file is not created  

---

### 📝 Render Output

**Acceptance Criteria:**  
- **WHEN** Action injects render data  
  **THEN** Instructions contain all required render fields (configs, templates, synchronizers)  

- **WHEN** Render output action executes  
  **THEN** Synchronizers are executed automatically  
  **AND** Template configs remain in instructions for AI handling  
  **AND** Instructions include synchronizer execution info  

---

### 📝 Save Guardrails

**Acceptance Criteria:**  
- **WHEN** Action saves answers with question and value  
  **THEN** System loads existing clarification.json for behavior  
  **AND** System merges new answer with existing answers  
  **AND** System saves updated clarification.json to workspace docs folder  
  **AND** File contains behavior section with saved answer  

- **WHEN** Action saves evidence with evidence type and file path  
  **THEN** System loads existing clarification.json for behavior  
  **AND** System merges new evidence with existing evidence  
  **AND** System saves updated clarification.json to workspace docs folder  
  **AND** File contains behavior section with saved evidence  

- **WHEN** Action saves decisions with decision key and value  
  **THEN** System loads existing strategy.json for behavior  
  **AND** System merges new decision with existing decisions  
  **AND** System saves updated strategy.json to workspace docs folder  
  **AND** File contains behavior section with saved decision  

- **WHEN** Action saves assumptions with assumption text  
  **THEN** System loads existing strategy.json for behavior  
  **AND** System merges new assumption with existing assumptions  
  **AND** System saves updated strategy.json to workspace docs folder  
  **AND** File contains behavior section with saved assumption  

- **WHEN** Merge occurs with existing data  
  **THEN** System preserves existing fields that are not updated  
  **AND** System overwrites fields that have new values  
  **AND** JSON file contains all fields with updated values  

---

## Consolidation Decisions

**Same logic, different data → Consolidate:**
- Save Guardrails story consolidates saving answers, evidence, decisions, and assumptions - same merge logic, different data types

**Different formulas → Keep separate:**
- Build Story Graph vs Build Story Graph Using API vs Build Story Graph With CLI - different construction mechanisms (template injection vs API calls vs CLI commands)
- Clarify Requirements vs Decide Strategy - different guardrail types with different field structures
- Validate Rules vs Display Rules - different purposes (validation with scanners vs display only)

**Different validation rules → Keep separate:**
- Story Graph scanners receive story_graph data structure
- File scanners receive file paths list
- Each has different input requirements and validation logic

---

## Domain Rules Referenced

1. **Action Instruction Injection**: Each action type has specific fields it must inject (templates, guardrails, rules, render configs)
2. **Guardrails Merge Semantics**: New data preserves existing fields, overwrites matching fields within same behavior section
3. **Behavior Context Isolation**: Each behavior maintains its own section in clarification.json and strategy.json
4. **Story Graph Hierarchy Integrity**: API and CLI both enforce no mixing sub-epics and stories at same level
5. **Scope Filtering**: Validation actions pass filtered data to scanners (story graph nodes or file paths matching scope)
6. **Synchronizer Priority**: Render action executes synchronizers first, then provides templates to AI
7. **Template Variable Replacement**: Build Story Graph action replaces all template variables before injecting instructions

---

## Source Material

- Story Graph JSON: `C:\dev\agile_bots\docs\stories\story-graph.json`
- Clarification Data: `C:\dev\agile_bots\docs\stories\clarification.json`
- Strategy Data: `C:\dev\agile_bots\docs\stories\strategy.json`
- Existing Story Map: `C:\dev\agile_bots\docs\stories\acceptance criteria\perform-action-story-map.txt`
- Test Files: Test scenarios extracted from story graph

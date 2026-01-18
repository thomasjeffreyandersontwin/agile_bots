# {increment_name} - Increment Exploration

**Navigation:** [📋 Story Map](../map/{story_map_filename}) | [📊 Increments](../increments/{increments_filename})

**File Name**: `{increment_name_slug}-exploration.md`
**Location**: `{solution_folder}/docs/stories/{increment_name_slug}-exploration.md`

**Priority:** {increment_priority}
**Relative Size:** {increment_relative_size}

## Increment Purpose

<Actor> <verb> <noun> <outcome_description>

**Example:**
Delivers complete end-to-end flow for initializing a project and starting the first behavior so that users can begin story shaping workflows

---

## Domain AC (Increment Level)

### Core Domain Concepts

- <Concept>: <description>  
- <Concept>: <description>  
- <Concept>: <description>  

**Example:**  
- Agile Bot: Manages workflow execution and coordinates behaviors  
- Project: Provides project context and manages project state  
- Workflow: Manages behavior state transitions and action sequencing  

---

### Domain Behaviors

- <Concept> <verb> <noun>: <description>  
- <Concept> <verb> <noun>: <description>  
- <Concept> <verb> <noun>: <description>  

**Example:**  
- Agile Bot manages workflow execution: Coordinates behaviors and state transitions  
- Project provides project context: Supplies project path and agent configuration  
- Workflow manages behavior state: Tracks current behavior and available actions  

---

### Domain Rules

- <Rule description>: <constraint or requirement>  
- <Rule description>: <constraint or requirement>  
- <Rule description>: <constraint or requirement>  

**Example:**  
- Workflow State transitions are sequential: Must complete current action before moving to next  
- Agent configuration must exist: Project cannot initialize without valid agent.json  
- Behaviors must provide required context: Clarification questions must be answered before proceeding  

---

## Stories ({story_count} total)

### 📝 <Story Name>

**Acceptance Criteria:**  
- **WHEN** <action>  
  **THEN** <outcome>  
  **AND** <additional outcome>  
- **WHEN** <action>  
  **THEN** <outcome>  
  **BUT** <negative condition - what NOT to do>  

**Example:**  
### 📝 User provides project path in chat window

**Acceptance Criteria:**  
- **WHEN** user types project path  
  **THEN** AI Chat receives project path  
  **AND** validates path exists  
- **WHEN** Project initializes with invalid path  
  **THEN** Project shows error message  
  **BUT** does not initialize project  

{stories_with_ac}

---

## Consolidation Decisions

{consolidation_decisions}

---

## Domain Rules Referenced

{domain_rules_referenced}

---

## Source Material

{source_material}


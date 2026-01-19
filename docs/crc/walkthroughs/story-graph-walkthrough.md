# Domain Walkthrough Realizations: Agile Bots Story Graph Editor

**Date**: 2026-01-18  
**Status**: Active - Initial Realizations Complete  
**Domain Model Version**: 1.0

## Purpose

This document validates the domain model by tracing object flows through key scenarios for the Story Graph editing features. Each walkthrough proves the model can fulfill story requirements by showing explicit method calls, parameters, nested collaborations, and return values.

**Coverage Tracking**: Each walkthrough explicitly maps to story graph nodes (Epic → Sub-Epic → Story → AC → Scenario → Steps). This "Covers" information is also stored in story-graph.json domain concepts as realization scenarios.

---

## Walkthrough Strategy

**Purpose**: Validate hierarchy management, node creation/deletion, and type compatibility enforcement in Story Graph  
**Depth**: Mixed - detailed for hierarchy rules (risky), high-level for standard CRUD  
**Focus Areas**: Node creation with position management, cascade deletion, SubEpic type mixing validation, Story collection routing  
**Stopping Criteria**: Stop when hierarchy management patterns proven and no new collaborations discovered

**Scenarios Selected**:
1. Create Child Story Node - Create child node with specified position
2. Delete Story Node - Delete node including children (cascade delete)
3. Create Child Story Node - SubEpic with SubEpics cannot create Story child
4. Create Child Story Node - Story creates child and adds to correct collection

**Rationale**:
These scenarios focus on the complex weak conditions mentioned by the user:
- **Position management**: How nodes maintain sequential order when inserting at specific positions
- **Hierarchy rules**: How SubEpic enforces "cannot mix SubEpics and Stories" constraint
- **Cascade deletion**: How recursive deletion works and siblings resequence
- **Collection routing**: How Story maintains separate scenario and acceptance criteria collections

---

## Realization Scenarios

### Scenario 1: Create Child Node with Specified Position

**Purpose**: Validate StoryNode can insert child at specific position, shift existing children, and maintain sequential order  
**Concepts Traced**: StoryNode, StoryNodeChildren, NodeValidator

**Scope**: Invoke Bot.Invoke Bot Directly.Manage Story Graph.Edit Story Graph.Create Child Story Node.Create child node with specified position

#### Walk Throughs

**Walk 1 - Covers**: Steps 1-2 (Initialize parent, validate position)

```
StoryNode
    parent_node: Epic = StoryGraph.get_epic(name: 'User Management')
    existing_children: ['SubEpic A', 'SubEpic B'] = parent_node.get_children()
    target_position: 1 = request.position
    is_valid: True = parent_node.validate_position(position: 1, child_count: 2)
        -> max_position: 2 = StoryNodeChildren.get_max_position(children: ['SubEpic A', 'SubEpic B'])
        -> is_in_range: True = (position: 1 <= max_position: 2)
           return is_in_range: True
    return is_valid: True
```

**Walk 2 - Covers**: Step 3 (Create child and insert at position)

```
StoryNode
    new_child: SubEpic = parent_node.create_child(name: 'SubEpic C', position: 1)
        -> is_duplicate: False = parent_node.validate_child_name_unique(name: 'SubEpic C')
           -> existing_names: ['SubEpic A', 'SubEpic B'] = StoryNodeChildren.get_child_names()
           -> is_unique: True = ('SubEpic C' not in existing_names)
              return is_unique: True
           return is_duplicate: False
        -> child: SubEpic = SubEpic.create(name: 'SubEpic C', parent: Epic)
        -> parent_node.resequence_children(insert_at: 1, new_child: child)
           -> children_to_shift: ['SubEpic B'] = StoryNodeChildren.get_children_from_position(position: 1)
           -> StoryNodeChildren.shift_positions(children: ['SubEpic B'], offset: 1)
              SubEpic B.position = 1 + 1 = 2
           -> StoryNodeChildren.insert(child: SubEpic C, position: 1)
              SubEpic C.position = 1
        -> final_order: ['SubEpic A', 'SubEpic C', 'SubEpic B'] = parent_node.get_children()
           return final_order
    return new_child: SubEpic
```

**Validation Result**: ✅ Model supports this scenario  
**Gaps Found**: None  
**Recommendations**: None

---

### Scenario 2: Delete Node Including Children (Cascade Delete)

**Purpose**: Validate StoryNode can recursively delete all descendants and resequence remaining siblings  
**Concepts Traced**: StoryNode, StoryNodeChildren, Parent

**Scope**: Invoke Bot.Invoke Bot Directly.Manage Story Graph.Edit Story Graph.Delete Story Node.Delete node including children (cascade delete)

#### Walk Throughs

**Walk 1 - Covers**: Steps 1-3 (Locate node, count descendants, initiate cascade delete)

```
StoryNode
    parent_node: Epic = StoryGraph.get_epic(name: 'User Management')
    target_node: SubEpic = parent_node.get_child(name: 'SubEpic B')
    child_count: 2 = target_node.count_children()
        -> direct_children: ['Story A', 'Story B'] = StoryNodeChildren.get_children()
           return len(direct_children): 2
    total_descendants: 5 = target_node.count_all_descendants()
        -> count: 2 = child_count
        -> for each child in direct_children:
           -> child_descendants: 3 = child.count_all_descendants()
              count = count + 1 + child_descendants = 2 + 1 + 2 = 5
           return count: 5
    cascade_flag: True = request.cascade
    return {node: target_node, descendants: 5, cascade: True}
```

**Walk 2 - Covers**: Steps 4-5 (Recursively delete descendants, remove from parent)

```
StoryNode
    target_node.delete(cascade: True)
        -> target_node.delete_all_descendants()
           -> children: ['Story A', 'Story B'] = target_node.get_children()
           -> for each child in children:
              -> child.delete(cascade: True)
                 -> nested_children = child.get_children()
                 -> for each nested in nested_children:
                    -> nested.delete(cascade: True)
                       # Recursively deletes scenarios under stories
                 -> child.remove_from_parent()
              # Stories A and B and their scenarios deleted
        -> target_node.remove_from_parent()
           -> parent: Epic = target_node.parent
           -> position: 1 = target_node.position
           -> parent.remove_child(child: target_node)
              -> StoryNodeChildren.remove(child: target_node)
              -> parent.resequence_children(deleted_position: 1)
                 -> siblings_after: ['SubEpic C', 'SubEpic D'] = StoryNodeChildren.get_children_from_position(position: 2)
                 -> StoryNodeChildren.shift_positions(children: siblings_after, offset: -1)
                    SubEpic C.position = 2 - 1 = 1
                    SubEpic D.position = 3 - 1 = 2
                 -> final_children: ['SubEpic A', 'SubEpic C', 'SubEpic D'] = parent.get_children()
                    return final_children
    return deleted: True
```

**Validation Result**: ✅ Model supports this scenario  
**Gaps Found**: None - recursive deletion pattern proven  
**Recommendations**: None

---

### Scenario 3: SubEpic with SubEpics Cannot Create Story Child

**Purpose**: Validate SubEpic enforces hierarchy rule preventing mixing of SubEpic and Story children  
**Concepts Traced**: SubEpic, StoryNodeChildren

**Scope**: Invoke Bot.Invoke Bot Directly.Manage Story Graph.Edit Story Graph.Create Child Story Node.SubEpic with SubEpics cannot create Story child

#### Walk Throughs

**Walk 1 - Covers**: Steps 1-4 (Attempt Story creation, validate hierarchy, reject with error)

```
SubEpic
    subepic_node: SubEpic = StoryGraph.get_subepic(name: 'User Management')
    existing_subepic: SubEpic = subepic_node.get_child(name: 'Authentication')
    requested_child_type: 'Story' = request.child_type
    can_add: False = subepic_node.check_child_type_compatibility(child_type: 'Story')
        -> has_subepics: True = subepic_node.has_children_of_type(type: 'SubEpic')
           -> children: [Authentication] = StoryNodeChildren.get_children()
           -> subepic_count: 1 = len([c for c in children if c.type == 'SubEpic'])
           -> has_subepics: True = (subepic_count: 1 > 0)
              return has_subepics: True
        -> is_compatible: False = SubEpic.validate_cannot_mix_subepics_and_stories(has_subepics: True, adding_type: 'Story')
           -> if has_subepics: True and adding_type: 'Story':
              return is_compatible: False
        return can_add: False
    error: ValidationError = SubEpic.create_hierarchy_error(message: 'Cannot create Story under SubEpic with SubEpics')
    return error: ValidationError
```

**Validation Result**: ✅ Model supports this scenario  
**Gaps Found**: None - hierarchy validation proven  
**Recommendations**: Consider adding similar validation for preventing SubEpic creation when Stories exist

---

### Scenario 4: Story Creates Child and Adds to Correct Collection

**Purpose**: Validate Story routes Scenario and AcceptanceCriteria to separate collections with independent ordering  
**Concepts Traced**: Story, ScenarioCollection, AcceptanceCriteriaCollection, StoryNodeChildren

**Scope**: Invoke Bot.Invoke Bot Directly.Manage Story Graph.Edit Story Graph.Create Child Story Node.Story creates child and adds to correct collection

#### Walk Throughs

**Walk 1 - Covers**: Steps 1-3 (Create Scenario child, route to scenarios collection)

```
Story
    story_node: Story = StoryGraph.get_story(name: 'Validate Password')
    child_type: 'Scenario' = request.child_type
    child_name: 'Valid Password Entered' = request.child_name
    new_scenario: Scenario = story_node.create_child(name: child_name, type: child_type)
        -> target_collection: 'scenarios' = story_node.route_child_to_correct_collection(child_type: 'Scenario')
           -> if child_type in ['Scenario', 'ScenarioOutline']:
              return collection: 'scenarios'
           -> elif child_type == 'AcceptanceCriteria':
              return collection: 'acceptance_criteria'
        -> scenario: Scenario = Scenario.create(name: 'Valid Password Entered', parent: story_node)
        -> position: 0 = ScenarioCollection.get_next_position()
        -> ScenarioCollection.add(child: scenario, position: 0)
           scenario.position = 0
        -> scenarios: ['Valid Password Entered'] = ScenarioCollection.get_all()
        -> acceptance_criteria: [] = AcceptanceCriteriaCollection.get_all()
           # Verify scenario NOT added to acceptance_criteria collection
           return {scenarios: scenarios, acceptance_criteria: acceptance_criteria}
    return new_scenario: Scenario
```

**Walk 2 - Covers**: Steps 4-6 (Create AcceptanceCriteria child, route to separate collection with independent ordering)

```
Story
    ac_child_type: 'AcceptanceCriteria' = request.child_type
    ac_name: 'Password Must Not Be Empty' = request.child_name
    new_ac: AcceptanceCriteria = story_node.create_child(name: ac_name, type: ac_child_type)
        -> target_collection: 'acceptance_criteria' = story_node.route_child_to_correct_collection(child_type: 'AcceptanceCriteria')
           return collection: 'acceptance_criteria'
        -> ac: AcceptanceCriteria = AcceptanceCriteria.create(name: 'Password Must Not Be Empty', parent: story_node)
        -> ac_position: 0 = AcceptanceCriteriaCollection.get_next_position()
           # Independent ordering from scenarios - both start at 0
        -> AcceptanceCriteriaCollection.add(child: ac, position: 0)
           ac.position = 0
        -> scenarios: ['Valid Password Entered'] = ScenarioCollection.get_all()
           # Verify AC NOT added to scenarios collection
        -> acceptance_criteria: ['Password Must Not Be Empty'] = AcceptanceCriteriaCollection.get_all()
           return {scenarios: scenarios, acceptance_criteria: acceptance_criteria}
    return new_ac: AcceptanceCriteria
```

**Validation Result**: ✅ Model supports this scenario  
**Gaps Found**: None - collection routing and independent ordering proven  
**Recommendations**: None

---

## Model Updates Discovered

### New Responsibilities Added

**StoryNode (Base)**
- Added: "Create child node with name and position: StoryNodeChildren, NodeValidator"
- Added: "Delete self and handle children: Parent, StoryNodeChildren"
- Added: "Validate child name unique among siblings: StoryNodeChildren"
- Added: "Adjust position to valid range: StoryNodeChildren"
- Added: "Resequence children after insert or delete: StoryNodeChildren"
- Rationale: Walkthroughs revealed these core node manipulation responsibilities were missing

**SubEpic**
- Added: "Create StoryGroup when first Story added: StoryGroup"
- Added: "Check child type compatibility before add: StoryNodeChildren"
- Rationale: Hierarchy validation requires checking compatibility before attempting creation

**Story**
- Added: "Route child to correct collection by type: ScenarioCollection, AcceptanceCriteriaCollection"
- Rationale: Story must route different child types to appropriate collections

### New Concepts Discovered

None - all concepts already existed in domain model

### Responsibilities Removed

None

### Responsibilities Modified

**StoryNode (Base)** - Clarified: "Resequence children after insert or delete" handles both insert AND delete cases
- Rationale: Walkthrough showed same responsibility used for both operations with different offsets

**SubEpic** - Clarified: "Validate cannot mix Sub-Epics and Stories" is invoked during create_child operations
- Rationale: Walkthrough showed this validation is part of child creation flow

**Story** - Clarified: "Maintain separate sequential ordering for scenarios and acceptance criteria" means independent position counters per collection
- Rationale: Walkthrough proved both collections can have position 0 simultaneously

---

## Model Validation Summary

**Total Scenarios Traced**: 4  
**Scenarios Validated**: 4 ✅  
**Scenarios with Gaps**: 0 ⚠️  
**New Concepts Discovered**: 0  
**Responsibilities Added**: 8  
**Responsibilities Modified**: 3 (clarifications)

**Model Confidence**: High - all hierarchy management scenarios validated

---

## Recommended Next Steps

1. **Walkthrough node movement scenarios** - Validate "Move Story Node To Parent" to prove parent transfer logic
2. **Walkthrough position adjustment edge cases** - Validate invalid position handling (position > child_count)
3. **Walkthrough duplicate name handling** - Validate error cases when duplicate names attempted
4. **Consider adding integration tests** - These walkthroughs reveal the complexity of hierarchy management; integration tests would catch regression issues

---

## Source Material

- **Story Graph**: `story-graph.json`
- **Domain Model**: From story-graph.json domain_concepts (Invoke Bot > Invoke Bot Directly > Manage Story Graph > Edit Story Graph)
- **Realization Scenarios**: Stored in story-graph.json domain_concepts with "Covers" mapping
- **Stories Traced**: Create Child Story Node, Delete Story Node
- **ACs/Scenarios Traced**: 4 scenarios across 2 stories
- **Story Graph Coverage**: 2 of 5 stories in Edit Story Graph sub-epic (40%)

---

## Walkthrough Notes

**Patterns Observed**:
- **Resequencing pattern**: Used consistently for both inserts (shift +1) and deletes (shift -1)
- **Position validation pattern**: Always check position <= max before attempting insertion
- **Duplicate name pattern**: Always validate name unique among siblings before creating child
- **Hierarchy validation pattern**: Check type compatibility before allowing child creation
- **Collection routing pattern**: Story uses type-based routing to direct children to correct collection

**Areas Needing More Detail**:
- **Parent transfer logic**: Move scenarios not yet walked through - how does node change parent while maintaining position?
- **StoryGroup creation**: First story creation auto-creates StoryGroup - when exactly does this happen?
- **Error propagation**: How do validation errors bubble up to user interface?
- **Transaction boundaries**: What happens if resequencing partially fails?

---

## Story Graph Integration

Each walkthrough realization is stored in `story-graph.json` under the relevant domain concept with the following format:

```json
{
  "name": "StoryNode (Base)",
  "realization": [
    {
      "scope": "Invoke Bot.Invoke Bot Directly.Manage Story Graph.Edit Story Graph.Create Child Story Node.Create child node with specified position",
      "scenario": "Parent node creates new child at specific position, shifting existing children and maintaining sequential order",
      "walks": [
        {
          "covers": "Steps 1-2 (Initialize parent, validate position)",
          "object_flow": ["parent_node: Epic = StoryGraph.get_epic(name: 'User Management')", "..."]
        },
        {
          "covers": "Step 3 (Create child and insert at position)",
          "object_flow": ["new_child: SubEpic = parent_node.create_child(name: 'SubEpic C', position: 1)", "..."]
        }
      ],
      "model_updates": ["Added 'Create child node with name and position' responsibility to StoryNode", "..."]
    }
  ]
}
```

**Coverage by Node Type**:
- Epic-level: Not traced (standard behavior)
- SubEpic-level: 2 walks (hierarchy validation, compatibility checking)
- Story-level: 2 walks (collection routing, independent ordering)
- Scenario-level: Implicitly traced through cascade deletion

This allows traceability from domain concepts to the stories they support, with granular coverage tracking per walk.

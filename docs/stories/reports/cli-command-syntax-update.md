# CLI Command Syntax Update - Parameter Notation

**Date:** 2026-01-19  
**Scope:** Story Graph CLI command syntax standardization  
**Files Updated:** 2

---

## Summary

Updated CLI command syntax across tests and story graph documentation to use proper parameter notation instead of continuing dot notation for action parameters.

### Command Syntax Pattern

**Old (Incorrect):**
```
story_graph."Epic Name".create_sub_epic."Child Name".at_position.1
story_graph."Epic Name"."Old Name".rename."New Name"
story_graph."Source Epic"."Node".move_to."Target Epic".at_position.2
```

**New (Correct):**
```
story_graph."Epic Name".create_sub_epic name:"Child Name" at_position:1
story_graph."Epic Name"."Old Name".rename name:"New Name"
story_graph."Source Epic"."Node".move_to target:"Target Epic" at_position:2
```

---

## Syntax Rules

### Pattern Components

1. **Navigation (dot notation):** `story_graph."Epic Name"."SubEpic Name"`
   - Navigate through the story graph hierarchy using quoted node names
   - Each level separated by dots

2. **Action:** `.action_name`
   - Action is part of the dot notation chain
   - Examples: `.create_sub_epic`, `.delete`, `.rename`, `.move_to`

3. **Parameters (key:value pairs):** `param1:"value1" param2:value2`
   - Space-separated key:value pairs
   - String values in quotes: `name:"Node Name"`
   - Numeric values without quotes: `at_position:1`

### Command Examples by Operation

**Create Child Node:**
```bash
# Create with auto-generated name at last position
story_graph."Invoke Bot".create_sub_epic

# Create with specific name at last position
story_graph."Invoke Bot".create_sub_epic name:"Manage Bot Information"

# Create with name at specific position
story_graph."Invoke Bot".create_sub_epic name:"Info" at_position:1

# Create different node types
story_graph."Authentication".create_story name:"Login Form"
story_graph."Login Form".create_scenario name:"Valid Login"
```

**Delete Node:**
```bash
# Delete without children (or with children moved to parent)
story_graph."Invoke Bot"."Manage Bot".delete

# Delete including all children (cascade)
story_graph."Invoke Bot"."Manage Bot".delete_including_children
```

**Rename Node:**
```bash
# Rename node
story_graph."Invoke Bot"."Old Name".rename name:"New Name"
```

**Move Node:**
```bash
# Move to different parent with position
story_graph."Invoke Bot"."Manage Bot".move_to target:"Other Epic" at_position:1

# Move to different parent at last position
story_graph."Invoke Bot"."Manage Bot".move_to target:"Other Epic"

# Reorder within same parent
story_graph."Invoke Bot"."Manage Bot".move_to_position position:3
```

**Execute Scoped Action:**
```bash
# Execute action on specific node
story_graph."User Management".build
story_graph."Create Scenarios".generate_scenarios
```

---

## Files Updated

### 1. Test File - `test/CLI/test_edit_story_graph_in_cli.py`

**Changes:** 18 command strings updated

| Operation | Old Syntax | New Syntax |
|-----------|------------|------------|
| Create | `.create_sub_epic."Name"` | `.create_sub_epic name:"Name"` |
| Create with position | `.create_sub_epic."Name".at_position.1` | `.create_sub_epic name:"Name" at_position:1` |
| Rename | `.rename."New Name"` | `.rename name:"New Name"` |
| Move to parent | `.move_to."Target".at_position.1` | `.move_to target:"Target" at_position:1` |
| Move within parent | `.move_to_position.3` | `.move_to_position position:3` |

**Test Methods Updated:**
- `test_create_child_with_dot_notation_default_position` (2 instances)
- `test_create_child_with_position_specified`
- `test_create_child_invalid_position_adjusts`
- `test_nonexistent_parent_outputs_error`
- `test_incompatible_child_type_outputs_error`
- `test_duplicate_name_outputs_error` (2 instances)
- `test_rename_node_with_valid_name`
- `test_rename_nonexistent_node_outputs_error`
- `test_rename_with_empty_name_outputs_error`
- `test_rename_with_duplicate_name_outputs_error`
- `test_rename_with_invalid_characters_outputs_error`
- `test_move_node_to_different_parent_with_position`
- `test_move_node_same_parent_different_position`
- `test_move_nonexistent_source_outputs_error`
- `test_move_to_nonexistent_target_outputs_error`
- `test_move_incompatible_type_outputs_error`
- `test_move_circular_reference_outputs_error`

### 2. Story Graph - `docs/stories/story-graph.json`

**Changes:** 20+ acceptance criteria and scenario steps updated

**Acceptance Criteria Examples Updated:**
```json
// Create Child Story Node - AC
"WHEN User creates new child with dot notation
EXAMPLE: cli.story_graph.\"Invoke Bot\".create_sub_epic name:\"Manage Bot Information\"
THEN CLI parses dot notation to parent..."

// Rename Node - AC
"WHEN User renames node with dot notation
EXAMPLE: cli.story_graph.\"Invoke Bot\".\"Old Name\".rename name:\"New Name\"
THEN CLI parses notation to node..."

// Move Node - AC
"WHEN User moves node with dot notation
EXAMPLE: cli.story_graph.\"Invoke Bot\".\"Manage Bot\".move_to target:\"Other Epic\" at_position:2
THEN CLI parses notation to source and target..."
```

**Scenario Steps Updated:**
- All `create_sub_epic` commands (6 scenarios)
- All `rename` commands (5 scenarios)
- All `move_to` and `move_to_position` commands (6 scenarios)

---

## Benefits of New Syntax

### 1. **Standard Parameter Pattern**
- Follows common CLI conventions (like `--flag value` or `key=value`)
- More intuitive for users familiar with command-line tools

### 2. **Clear Separation of Concerns**
- Navigation (dot notation) vs Parameters (key:value)
- Action is part of navigation, parameters configure the action

### 3. **Easier to Parse**
- Dot notation stops at action
- Everything after is space-separated parameters
- No ambiguity about what's a node name vs what's a parameter

### 4. **Better Extensibility**
- Easy to add new parameters without changing syntax
- Can support optional parameters naturally
- Can support boolean flags: `force:true`

### 5. **Consistent with Domain**
- Parameters map directly to method arguments
- `create_sub_epic name:"X" at_position:1` → `create_child(name="X", position=1)`

---

## Parser Implementation Notes

### Parsing Strategy

```python
def parse_story_graph_command(command: str):
    # 1. Split on first space to separate navigation from parameters
    parts = command.split(' ', 1)
    navigation = parts[0]  # "story_graph.\"Epic\".create_sub_epic"
    params_str = parts[1] if len(parts) > 1 else ""  # "name:\"Info\" at_position:1"
    
    # 2. Parse navigation using dot notation parser
    path_parts = parse_dot_notation(navigation)
    # ["story_graph", "Epic", "create_sub_epic"]
    
    # 3. Parse parameters as key:value pairs
    params = parse_parameters(params_str)
    # {"name": "Info", "at_position": 1}
    
    return {
        "path": path_parts[:-1],  # ["story_graph", "Epic"]
        "action": path_parts[-1],  # "create_sub_epic"
        "params": params
    }
```

### Parameter Parsing Rules

1. **String values** (quoted): `name:"Node Name"` → `{"name": "Node Name"}`
2. **Numeric values** (unquoted): `at_position:1` → `{"at_position": 1}`
3. **Boolean values** (unquoted): `force:true` → `{"force": True}`
4. **Multiple parameters** (space-separated): `name:"X" at_position:1`

---

## Verification

### Pre-Update Issues

✗ Ambiguous syntax mixing navigation and parameters  
✗ Hard to distinguish node names from parameter values  
✗ Non-standard CLI pattern  
✗ Difficult to extend with new parameters

### Post-Update Benefits

✅ Clear separation: navigation vs parameters  
✅ Standard key:value parameter pattern  
✅ Intuitive for CLI users  
✅ Easy to parse and extend  
✅ Maps directly to domain method signatures

---

## Next Steps

### Implementation Requirements

1. **CLI Command Parser** - Update to handle new parameter syntax
2. **Parameter Validation** - Validate parameter keys and value types
3. **Help Text** - Update command help to show new syntax
4. **Error Messages** - Show correct syntax in error messages

### Testing

- [x] Test files updated with correct syntax
- [ ] Verify parser handles new syntax
- [ ] Verify all commands execute correctly
- [ ] Verify error messages show correct syntax examples

### Documentation

- [x] Story graph acceptance criteria updated
- [x] Scenario steps updated
- [x] Test docstrings updated
- [ ] User documentation updated (if exists)
- [ ] CLI help text updated

---

## Conclusion

Successfully standardized CLI command syntax for story graph operations to use proper parameter notation. The new syntax is:
- More intuitive and standard
- Easier to parse and extend
- Clearly separates navigation from configuration
- Maps directly to domain method signatures

All tests and story graph documentation now reflect the correct syntax pattern.

# Walkthrough Realization: Create Epic at Root Level

**Scope:** Invoke Bot.Invoke Bot Through Panel.Manage Story Graph Through Panel.Edit Story Graph In Panel.Create Epic

**Scenario:** User creates Epic with auto-generated name in edit mode at root level

---

## Walk 1: User Clicks Create Epic Button at Root

**Covers:** Steps: Root selection → Create Epic button shown → CLI command → domain operation

### Object Flow

```
selection_event: {node_id: 'story-map-root'} = User.clicks(element_id: 'story-map-root')

# StoryMapView uses existing responsibility: "Shows context-appropriate action buttons"
# When root selected, shows "Create Epic" button

html: '<button id="create-epic">Create Epic</button>' = StoryMapView.show_context_appropriate_action_buttons(node: 'root')
  -> node_type: 'StoryMapRoot' = StoryMapView.get_selected_node_type()
     return node_type: 'StoryMapRoot'
  
  # Root node → show Create Epic button
  -> buttons: ['Create Epic'] = StoryMapView.determine_buttons_for_node(node_type: 'StoryMapRoot')
     return buttons: ['Create Epic']
  
  -> html: '<button id="create-epic">Create Epic</button>' = StoryMapView.render_buttons(buttons: ['Create Epic'])
     return html: '<button>...</button>'
  
  return html: '<button>Create Epic</button>'

DOM.update(element_id: 'node-actions', html: html)

# User clicks Create Epic button
click_event: {button_id: 'create-epic'} = User.clicks(element_id: 'create-epic')

# StoryMapView executes create operation via CLI
result: {success: True, epic_name: 'Epic1'} = CLI.execute_command(command: 'story_graph.create_epic')
  -> story_map: StoryMap = Bot.story_graph
     return story_map: StoryMap
  
  -> new_epic: Epic = StoryMap.create_epic()
     # Domain generates unique name: "Epic1", "Epic2", etc
     -> unique_name: 'Epic1' = StoryMap._generate_unique_epic_name()
        return unique_name: 'Epic1'
     
     # Create Epic instance
     -> epic: Epic = Epic(name: 'Epic1', domain_concepts: [])
        return epic: Epic{name: 'Epic1'}
     
     # Add to epics list at last position
     -> StoryMap._epics_list.append(epic)
     
     # Rebuild epics collection
     -> StoryMap._epics = EpicsCollection(StoryMap._epics_list)
     
     # Update story_graph dict
     -> StoryMap.story_graph['epics'] = [StoryMap._epic_to_dict(e) for e in StoryMap._epics_list]
     
     return epic: Epic{name: 'Epic1'}
  
  return result: {success: True, epic_name: 'Epic1'}
```

---

## Walk 2: Panel Delegates to InlineNameEditor

**Covers:** Steps: CLI returns → put in edit mode → select text

### Object Flow

```
# StoryMapView uses existing responsibility: "Delegates to InlineNameEditor"
InlineNameEditor.enable_editing_mode(node_element: DOM.element('epic-epic1'), current_name: 'Epic1')
  # InlineNameEditor uses existing responsibility: "Enables inline editing mode"
  -> input_field: HTMLInputElement = DOM.create_input_field(value: 'Epic1')
     return input_field: HTMLInputElement
  
  -> DOM.replace_element(old: text_element, new: input_field)
  
  -> DOM.focus(element: input_field)
  
  -> DOM.select_all(element: input_field)
  
  return
```

---

## Walk 3: Panel Refreshes Tree Display

**Covers:** Steps: Refresh tree to show new Epic at root

### Object Flow

```
# StoryMapView uses existing responsibility: "Refreshes tree display"
StoryMapView.refresh_tree_display()
  -> story_map: StoryMap = Bot.story_graph
     return story_map: StoryMap{epics: [Epic{name: 'Epic1'}]}
  
  # StoryMapView uses existing responsibility: "Renders story graph as tree hierarchy"
  -> html: '<div class="tree">...</div>' = StoryMapView.render_tree_hierarchy(story_map: story_map)
     # Renders Story Map root node (NEW)
     -> root_html: '<div class="root">Story Map</div>' = StoryMapView.render_root_node()
        return root_html: '<div>Story Map</div>'
     
     -> epics_html: '<div class="epic">Epic1</div>' = StoryMapView.render_nodes(nodes: story_map.epics)
        return epics_html: '<div>...</div>'
     
     return html: '<div class="tree"><div>Story Map</div><div>Epic1</div></div>'
  
  -> DOM.update(element_id: 'story-tree', html: html)
  
  return
```

---

## Model Updates Discovered

None - all flows traced using existing responsibilities from domain model.

**Note:** StoryMapView's existing responsibility "Shows context-appropriate action buttons" now handles root node selection to show "Create Epic" button.

---

## Key Insights

1. **Root Node in Tree:** Panel must display "Story Map" as selectable root node above all Epics.

2. **Domain Generates Name:** Panel calls `story_graph.create_epic` with NO name parameter. Domain's `create_epic()` generates unique name automatically (Epic1, Epic2, etc.).

3. **Context-Appropriate Buttons:** Panel's existing responsibility "Shows context-appropriate action buttons" implements logic for root node → "Create Epic" button.

4. **Delegation to Editor:** Panel uses existing responsibility "Delegates to InlineNameEditor" to enable edit mode after creation.

5. **Tree Refresh:** Panel uses existing responsibility "Refreshes tree display" to reload and display updated graph with new Epic.

All flows work using only existing responsibilities - no new responsibilities needed except StoryMap.create_epic() in domain model.

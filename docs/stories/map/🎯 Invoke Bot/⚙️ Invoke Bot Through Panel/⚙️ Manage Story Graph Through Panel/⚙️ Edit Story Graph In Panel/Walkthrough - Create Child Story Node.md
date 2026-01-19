# Walkthrough Realization: Create Child Story Node Under Parent

**Scope:** Invoke Bot.Invoke Bot Through Panel.Manage Story Graph Through Panel.Edit Story Graph In Panel.Create Child Story Node Under Parent

**Scenario:** User creates child node with auto-generated name in edit mode

---

## Walk 1: User Clicks Create Button and Panel Calls CLI

**Covers:** Steps: Button click → CLI command → domain operation

### Object Flow

```
click_event: {button_id: 'create-subepic'} = User.clicks(element_id: 'create-subepic')

# StoryMapView uses existing responsibility: "Shows context-appropriate action buttons"
# which includes executing the create operation via CLI

result: {success: True, child_name: 'Child1'} = CLI.execute_command(command: 'cli.story_graph."User Management".create')
  -> graph: StoryGraph = StoryGraph.load(file_path: 'docs/stories/story-graph.json')
     return graph: StoryGraph
  
  -> parent_node: Epic = StoryGraph.find_node(path: 'User Management')
     -> epic: Epic = StoryGraph.epics['User Management']
        return epic: Epic{name: 'User Management', children: []}
     return parent_node: Epic{name: 'User Management', children: []}
  
  -> child: SubEpic = Epic.createChild()
     # Domain generates unique name: "Child1", "Child2", etc (per AC line 1542)
     # Domain determines child type based on parent type
     # Domain adds as last child (per AC line 1538)
     return child: SubEpic{name: 'Child1', sequential_order: 0}
  
  -> StoryGraph.save(file_path: 'docs/stories/story-graph.json')
  
  return result: {success: True, child_name: 'Child1', node_path: 'User Management.Child1'}
```

---

## Walk 2: Panel Delegates to InlineNameEditor

**Covers:** Steps: CLI returns → put in edit mode → select text

### Object Flow

```
# StoryMapView uses existing responsibility: "Delegates to InlineNameEditor"
InlineNameEditor.enable_editing_mode(node_element: DOM.element('subepic-child1'), current_name: 'Child1')
  # InlineNameEditor uses existing responsibility: "Enables inline editing mode"
  -> input_field: HTMLInputElement = DOM.create_input_field(value: 'Child1')
     return input_field: HTMLInputElement
  
  -> DOM.replace_element(old: text_element, new: input_field)
  
  -> DOM.focus(element: input_field)
  
  -> DOM.select_all(element: input_field)
  
  return
```

---

## Walk 3: Panel Refreshes Tree Display

**Covers:** Steps: Refresh tree to show new child

### Object Flow

```
# StoryMapView uses existing responsibility: "Refreshes tree display"
StoryMapView.refresh_tree_display()
  -> graph: StoryGraph = StoryGraph.load(file_path: 'docs/stories/story-graph.json')
     return graph: StoryGraph{epics: [{name: 'User Management', children: [SubEpic{name: 'Child1'}]}]}
  
  # StoryMapView uses existing responsibility: "Renders story graph as tree hierarchy"
  -> html: '<div class="tree">...</div>' = StoryMapView.render_tree_hierarchy(graph: graph)
     -> epic_html: '<div class="epic">User Management<div class="subepic">Child1</div></div>' = StoryMapView.render_nodes(nodes: graph.epics)
        return epic_html: '<div>...</div>'
     return html: '<div class="tree">...</div>'
  
  -> DOM.update(element_id: 'story-tree', html: html)
  
  return
```

---

## Walk 4: Panel Shows Context-Specific Buttons for SubEpic with Stories

**Covers:** Steps: SubEpic with Stories selected → only "Create Story" button shown

### Object Flow

```
selection_event: {node_name: 'Authentication'} = User.clicks(element_id: 'subepic-authentication')

# StoryMapView uses existing responsibility: "Shows context-appropriate action buttons"
html: '<button>Create Story</button>' = StoryMapView.show_context_appropriate_action_buttons(node: 'Authentication')
  -> node_json: {name: 'Authentication', type: 'SubEpic', children: [{type: 'Story', name: 'Login Form'}]} = CLI.execute_command(command: 'cli.story_graph."Authentication"')
     -> node: SubEpic = StoryGraph.find_node(path: 'Authentication')
        return node: SubEpic{name: 'Authentication', children: [Story{name: 'Login Form'}]}
     
     -> node_data: {...} = SubEpic.to_json()
        return node_data: {name: 'Authentication', type: 'SubEpic', children: [{type: 'Story', name: 'Login Form'}]}
     
     return node_json: {name: 'Authentication', type: 'SubEpic', children: [{type: 'Story',...}]}
  
  # Panel determines buttons based on node type and existing children
  # SubEpic with Stories → only "Create Story" button (per AC line 10870)
  -> buttons: ['Create Story'] = StoryMapView.determine_buttons_for_node(node_type: 'SubEpic', children: [{type: 'Story'}])
     return buttons: ['Create Story']
  
  -> html: '<button id="create-story">Create Story</button>' = StoryMapView.render_buttons(buttons: ['Create Story'])
     return html: '<button id="create-story">Create Story</button>'
  
  return html: '<button>Create Story</button>'

DOM.update(element_id: 'node-actions', html: html)
```

---

## Model Updates Discovered

None - all flows traced using existing responsibilities from domain model.

---

## Key Insights

1. **Domain Generates Name:** Panel calls `cli.story_graph."Parent".create` with NO name. Domain's `createChild()` generates unique name automatically.

2. **Context-Appropriate Buttons:** Panel's existing responsibility "Shows context-appropriate action buttons" implements the logic for which buttons to display based on node type and children.

3. **Delegation to Editor:** Panel uses existing responsibility "Delegates to InlineNameEditor" to enable edit mode after creation.

4. **Tree Refresh:** Panel uses existing responsibility "Refreshes tree display" to reload and display updated graph.

5. **InlineNameEditor Responsibilities:** Uses existing responsibilities for enabling edit mode, selecting text, validating names, and showing validation messages.

All flows work using only existing responsibilities - no new responsibilities needed.

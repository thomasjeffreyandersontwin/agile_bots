# Walkthrough Realization: Delete Story Node From Parent

**Scope:** Invoke Bot.Invoke Bot Through Panel.Manage Story Graph Through Panel.Edit Story Graph In Panel.Delete Story Node From Parent

**Scenario:** User confirms delete for node with children and children move to parent

---

## Walk 1: User Selects Node with Children

**Covers:** Steps: Node selection → show both delete buttons

### Object Flow

```
selection_event: {node_name: 'Authentication'} = User.clicks(element_id: 'subepic-authentication')

# StoryMapView uses existing responsibility: "Shows context-appropriate action buttons"
html: '<button>Delete</button><button>Delete Including Children</button>' = StoryMapView.show_context_appropriate_action_buttons(node: 'Authentication')
  -> node_json: {name: 'Authentication', children: [{name: 'Login Form'}, {name: 'Password Reset'}]} = CLI.execute_command(command: 'cli.story_graph."Authentication"')
     -> node: SubEpic = StoryGraph.find_node(path: 'Authentication')
        return node: SubEpic{name: 'Authentication', children: [Story, Story]}
     return node_json: {...}
  
  # Node has children → show both delete buttons (per AC line 10984)
  -> buttons: ['Delete', 'Delete Including Children'] = StoryMapView.determine_buttons(node_json: node_json)
     return buttons: ['Delete', 'Delete Including Children']
  
  return html: '<button>Delete</button><button>Delete Including Children</button>'

DOM.update(element_id: 'node-actions', html: html)
```

---

## Walk 2: User Clicks Delete and Confirmation Shown

**Covers:** Steps: Delete click → confirmation inline → confirm/cancel buttons

### Object Flow

```
click_event: {button_id: 'delete'} = User.clicks(element_id: 'delete')

# Panel shows confirmation inline (per AC line 10985)
html: '<div>Confirm | Cancel</div>' = StoryMapView.show_inline_confirmation(node: 'Authentication', mode: 'delete')
  -> confirmation_html: '<div class="confirmation">Delete "Authentication"? Children will be moved to parent. <button>Confirm</button> <button>Cancel</button></div>' = StoryMapView.render_confirmation()
     return confirmation_html: '<div>...</div>'
  
  return html: '<div>...</div>'

DOM.replace(element_id: 'node-actions', html: html)
```

---

## Walk 3: User Confirms Delete and Domain Moves Children to Parent

**Covers:** Steps: Confirm → CLI delete → domain operation → refresh

### Object Flow

```
click_event: {button_id: 'confirm'} = User.clicks(element_id: 'confirm')

result: {success: True} = CLI.execute_command(command: 'cli.story_graph."Invoke Bot"."Authentication".delete')
  -> parent: Epic = StoryGraph.find_node(path: 'Invoke Bot')
     return parent: Epic{name: 'Invoke Bot'}
  
  -> node_to_delete: SubEpic = Epic.find_child(name: 'Authentication')
     return node_to_delete: SubEpic{name: 'Authentication', children: [Story, Story]}
  
  # Domain deletes node per AC line 10987: "removes node from parent AND resequences siblings"
  # Per domain AC line 1538: when node has children, they move to parent
  -> Epic.delete_child(child: node_to_delete)
     # Move children to parent first
     -> children: [Story, Story] = SubEpic.children
        return children: [Story{name: 'Login Form'}, Story{name: 'Password Reset'}]
     
     -> Epic.add_child(child: Story{name: 'Login Form'})
     -> Epic.add_child(child: Story{name: 'Password Reset'})
     
     # Remove SubEpic
     -> Epic.children.remove(child: node_to_delete)
     
     # Resequence per AC line 10987
     -> Epic.resequence_children()
     
     return
  
  -> StoryGraph.save(file_path: 'docs/stories/story-graph.json')
  
  return result: {success: True}

# StoryMapView uses existing responsibility: "Refreshes tree display"
StoryMapView.refresh_tree_display()
  -> graph: StoryGraph = StoryGraph.load(file_path: 'docs/stories/story-graph.json')
     return graph: StoryGraph
  
  -> html: '<div>...</div>' = StoryMapView.render_tree_hierarchy(graph: graph)
     return html: '<div>...</div>'
  
  -> DOM.update(element_id: 'story-tree', html: html)
  
  return
```

---

## Walk 4: User Confirms Delete Including Children - Recursive Delete

**Covers:** Steps: Confirm delete all → recursive removal → refresh

### Object Flow

```
click_event: {button_id: 'delete-all-confirm'} = User.clicks(element_id: 'delete-all-confirm')

result: {success: True} = CLI.execute_command(command: 'cli.story_graph."Invoke Bot"."Authentication".delete_including_children')
  -> parent: Epic = StoryGraph.find_node(path: 'Invoke Bot')
     return parent: Epic
  
  -> node_to_delete: SubEpic = Epic.find_child(name: 'Authentication')
     return node_to_delete: SubEpic{name: 'Authentication', children: [Story, Story]}
  
  # Domain recursively removes all children per AC line 10988
  -> Epic.delete_child_recursively(child: node_to_delete)
     # Recursively delete all descendants
     -> SubEpic.delete_all_children_recursively()
        -> Story{name: 'Login Form'}.delete_all_children_recursively()
           # Delete Scenario children
           return
        
        -> Story{name: 'Password Reset'}.delete_all_children_recursively()
           return
        
        return
     
     # Remove SubEpic itself
     -> Epic.children.remove(child: node_to_delete)
     
     return
  
  -> StoryGraph.save(file_path: 'docs/stories/story-graph.json')
  
  return result: {success: True}

# StoryMapView uses existing responsibility: "Refreshes tree display"
StoryMapView.refresh_tree_display()
```

---

## Walk 5: User Cancels Delete

**Covers:** Steps: Cancel → hide confirmation → restore buttons

### Object Flow

```
click_event: {button_id: 'cancel'} = User.clicks(element_id: 'cancel')

# Panel hides confirmation per AC line 10989
cancelled: True = StoryMapView.hide_confirmation()
  # Restore original buttons
  -> html: '<button>Delete</button><button>Delete Including Children</button>' = StoryMapView.show_context_appropriate_action_buttons(node: 'Authentication')
     return html: '<button>...</button>'
  
  -> DOM.replace(element_id: 'confirmation', html: html)
  
  return cancelled: True

# Node remains unchanged per AC line 10989 - no domain operation occurred
```

---

## Model Updates Discovered

None - all flows traced using existing responsibilities from domain model.

---

## Key Insights

1. **Two Delete Commands:**
   - `cli.story_graph."Parent"."Node".delete` - moves children to parent
   - `cli.story_graph."Parent"."Node".delete_including_children` - recursive delete

2. **Inline Confirmation:** Panel shows confirmation in place of action buttons before executing domain operation.

3. **Domain Handles Child Movement:** Domain automatically moves children to parent during delete operation.

4. **Recursive Delete:** Domain recursively deletes all descendants bottom-up.

5. **Cancel Has No Side Effects:** Cancel simply hides confirmation and restores original buttons - no domain operation.

All flows work using only existing domain model responsibilities.

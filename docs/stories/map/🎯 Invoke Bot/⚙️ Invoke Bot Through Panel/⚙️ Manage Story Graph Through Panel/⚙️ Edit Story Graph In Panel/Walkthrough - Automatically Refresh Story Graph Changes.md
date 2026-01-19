# Walkthrough Realization: Automatically Refresh Story Graph Changes

**Scope:** Invoke Bot.Invoke Bot Through Panel.Manage Story Graph Through Panel.Edit Story Graph In Panel.Automatically Refresh Story Graph Changes

**Scenario:** Panel detects file modification and refreshes with valid structure

---

## Walk 1: External Modification Detected

**Covers:** Steps: External edit → file watch → modification detected

### Object Flow

```
# External process modifies file
file_write: True = ExternalProcess.write(file_path: 'docs/stories/story-graph.json', content: {...})

# File system emits watch event
watch_event: {file_path: 'docs/stories/story-graph.json', event_type: 'modified'} = FileSystem.emit_event()

# FileModificationMonitor uses existing responsibility: "Detects file modification"
detected: True = FileModificationMonitor.detect_modification(event: watch_event)
  return detected: True
```

---

## Walk 2: Monitor Delegates Reload to StoryGraph

**Covers:** Steps: Reload file → validate → trigger refresh

### Object Flow

```
# FileModificationMonitor uses existing responsibility: "Delegates reload to StoryGraph"
reload_result: {valid: True, graph: StoryGraph} = FileModificationMonitor.delegate_reload()
  -> graph: StoryGraph = StoryGraph.load(file_path: 'docs/stories/story-graph.json')
     return graph: StoryGraph{epics: [...updated...]}
  
  return reload_result: {valid: True, graph: graph}
```

---

## Walk 3: Monitor Triggers Panel Refresh

**Covers:** Steps: Trigger refresh → panel updates tree → preserves navigation

### Object Flow

```
# FileModificationMonitor uses existing responsibility: "Triggers panel refresh"
FileModificationMonitor.trigger_panel_refresh(graph: updated_graph)
  -> StoryMapView.on_refresh_event(graph: updated_graph)
     return

# StoryMapView uses existing responsibility: "Refreshes tree display"
StoryMapView.refresh_tree_display()
  -> graph: StoryGraph = updated_graph
     return graph: StoryGraph
  
  # StoryMapView uses existing responsibility: "Renders story graph as tree hierarchy"
  -> html: '<div>...</div>' = StoryMapView.render_tree_hierarchy(graph: graph)
     return html: '<div class="tree">...</div>'
  
  -> DOM.update(element_id: 'story-tree', html: html)
  
  # Panel preserves navigation state (per AC: "preserves navigation state if possible")
  -> DOM.restore_scroll_position()
  -> DOM.restore_selection()
  
  return
```

---

## Walk 4: Invalid Structure Detected

**Covers:** Steps: Invalid file → validation error → error notification → retain previous state

### Object Flow

```
# External process writes invalid JSON
file_write: True = ExternalProcess.write(file_path: 'docs/stories/story-graph.json', content: '{invalid...')

watch_event: {file_path: 'story-graph.json'} = FileSystem.emit_event()

# FileModificationMonitor uses existing responsibility: "Detects file modification"
detected: True = FileModificationMonitor.detect_modification(event: watch_event)

# FileModificationMonitor uses existing responsibility: "Delegates reload to StoryGraph"
reload_result: {valid: False, error: 'Parse error'} = FileModificationMonitor.delegate_reload()
  -> error: SyntaxError = StoryGraph.load(file_path: 'docs/stories/story-graph.json')
     throw error: SyntaxError
  return reload_result: {valid: False, error: 'Parse error'}

# FileModificationMonitor uses existing responsibility: "Shows validation error notification"
FileModificationMonitor.show_validation_error_notification(error: 'Parse error')
  -> message: 'Story graph file contains invalid structure' = FileModificationMonitor.format_error(error: 'Parse error')
     return message: 'Story graph file contains invalid structure'
  
  -> DOM.show_notification(message: message, type: 'error')
  
  return

# FileModificationMonitor uses existing responsibility: "Retains previous valid graph on error"
retained_graph: StoryGraph = FileModificationMonitor.retain_previous_valid_graph()
  -> previous_graph: StoryGraph = FileModificationMonitor.previous_valid_graph_reference
     return previous_graph: StoryGraph
  
  return retained_graph: StoryGraph

# Panel continues displaying previous valid state
# No tree refresh occurs
```

---

## Model Updates Discovered

None - all flows traced using existing responsibilities from domain model.

---

## Key Insights

1. **FileModificationMonitor Responsibilities:** All four existing responsibilities work together:
   - Detects file modification
   - Delegates reload to StoryGraph
   - Triggers panel refresh (on success)
   - Shows validation error notification (on failure)
   - Retains previous valid graph on error

2. **StoryMapView Responsibilities:** Uses existing responsibilities:
   - Refreshes tree display
   - Renders story graph as tree hierarchy

3. **Error Handling:** When structure is invalid, monitor shows error notification and retains previous valid graph - Panel continues displaying last valid state.

4. **Navigation Preservation:** Panel preserves user's navigation state (selection, scroll) after refresh (per acceptance criteria).

All flows work using only existing domain model responsibilities.

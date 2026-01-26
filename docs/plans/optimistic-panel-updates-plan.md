# Optimistic Panel Updates - Implementation Plan

## Problem Statement

Currently, move/create/rename operations in the Bot Panel take **~5 seconds** to complete:
- Python operation (load + modify + save): ~2-3 seconds
- Panel refresh (reload entire graph): ~2 seconds
- Total: **5 seconds of blocking UI**

This makes the panel feel sluggish and prevents rapid editing workflows.

## Solution: Optimistic Updates with Async Saves

Implement instant UI updates with background saves, similar to Google Docs, VS Code, etc.

### User Experience Flow

```
User drops SubEpic
    ↓
[Instant UI Update]  ← <10ms
  - Move SubEpic in DOM immediately
  - Show spinner: 🔄
  - User can continue working
    ↓
[Background Save]  ← 2-3 seconds (non-blocking)
  - Execute Python command
  - Write to disk
    ↓
Success?
  YES → Show ✓ for 2s, fade out
  NO  → Show ✗, user can click to see error + rollback
```

## Complexity Assessment

**Level: MEDIUM**
**Estimated Time: 6-7 hours**

Most infrastructure exists - we're adding:
1. Save status indicator UI
2. Optimistic DOM updates
3. Async save queue
4. Error handling & rollback

## Implementation Phases

### Phase 1: Add Save Status Indicator (1 hour)

**Objective:** Add visual feedback for save operations in the Story Map header.

**Files to Modify:**
- `src/panel/story_map_view.js`
- `src/panel/bot_panel_styles.css` (create if needed, or inline styles)

**Changes:**

1. **Update Story Map Header Layout**

```javascript
// story_map_view.js - Modify _renderHeader or header rendering
_renderHeader(headerHtml) {
  return `
    <div class="story-map-header" style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px;">
      <div>${headerHtml}</div>
      <div id="save-status-indicator" class="save-status" style="display: none;">
        <span class="save-icon"></span>
        <span class="save-message"></span>
      </div>
    </div>
  `;
}
```

2. **Add CSS Styles**

```css
/* Save status indicator styles */
.save-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
  transition: opacity 0.3s;
  white-space: nowrap;
}

.save-status.saving {
  background: #f0f0f0;
  color: #666;
}

.save-status.success {
  background: #e8f5e9;
  color: #2e7d32;
}

.save-status.error {
  background: #ffebee;
  color: #c62828;
  cursor: pointer;
}

.save-status.error:hover {
  background: #ffcdd2;
}

.save-icon {
  width: 16px;
  height: 16px;
  display: inline-block;
  font-size: 16px;
  line-height: 1;
}

.save-icon.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

**Visual States:**
- **Hidden** (default) - No pending operations
- **🔄 Saving** - Spinning icon + "Saving X change(s)..."
- **✓ Success** - Green checkmark + "Saved" (shows 2s, fades out)
- **✗ Error** - Red X + "Save failed - click for details" (clickable, stays visible)

---

### Phase 2: Create SaveQueue Manager (2 hours)

**Objective:** Build a queue system that batches and manages async save operations.

**File:** `src/panel/story_map_view.js`

**Implementation:**

```javascript
/**
 * Manages queued save operations with visual feedback
 */
class SaveQueue {
  constructor(executeCallback, statusCallback) {
    this.queue = [];
    this.executing = false;
    this.executeCallback = executeCallback; // Function to execute command
    this.statusCallback = statusCallback;   // Function to update UI status
    this.debounceTimer = null;
  }

  /**
   * Add operation to queue and schedule processing
   * @param {Object} operation - {command: string, rollback: function, metadata: object}
   */
  enqueue(operation) {
    this.queue.push({
      ...operation,
      timestamp: Date.now()
    });
    
    // Debounce: wait 500ms after last change before processing
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
    }
    
    this.debounceTimer = setTimeout(() => {
      this.processQueue();
    }, 500);
  }

  /**
   * Process all queued operations in batch
   */
  async processQueue() {
    if (this.executing || this.queue.length === 0) return;
    
    this.executing = true;
    const count = this.queue.length;
    const message = count === 1 ? 'Saving change...' : `Saving ${count} changes...`;
    this.statusCallback('saving', message);
    
    // Take snapshot of current queue
    const batch = [...this.queue];
    this.queue = [];
    
    const results = {
      success: [],
      failed: []
    };
    
    try {
      // Execute all operations sequentially
      for (const op of batch) {
        try {
          await this.executeCallback(op.command);
          results.success.push(op);
        } catch (error) {
          results.failed.push({ op, error });
        }
      }
      
      // Report results
      if (results.failed.length === 0) {
        // All succeeded
        this.statusCallback('success', 'Saved');
        
        // Auto-hide after 2 seconds
        setTimeout(() => {
          this.statusCallback('hidden', '');
        }, 2000);
        
      } else {
        // Some failed - rollback and show error
        const failedCount = results.failed.length;
        const errorMsg = failedCount === 1 
          ? 'Save failed - click for details'
          : `${failedCount} saves failed - click for details`;
        
        const firstError = results.failed[0].error;
        this.statusCallback('error', errorMsg, firstError);
        
        // Rollback failed operations
        for (const { op } of results.failed) {
          if (op.rollback) {
            try {
              op.rollback();
            } catch (rollbackError) {
              console.error('Rollback failed:', rollbackError);
            }
          }
        }
      }
      
    } catch (error) {
      // Critical error - rollback everything
      this.statusCallback('error', 'Save failed - click for details', error);
      
      for (const op of batch) {
        if (op.rollback) {
          try {
            op.rollback();
          } catch (rollbackError) {
            console.error('Rollback failed:', rollbackError);
          }
        }
      }
    }
    
    this.executing = false;
    
    // Process remaining queue if new items added during execution
    if (this.queue.length > 0) {
      setTimeout(() => this.processQueue(), 500);
    }
  }

  /**
   * Update the status indicator UI
   * @param {string} state - 'saving' | 'success' | 'error' | 'hidden'
   * @param {string} message - Display message
   * @param {Error} error - Error object (for error state)
   */
  updateStatus(state, message, error = null) {
    const indicator = document.getElementById('save-status-indicator');
    if (!indicator) return;
    
    const icon = indicator.querySelector('.save-icon');
    const msg = indicator.querySelector('.save-message');
    
    if (state === 'hidden') {
      indicator.style.display = 'none';
      indicator.onclick = null;
      return;
    }
    
    indicator.style.display = 'flex';
    indicator.className = `save-status ${state}`;
    
    // Update icon
    if (state === 'saving') {
      icon.innerHTML = '⟳';
      icon.classList.add('spinner');
    } else if (state === 'success') {
      icon.innerHTML = '✓';
      icon.classList.remove('spinner');
    } else if (state === 'error') {
      icon.innerHTML = '✗';
      icon.classList.remove('spinner');
      
      // Make clickable to show error details
      indicator.onclick = () => {
        const errorDetails = error 
          ? `${error.message}\n\n${error.stack || ''}`
          : 'Unknown error occurred';
        
        // Send to extension host to show error dialog
        this.webview?.postMessage({
          type: 'showErrorDialog',
          title: 'Save Failed',
          message: errorDetails
        });
      };
    }
    
    msg.textContent = message;
  }
}
```

**Integration into StoryMapView:**

```javascript
// story_map_view.js - In constructor
constructor(botPathOrCli, webview, extensionUri, parentView) {
  super(botPathOrCli);
  this.webview = webview;
  this.extensionUri = extensionUri;
  this.parentView = parentView;
  
  // Initialize save queue
  this.saveQueue = new SaveQueue(
    (cmd) => this.execute(cmd),
    (state, msg, err) => this.saveQueue.updateStatus(state, msg, err)
  );
  
  this.saveQueue.webview = webview; // For error dialogs
}
```

---

### Phase 3: Implement Optimistic Updates (2-3 hours)

**Objective:** Update DOM immediately for move/rename/delete operations, then queue saves.

**Files to Modify:**
- `src/panel/story_map_view.js`

**Key Operations to Update:**

#### 1. Move Node

```javascript
/**
 * Handle node move with optimistic update
 */
handleMoveNode(message) {
  const { sourceNodePath, targetParentPath, position } = message;
  
  // Find DOM elements
  const sourceNode = this.findNodeElement(sourceNodePath);
  const targetParent = this.findNodeElement(targetParentPath);
  
  if (!sourceNode || !targetParent) {
    console.error('Move failed: Could not find nodes');
    return;
  }
  
  // 1. Capture current state for rollback
  const rollback = {
    originalParent: sourceNode.parentElement,
    originalPosition: Array.from(sourceNode.parentElement.children).indexOf(sourceNode),
    sourceNode: sourceNode
  };
  
  // 2. Optimistic UI update (immediate)
  this.moveNodeInDOM(sourceNode, targetParent, position);
  
  // 3. Build command
  const command = this.buildMoveCommand(sourceNodePath, targetParentPath, position);
  
  // 4. Queue backend save (async)
  this.saveQueue.enqueue({
    command: command,
    rollback: () => {
      // Restore original position in DOM
      const parent = rollback.originalParent;
      const pos = rollback.originalPosition;
      
      if (pos >= parent.children.length) {
        parent.appendChild(rollback.sourceNode);
      } else {
        parent.insertBefore(rollback.sourceNode, parent.children[pos]);
      }
    },
    metadata: {
      operation: 'move',
      source: sourceNodePath,
      target: targetParentPath,
      position: position
    }
  });
}

/**
 * Pure DOM manipulation for moving nodes
 */
moveNodeInDOM(sourceNode, targetParent, position) {
  const targetContainer = targetParent.querySelector('.children-container') || targetParent;
  const targetChildren = Array.from(targetContainer.children);
  
  // Remove from current position
  sourceNode.parentElement.removeChild(sourceNode);
  
  // Insert at new position
  if (position >= targetChildren.length) {
    targetContainer.appendChild(sourceNode);
  } else {
    targetContainer.insertBefore(sourceNode, targetChildren[position]);
  }
}

/**
 * Build Python command for move operation
 */
buildMoveCommand(sourceNodePath, targetParentPath, position) {
  // Parse paths like "Epic1.SubEpic1.Story1"
  const sourceParts = sourceNodePath.split('.');
  const targetParts = targetParentPath.split('.');
  
  // Build command: story_map["Epic"]["SubEpic"]["Story"].move_to("Target", at_position=1)
  const sourceAccessor = sourceParts.map(p => `["${p}"]`).join('');
  const targetName = targetParts[targetParts.length - 1];
  
  return `story_map${sourceAccessor}.move_to("${targetName}", at_position=${position})`;
}
```

#### 2. Rename Node

```javascript
/**
 * Handle node rename with optimistic update
 */
handleRenameNode(message) {
  const { nodePath, oldName, newName } = message;
  
  const nodeElement = this.findNodeElement(nodePath);
  if (!nodeElement) {
    console.error('Rename failed: Could not find node');
    return;
  }
  
  // 1. Capture for rollback
  const nameElement = nodeElement.querySelector('.node-name');
  const rollback = {
    element: nameElement,
    oldName: oldName
  };
  
  // 2. Optimistic UI update
  nameElement.textContent = newName;
  nameElement.setAttribute('data-node-name', newName);
  
  // 3. Build command
  const command = this.buildRenameCommand(nodePath, oldName, newName);
  
  // 4. Queue save
  this.saveQueue.enqueue({
    command: command,
    rollback: () => {
      rollback.element.textContent = rollback.oldName;
      rollback.element.setAttribute('data-node-name', rollback.oldName);
    },
    metadata: {
      operation: 'rename',
      path: nodePath,
      oldName: oldName,
      newName: newName
    }
  });
}

/**
 * Build Python command for rename operation
 */
buildRenameCommand(nodePath, oldName, newName) {
  const parts = nodePath.split('.');
  const accessor = parts.map(p => `["${p}"]`).join('');
  return `story_map${accessor}.rename("${newName}")`;
}
```

#### 3. Delete Node

```javascript
/**
 * Handle node delete with optimistic update
 */
handleDeleteNode(message) {
  const { nodePath } = message;
  
  const nodeElement = this.findNodeElement(nodePath);
  if (!nodeElement) {
    console.error('Delete failed: Could not find node');
    return;
  }
  
  // 1. Capture entire node HTML for rollback
  const parent = nodeElement.parentElement;
  const position = Array.from(parent.children).indexOf(nodeElement);
  const nodeHTML = nodeElement.outerHTML;
  
  const rollback = {
    parent: parent,
    position: position,
    nodeHTML: nodeHTML
  };
  
  // 2. Optimistic UI update (remove from DOM)
  nodeElement.remove();
  
  // 3. Build command
  const command = this.buildDeleteCommand(nodePath);
  
  // 4. Queue save
  this.saveQueue.enqueue({
    command: command,
    rollback: () => {
      // Restore deleted node
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = rollback.nodeHTML;
      const restoredNode = tempDiv.firstChild;
      
      if (rollback.position >= rollback.parent.children.length) {
        rollback.parent.appendChild(restoredNode);
      } else {
        rollback.parent.insertBefore(restoredNode, rollback.parent.children[rollback.position]);
      }
    },
    metadata: {
      operation: 'delete',
      path: nodePath
    }
  });
}

/**
 * Build Python command for delete operation
 */
buildDeleteCommand(nodePath) {
  const parts = nodePath.split('.');
  const accessor = parts.map(p => `["${p}"]`).join('');
  return `story_map${accessor}.delete()`;
}
```

#### 4. Helper Method

```javascript
/**
 * Find DOM element by node path
 * @param {string} nodePath - e.g., "Epic1.SubEpic1.Story1"
 * @returns {HTMLElement|null}
 */
findNodeElement(nodePath) {
  const parts = nodePath.split('.');
  const nodeName = parts[parts.length - 1];
  
  // Find element with matching data-node-path attribute
  return document.querySelector(`[data-node-path="${nodePath}"]`);
}
```

---

### Phase 4: Skip Unnecessary Refreshes (30 minutes)

**Objective:** Don't reload entire panel after optimistic operations - only update status indicator.

**File:** `src/panel/bot_panel.js`

**Changes:**

```javascript
// bot_panel.js - Modify executeCommand handler
case "executeCommand":
  if (message.commandText) {
    this._log(`[BotPanel] RECEIVED executeCommand MESSAGE`);
    this._log(`[BotPanel] commandText: ${message.commandText}`);
    
    // Check if this is an optimistic operation
    const isOptimistic = message.optimistic === true;
    
    const fs = require('fs');
    const logPath = path.join(this._workspaceRoot, 'story_graph_operations.log');
    const timestamp = new Date().toISOString();
    const logEntry = `\n${'='.repeat(80)}\n[${timestamp}] RECEIVED COMMAND (optimistic=${isOptimistic}): ${message.commandText}\n`;
    
    try {
      fs.appendFileSync(logPath, logEntry);
    } catch (err) {
      this._log(`[BotPanel] Failed to write to log file: ${err.message}`);
    }
    
    this._log(`[BotPanel] Calling botView.execute...`);
    this._botView?.execute(message.commandText)
      .then((result) => {
        this._log(`[BotPanel] executeCommand SUCCESS`);
        this._log(`[BotPanel] result: ${JSON.stringify(result).substring(0, 500)}`);
        
        // Log result to file
        const resultLog = `[${timestamp}] SUCCESS RESULT: ${JSON.stringify(result, null, 2)}\n`;
        try {
          fs.appendFileSync(logPath, resultLog);
        } catch (err) {
          this._log(`[BotPanel] Failed to write result to log file: ${err.message}`);
        }
        
        // Update timestamp for behavior cache invalidation
        const timestampFile = path.join(this._workspaceRoot, 'docs', 'stories', '.story-graph-panel-edit-time');
        try {
          fs.writeFileSync(timestampFile, Date.now().toString());
          this._log(`[BotPanel] Logged panel edit timestamp: ${Date.now()}`);
        } catch (err) {
          this._log(`[BotPanel] Failed to write timestamp file: ${err.message}`);
        }
        
        // CRITICAL: Only refresh if NOT optimistic
        if (isOptimistic) {
          this._log(`[BotPanel] Optimistic operation - skipping panel refresh`);
          return Promise.resolve();
        } else {
          this._log(`[BotPanel] Non-optimistic operation - calling _update() to refresh panel...`);
          return this._update();
        }
      })
      .then(() => {
        this._log(`[BotPanel] Command processing completed`);
        this._log(`${'='.repeat(80)}\n`);
      })
      .catch((error) => {
        this._log(`[BotPanel] *** executeCommand ERROR ***`);
        this._log(`[BotPanel] command: ${message.commandText}`);
        this._log(`[BotPanel] error: ${error.message}`);
        this._log(`[BotPanel] stack: ${error.stack}`);
        
        // Log error to file
        const errorLog = `[${timestamp}] ERROR: ${error.message}\nSTACK: ${error.stack}\n`;
        try {
          fs.appendFileSync(logPath, errorLog);
        } catch (err) {
          this._log(`[BotPanel] Failed to write error to log file: ${err.message}`);
        }
        
        vscode.window.showErrorMessage(`Operation failed: ${error.message}`);
        
        // Always refresh on error to show accurate backend state
        // (rollback should have already happened in SaveQueue)
        if (!isOptimistic) {
          this._update().catch(err => {
            this._log(`[BotPanel] ERROR in _update after failure: ${err.message}`);
          });
        }
      });
  }
  return;
```

**Update Message Sending:**

```javascript
// story_map_view.js - When sending commands
this.webview.postMessage({
  type: 'executeCommand',
  commandText: command,
  optimistic: true  // ← Mark as optimistic
});
```

---

## Testing Plan

### 1. Single Operation Test
- **Action:** Move one SubEpic to a new position
- **Expected:**
  - SubEpic moves instantly in UI
  - Spinner appears in header
  - After ~2-3s, checkmark appears
  - Checkmark fades after 2s
  - Backend file updated correctly

### 2. Rapid Operations Test
- **Action:** Move 5 SubEpics quickly (within 2 seconds)
- **Expected:**
  - All 5 move instantly in UI
  - Spinner shows "Saving 5 changes..."
  - One batch save completes
  - Single checkmark appears
  - All changes persisted correctly

### 3. Error Handling Test
- **Action:** Rename a Story to an invalid name (e.g., empty string, duplicate, special chars)
- **Expected:**
  - Name changes instantly in UI
  - Spinner appears
  - Red X appears with "Save failed" message
  - Click X shows error details
  - Name rolls back to original
  - Backend file unchanged

### 4. Network/Process Failure Test
- **Action:** Rename a Story, immediately kill Python process
- **Expected:**
  - Name changes instantly
  - Spinner appears
  - Eventually times out with error
  - Red X appears
  - Name rolls back
  - User informed of failure

### 5. Concurrent Operations Test
- **Action:** Start moving SubEpic A, then immediately rename SubEpic B before first save completes
- **Expected:**
  - Both changes appear instantly
  - Spinner shows "Saving 2 changes..."
  - Both operations queued and processed
  - Single checkmark after completion
  - Both changes persisted

### 6. Validation Test
- **Action:** Move Story to invalid parent type (e.g., Story under Story)
- **Expected:**
  - Move happens in UI
  - Spinner appears
  - Backend rejects with validation error
  - Red X appears
  - Story rolls back to original position
  - Error details available on click

### 7. Long Operation Test
- **Action:** Create 10 new Stories rapidly
- **Expected:**
  - All appear instantly in UI
  - Spinner shows "Saving 10 changes..."
  - Progress visible (spinner keeps spinning)
  - Checkmark after all complete
  - All Stories persisted

---

## Migration Strategy

### Phase 1: Feature Flag Implementation
Add configuration to enable/disable optimistic updates:

```javascript
// story_map_view.js
const OPTIMISTIC_UPDATES_ENABLED = true; // Feature flag

if (OPTIMISTIC_UPDATES_ENABLED) {
  this.handleMoveNodeOptimistic(message);
} else {
  this.handleMoveNodeBlocking(message);
}
```

### Phase 2: Gradual Rollout
1. **Week 1:** Enable for move operations only
2. **Week 2:** Enable for rename operations
3. **Week 3:** Enable for create/delete operations
4. **Week 4:** Full rollout if no issues

### Phase 3: Remove Old Code
Once stable for 2+ weeks, remove blocking implementation and feature flag.

---

## Risk Assessment

### Low Risk ✅
- All changes are additive
- Can be feature-flagged
- Easy rollback by setting `OPTIMISTIC_UPDATES_ENABLED = false`
- Existing validation logic unchanged
- Backend save logic unchanged

### Medium Risk ⚠️
- DOM manipulation bugs could cause UI/backend drift
  - **Mitigation:** Comprehensive testing + rollback mechanism
- Race conditions with rapid operations
  - **Mitigation:** Queue system with debouncing
- Complex rollback scenarios (partial failures)
  - **Mitigation:** Transactional rollback (all or nothing)

### High Risk ❌
- None identified

---

## Success Metrics

### Performance
- **Move operation:** 5 seconds → **<50ms perceived time**
- **Rename operation:** 5 seconds → **<50ms perceived time**
- **Create operation:** 5 seconds → **<50ms perceived time**
- **Batch operations:** Linear time → **Constant time** (all instant, one save)

### User Experience
- Zero blocking UI during operations
- Clear visual feedback on save status
- Graceful error handling with rollback
- Professional, modern feel

### Reliability
- <1% rollback rate (failed saves)
- Zero data loss incidents
- No UI/backend state drift

---

## Future Enhancements (Not in this plan)

1. **Persistent Python Process**
   - Keep Python process alive via MCP/WebSocket
   - Eliminates process spawn overhead
   - Enables instant validation
   - Allows true batched operations

2. **Conflict Resolution**
   - Handle concurrent edits from multiple sources
   - Show merge conflicts in UI
   - Allow user to resolve

3. **Undo/Redo Stack**
   - Track operation history
   - Ctrl+Z / Ctrl+Y support
   - Works with optimistic updates

4. **Offline Mode**
   - Queue operations when backend unavailable
   - Sync when connection restored
   - Show "offline" indicator

---

## Approval Checklist

Before starting implementation:
- [ ] Plan reviewed and approved
- [ ] Timeline acceptable (6-7 hours)
- [ ] Feature flag strategy approved
- [ ] Testing plan sufficient
- [ ] Rollback plan clear

---

## Implementation Notes

### Key Files to Modify
1. `src/panel/story_map_view.js` - Main implementation
2. `src/panel/bot_panel.js` - Skip unnecessary refreshes
3. `src/panel/bot_panel_styles.css` - Status indicator styles (create if needed)

### Dependencies
- No new external dependencies required
- Uses existing `execute()` method for backend operations
- Uses existing DOM manipulation APIs

### Backward Compatibility
- Fully backward compatible
- Can run side-by-side with existing code
- Feature flag allows instant rollback

---

**Document Version:** 1.0  
**Created:** 2026-01-26  
**Author:** AI Assistant  
**Status:** Draft - Pending Approval

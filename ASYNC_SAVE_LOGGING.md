# Async Save Logging Guide

## Overview
Comprehensive logging has been added throughout the async save flow to track every step from user action to final save completion/failure.

## Log Prefixes
All async save logs are prefixed with `[ASYNC_SAVE]` for easy filtering:
- `[ASYNC_SAVE] [WEBVIEW]` - Logs from webview (browser console)
- `[ASYNC_SAVE] [EXTENSION_HOST]` - Logs from extension host (VS Code Output panel)
- `[ASYNC_SAVE] [QUEUE]` - Logs from async save queue
- `[ASYNC_SAVE] [OPTIMISTIC]` - Logs for optimistic DOM updates
- `[ASYNC_SAVE] [USER_ACTION]` - Logs when user initiates an action

## Move Operation Flow

### Step 1: User Action (Webview)
```
[ASYNC_SAVE] ========== MOVE OPERATION START ==========
[ASYNC_SAVE] [USER_ACTION] User dropped node
[ASYNC_SAVE] [STEP 1] Applying optimistic DOM update
[ASYNC_SAVE] [OPTIMISTIC] applyOptimisticMove() called
[ASYNC_SAVE] [OPTIMISTIC] [SUCCESS] Optimistic move applied - node moved in DOM
[ASYNC_SAVE] [STEP 2] Showing save status indicator
[ASYNC_SAVE] [STEP 1] showSaveStatus() called
[ASYNC_SAVE] [STEP 2] Setting indicator display to flex
[ASYNC_SAVE] [STEP 3] Status indicator visible
[ASYNC_SAVE] [STEP 3] Sending command to extension host
[ASYNC_SAVE] [STEP 3] Command sent, waiting for backend response...
[ASYNC_SAVE] ========== MOVE OPERATION QUEUED ==========
```

### Step 2: Extension Host Receives Command
```
[ASYNC_SAVE] [EXTENSION_HOST] ========== COMMAND RECEIVED ==========
[ASYNC_SAVE] [EXTENSION_HOST] [STEP 4] Received executeCommand message
[ASYNC_SAVE] [EXTENSION_HOST] [STEP 4] Operation type detected
[ASYNC_SAVE] [EXTENSION_HOST] [STEP 5] Executing command via backend...
```

### Step 3: Backend Execution
```
[ASYNC_SAVE] [EXTENSION_HOST] [STEP 6] [SUCCESS] Backend command executed successfully
[ASYNC_SAVE] [EXTENSION_HOST] [STEP 7] Sending saveCompleted(success=true) to webview
[ASYNC_SAVE] [EXTENSION_HOST] [STEP 8] Refreshing panel to show latest state...
[ASYNC_SAVE] [EXTENSION_HOST] [STEP 9] Panel refresh completed
[ASYNC_SAVE] [EXTENSION_HOST] ========== COMMAND FLOW COMPLETE ==========
```

### Step 4: Webview Receives Success
```
[ASYNC_SAVE] [WEBVIEW] [STEP 10] Received saveCompleted message from extension host
[ASYNC_SAVE] [WEBVIEW] [STEP 10] Processing success response
[ASYNC_SAVE] [SUCCESS] showSaveSuccess() called
[ASYNC_SAVE] [SUCCESS] Updating indicator to show success
[ASYNC_SAVE] [SUCCESS] Scheduling auto-hide in 2000ms
[ASYNC_SAVE] [SUCCESS] Auto-hide timeout fired, hiding indicator
[ASYNC_SAVE] [WEBVIEW] ========== SAVE FLOW COMPLETE ==========
```

## Rename Operation Flow

### Step 1: User Action (Webview)
```
[ASYNC_SAVE] ========== RENAME OPERATION START ==========
[ASYNC_SAVE] [USER_ACTION] User double-clicked node to rename
[ASYNC_SAVE] [USER_ACTION] Extracted current name
[ASYNC_SAVE] [USER_ACTION] Sending renameNode message to extension host
[ASYNC_SAVE] ========== RENAME OPERATION INITIATED ==========
```

### Step 2: Extension Host Processes Rename
```
[ASYNC_SAVE] [EXTENSION_HOST] ========== RENAME OPERATION RECEIVED ==========
[ASYNC_SAVE] [EXTENSION_HOST] [RENAME] Received renameNode message
[ASYNC_SAVE] [EXTENSION_HOST] [RENAME] Prompting user for new name
[ASYNC_SAVE] [EXTENSION_HOST] [RENAME] User provided new name
[ASYNC_SAVE] [EXTENSION_HOST] [RENAME] Built rename command
[ASYNC_SAVE] [EXTENSION_HOST] [RENAME] Executing rename command via backend...
[ASYNC_SAVE] [EXTENSION_HOST] [RENAME] [SUCCESS] Backend rename executed successfully
[ASYNC_SAVE] [EXTENSION_HOST] [RENAME] Refreshing panel...
[ASYNC_SAVE] [EXTENSION_HOST] [RENAME] Panel refresh completed
[ASYNC_SAVE] [EXTENSION_HOST] ========== RENAME OPERATION COMPLETE ==========
```

## Error Flow

### If Backend Fails
```
[ASYNC_SAVE] [EXTENSION_HOST] [ERROR] Command execution failed
[ASYNC_SAVE] [EXTENSION_HOST] [ERROR] Sending saveCompleted(success=false) to webview
[ASYNC_SAVE] [WEBVIEW] [STEP 10] Received saveCompleted message
[ASYNC_SAVE] [WEBVIEW] [STEP 10] Processing error response
[ASYNC_SAVE] [ERROR] showSaveError() called
[ASYNC_SAVE] [ERROR] Updating indicator to show error
[ASYNC_SAVE] [ERROR] Error indicator displayed (will not auto-hide)
```

## Where to View Logs

### Webview Logs (Browser Console)
1. Right-click in the Bot Panel
2. Select "Inspect" or "Inspect Element"
3. Open the "Console" tab
4. Filter by `[ASYNC_SAVE]`

### Extension Host Logs (VS Code Output)
1. Open VS Code Output panel (`Ctrl+Shift+U` or `View > Output`)
2. Select "Log (Extension Host)" from the dropdown
3. Filter by `[ASYNC_SAVE]`

## Debugging Checklist

When debugging async save issues, check these logs in order:

1. ✅ **User Action Logged?**
   - Look for `[USER_ACTION]` logs
   - Verify the action type (move/rename)

2. ✅ **Optimistic Update Applied?**
   - Look for `[OPTIMISTIC]` logs
   - Check if DOM update succeeded

3. ✅ **Spinner Shown?**
   - Look for `[STEP 2]` and `showSaveStatus()` logs
   - Verify `Status indicator visible` log

4. ✅ **Command Sent to Extension Host?**
   - Look for `[STEP 3]` logs
   - Verify command string

5. ✅ **Extension Host Received Command?**
   - Look for `[EXTENSION_HOST] [STEP 4]` logs
   - Verify operation type detected

6. ✅ **Backend Executed?**
   - Look for `[STEP 6]` logs
   - Check success/error status

7. ✅ **Webview Received Response?**
   - Look for `[STEP 10]` logs
   - Verify success/error message received

8. ✅ **Status Indicator Updated?**
   - Look for `[SUCCESS]` or `[ERROR]` logs
   - Check if spinner changed to success/error

## Common Issues

### Spinner Not Showing
- Check `[STEP 2]` logs - is `showSaveStatus()` being called?
- Check `[STEP 3]` logs - verify element exists
- Inspect DOM: `document.getElementById('save-status-indicator')`

### Optimistic Update Not Working
- Check `[OPTIMISTIC]` logs - is function being called?
- Check for errors in optimistic update function
- Verify DOM elements exist: `document.querySelector('[data-path="..."]')`

### Command Not Executing
- Check `[EXTENSION_HOST] [STEP 4]` logs - was command received?
- Check `[STEP 5]` logs - is backend execution starting?
- Check for errors in `[ERROR]` logs

### Status Not Updating After Save
- Check `[STEP 10]` logs - was message received?
- Check `[SUCCESS]` or `[ERROR]` logs - is function being called?
- Verify message handler is registered

## Filtering Logs

### VS Code Output Panel
Use the filter box and enter: `ASYNC_SAVE`

### Browser Console
Use console filter: `ASYNC_SAVE`

### All Logs for One Operation
Look for the operation start marker:
- Move: `========== MOVE OPERATION START ==========`
- Rename: `========== RENAME OPERATION START ==========`

Then follow the logs until you see the completion marker.

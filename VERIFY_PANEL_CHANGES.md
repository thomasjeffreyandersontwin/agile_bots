# Verifying Panel Changes

## Issue
The optimistic updates and spinner are not appearing in the panel even after reinstalling.

## Steps to Verify Changes Are Applied

1. **Reload VS Code Window**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Developer: Reload Window"
   - Press Enter
   - This forces VS Code to reload the extension and regenerate webview HTML

2. **Close and Reopen the Panel**
   - Close the Bot Panel completely
   - Reopen it using the command palette or the command
   - The new HTML with status indicator should be generated

3. **Check Browser Console**
   - Right-click in the panel → "Inspect" or "Inspect Element"
   - Open the Console tab
   - Look for messages starting with `[WebView]`
   - When you drag a node, you should see:
     - `[WebView] ========== OPTIMISTIC UPDATE START ==========`
     - `[WebView] showSaveStatus called with count: 1`
     - `[WebView] Showing save status indicator`

4. **Verify Status Indicator Element Exists**
   - In the browser inspector, search for `save-status-indicator`
   - It should be in the `.main-header` div
   - When visible, it should have `display: flex` style

5. **Check if Extension is Running from Source**
   - Make sure you're not running a packaged `.vsix` file
   - The extension should be loaded from `src/panel/` directory
   - Check Output panel → "Log (Extension Host)" for file paths

## Expected Behavior After Fix

When you drag and drop a story node:
1. **Immediately**: Node moves in DOM (optimistic update)
2. **Immediately**: Spinner appears in header with "Saving 1 change..." message
3. **After 500ms**: Backend command is sent
4. **After backend completes**: Spinner changes to green checkmark "Saved"
5. **After 2 seconds**: Status indicator auto-hides

## If Still Not Working

1. Check that `bot_header_view.js` has the status indicator HTML (line ~155)
2. Check that `bot_panel.js` has the `showSaveStatus` function (line ~2272)
3. Check that the drop handler calls `showSaveStatus(1)` (line ~2024)
4. Verify the CSS for `.main-header-status` exists (line ~1406)

## Debugging

Open browser console in the panel and run:
```javascript
// Check if status indicator exists
document.getElementById('save-status-indicator')

// Manually trigger spinner
showSaveStatus(1)

// Check if functions exist
typeof showSaveStatus
typeof applyOptimisticMove
```

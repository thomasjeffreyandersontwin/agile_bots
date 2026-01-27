/**
 * StoryMapView - Renders story map with filtering and editing capabilities.
 * 
 * Combines scope filtering with story graph editing in one unified view.
 * 
 * Epic: Invoke Bot Through Panel
 * Sub-Epic: Manage Story Graph Through Panel
 * Stories: 
 *   - Display Story Scope Hierarchy, Filter Story Scope
 *   - Edit Story Graph In Panel
 */

const PanelView = require('./panel_view');
const StoryGraphAsyncSaveController = require('./story_graph/async_save_controller.js');
const fs = require('fs');
const path = require('path');

// Simple file logger
function log(msg) {
    const timestamp = new Date().toISOString();
    try {
        const logFile = path.join(process.cwd(), 'panel-debug.log');
        fs.appendFileSync(logFile, `${timestamp} ${msg}\n`);
    } catch (e) {
        // Ignore
    }
    console.log(msg);
}

class StoryMapView extends PanelView {
    /**
     * Story map view with filtering and editing.
     * 
     * @param {string|PanelView} botPathOrCli - Bot path or CLI instance
     * @param {Object} webview - VS Code webview instance (optional)
     * @param {Object} extensionUri - Extension URI (optional)
     * @param {Object} parentView - Parent BotView (optional, for accessing cached botData)
     */
    constructor(botPathOrCli, webview, extensionUri, parentView = null) {
        super(botPathOrCli);
        this.webview = webview || null;
        this.extensionUri = extensionUri || null;
        this.parentView = parentView;
        
        // Initialize save queue using existing StoryGraphAsyncSaveController
        // This manages the backend queue and coordinates with webview for DOM updates
        const backendPanel = this; // StoryMapView extends PanelView, can execute commands
        this.saveQueue = new StoryGraphAsyncSaveController(backendPanel);
    }
    
    /**
     * Render header with save status indicator
     * @param {string} headerHtml - Existing header HTML
     * @returns {string} Header HTML with status indicator
     */
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
    
    /**
     * Escape HTML entities.
     * 
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        if (typeof text !== 'string') {
            text = String(text);
        }
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
    
    /**
     * Escape for JavaScript string.
     * 
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeForJs(text) {
        if (typeof text !== 'string') {
            text = String(text);
        }
        return text.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '\\"').replace(/\n/g, '\\n').replace(/\r/g, '\\r');
    }
    
    /**
     * Create scenario anchor ID from scenario name (matches synchronizer format).
     * 
     * @param {string} scenarioName - Scenario name
     * @returns {string} Anchor ID
     */
    createScenarioAnchor(scenarioName) {
        if (typeof scenarioName !== 'string') {
            scenarioName = String(scenarioName);
        }
        // Normalize for markdown anchor: lowercase, replace spaces/special chars with hyphens
        let anchor = scenarioName.toLowerCase();
        // Replace spaces and common special characters with hyphens
        anchor = anchor.replace(/[^\w\s-]/g, '');
        anchor = anchor.replace(/[-\s]+/g, '-');
        // Remove leading/trailing hyphens
        anchor = anchor.replace(/^-+|-+$/g, '');
        return `scenario-${anchor}`;
    }
    
    /**
     * Render scope section HTML.
     * 
     * @returns {string} HTML string
     */
    async render() {
        // ===== PERFORMANCE: Start story map rendering =====
        const perfRenderStart = performance.now();
        
        // Use cached botData from parent if available, otherwise fetch it
        const perfStatusStart = performance.now();
        const botData = this.parentView?.botData || await this.execute('status');
        const perfStatusEnd = performance.now();
        const dataSource = this.parentView?.botData ? 'cached' : 'fetched';
        log(`[StoryMapView] [PERF] Bot data (${dataSource}): ${(perfStatusEnd - perfStatusStart).toFixed(2)}ms`);
        
        const scopeData = botData.scope || { type: 'all', filter: '', content: null, graphLinks: [] };
        const vscode = require('vscode');
        
        // Get the proper webview URIs for icons
        // In test mode (no webview), use simple paths so tests can verify icon presence
        let magnifyingGlassIconPath = 'img/magnifying_glass.png';
        let clearIconPath = 'img/close.png';
        let showAllIconPath = 'img/show_all.png';
        let plusIconPath = 'img/plus.png';
        let subtractIconPath = 'img/subtract.png';
        let emptyIconPath = 'img/empty.png';
        let gearIconPath = 'img/gear.png';
        let epicIconPath = 'img/light_bulb2.png';
        let pageIconPath = 'img/page.png';
        let testTubeIconPath = 'img/test_tube.png';
        let documentIconPath = 'img/document.png';
        let addEpicIconPath = 'img/add_epic.png';
        let addSubEpicIconPath = 'img/add_sub_epic.png';
        let addStoryIconPath = 'img/add_story.png';
        let addTestsIconPath = 'img/add_tests.png';
        let addAcceptanceCriteriaIconPath = 'img/add_ac.png';
        let deleteIconPath = 'img/delete.png';
        let deleteChildrenIconPath = 'img/delete_children.png';
        let scopeToIconPath = 'img/bullseye.png';
        let submitShapeIconPath = 'img/submit_subepic.png';
        let submitExploreIconPath = 'img/submit_story.png';
        let submitScenarioIconPath = 'img/submit_ac.png';
        let submitTestIconPath = 'img/submit_tests.png';
        let submitCodeIconPath = 'img/submit_code.png';
        
        if (this.webview && this.extensionUri) {
            try {
                const magnifyingGlassUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'magnifying_glass.png');
                magnifyingGlassIconPath = this.webview.asWebviewUri(magnifyingGlassUri).toString();
                
                const clearUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'close.png');
                clearIconPath = this.webview.asWebviewUri(clearUri).toString();
                
                const showAllUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'show_all.png');
                showAllIconPath = this.webview.asWebviewUri(showAllUri).toString();
                
                const plusUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'plus.png');
                plusIconPath = this.webview.asWebviewUri(plusUri).toString();
                
                const subtractUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'subtract.png');
                subtractIconPath = this.webview.asWebviewUri(subtractUri).toString();
                
                const emptyUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'empty.png');
                emptyIconPath = this.webview.asWebviewUri(emptyUri).toString();
                
                const gearUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'gear.png');
                gearIconPath = this.webview.asWebviewUri(gearUri).toString();
                
                const epicUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'light_bulb2.png');
                epicIconPath = this.webview.asWebviewUri(epicUri).toString();
                
                const pageUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'page.png');
                pageIconPath = this.webview.asWebviewUri(pageUri).toString();
                
                const testTubeUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'test_tube.png');
                testTubeIconPath = this.webview.asWebviewUri(testTubeUri).toString();
                
                const documentUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'document.png');
                documentIconPath = this.webview.asWebviewUri(documentUri).toString();
                
                const addEpicUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'add_epic.png');
                addEpicIconPath = this.webview.asWebviewUri(addEpicUri).toString();
                
                const addSubEpicUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'add_sub_epic.png');
                addSubEpicIconPath = this.webview.asWebviewUri(addSubEpicUri).toString();
                
                const addStoryUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'add_story.png');
                addStoryIconPath = this.webview.asWebviewUri(addStoryUri).toString();
                
                const addTestsUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'add_tests.png');
                addTestsIconPath = this.webview.asWebviewUri(addTestsUri).toString();
                
                const addAcceptanceCriteriaUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'add_ac.png');
                addAcceptanceCriteriaIconPath = this.webview.asWebviewUri(addAcceptanceCriteriaUri).toString();
                
                const deleteUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'delete.png');
                deleteIconPath = this.webview.asWebviewUri(deleteUri).toString();
                
                const deleteChildrenUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'delete_children.png');
                deleteChildrenIconPath = this.webview.asWebviewUri(deleteChildrenUri).toString();
                
                const scopeToUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'bullseye.png');
                scopeToIconPath = this.webview.asWebviewUri(scopeToUri).toString();
                
                const submitShapeUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'submit_subepic.png');
                submitShapeIconPath = this.webview.asWebviewUri(submitShapeUri).toString();
                
                const submitExploreUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'submit_story.png');
                submitExploreIconPath = this.webview.asWebviewUri(submitExploreUri).toString();
                
                const submitScenarioUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'submit_ac.png');
                submitScenarioIconPath = this.webview.asWebviewUri(submitScenarioUri).toString();
                
                const submitTestUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'submit_tests.png');
                submitTestIconPath = this.webview.asWebviewUri(submitTestUri).toString();
                
                const submitCodeUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'submit_code.png');
                submitCodeIconPath = this.webview.asWebviewUri(submitCodeUri).toString();
            } catch (err) {
                console.error('Failed to create icon URIs:', err);
            }
        }
        
        // Create contextual action buttons toolbar
        const actionButtonsHtml = `
            <div id="contextual-actions" style="display: flex; align-items: center; margin-left: 12px; gap: 6px;">
                <!-- Create and delete buttons with tight spacing -->
                <div style="display: flex; align-items: center; gap: 2px;">
                    <button id="btn-create-epic" onclick="event.stopPropagation(); createEpic();" style="display: block; background: transparent; border: none; padding: 4px; cursor: pointer; transition: opacity 0.15s ease;" onmouseover="this.style.opacity='0.7'" onmouseout="this.style.opacity='1'" title="Create Epic">
                        <img src="${addEpicIconPath}" style="width: 28px; height: 28px; object-fit: contain;" alt="Create Epic" />
                    </button>
                    <button id="btn-create-sub-epic" onclick="event.stopPropagation(); handleContextualCreate('sub-epic');" style="display: none; background: transparent; border: none; padding: 4px; cursor: pointer; transition: opacity 0.15s ease;" onmouseover="this.style.opacity='0.7'" onmouseout="this.style.opacity='1'" title="Create Sub-Epic">
                        <img src="${addSubEpicIconPath}" style="width: 28px; height: 28px; object-fit: contain;" alt="Create Sub-Epic" />
                    </button>
                    <button id="btn-create-story" onclick="event.stopPropagation(); handleContextualCreate('story');" style="display: none; background: transparent; border: none; padding: 4px; cursor: pointer; transition: opacity 0.15s ease;" onmouseover="this.style.opacity='0.7'" onmouseout="this.style.opacity='1'" title="Create Story">
                        <img src="${addStoryIconPath}" style="width: 28px; height: 28px; object-fit: contain;" alt="Create Story" />
                    </button>
                    <button id="btn-create-scenario" onclick="event.stopPropagation(); handleContextualCreate('scenario');" style="display: none; background: transparent; border: none; padding: 4px; cursor: pointer; transition: opacity 0.15s ease;" onmouseover="this.style.opacity='0.7'" onmouseout="this.style.opacity='1'" title="Create Scenario">
                        <img src="${addTestsIconPath}" style="width: 28px; height: 28px; object-fit: contain;" alt="Create Scenario" />
                    </button>
                    <button id="btn-create-acceptance-criteria" onclick="event.stopPropagation(); handleContextualCreate('acceptance-criteria');" style="display: none; background: transparent; border: none; padding: 4px; cursor: pointer; transition: opacity 0.15s ease;" onmouseover="this.style.opacity='0.7'" onmouseout="this.style.opacity='1'" title="Create Acceptance Criteria">
                        <img src="${addAcceptanceCriteriaIconPath}" style="width: 28px; height: 28px; object-fit: contain;" alt="Create Acceptance Criteria" />
                    </button>
                    <button id="btn-delete" onclick="event.stopPropagation(); handleDelete();" style="display: none; background: transparent; border: none; padding: 4px; cursor: pointer; transition: opacity 0.15s ease;" onmouseover="this.style.opacity='0.7'" onmouseout="this.style.opacity='1'" title="Delete (including children)">
                        <img src="${deleteIconPath}" style="width: 28px; height: 28px; object-fit: contain;" alt="Delete" />
                    </button>
                </div>
                
                <!-- Scope buttons group with space for additional scope buttons -->
                <div style="display: flex; align-items: center; gap: 2px; margin-left: 10px;">
                    <button id="btn-scope-to" onclick="event.stopPropagation(); handleScopeTo();" style="display: none; background: transparent; border: none; padding: 4px; cursor: pointer; transition: opacity 0.15s ease;" onmouseover="this.style.opacity='0.7'" onmouseout="this.style.opacity='1'" title="Scope to selected node">
                        <img src="${scopeToIconPath}" style="width: 28px; height: 28px; object-fit: contain;" alt="Scope To" />
                    </button>
                    <button id="btn-submit" 
                            onclick="event.stopPropagation(); handleSubmit();" 
                            style="display: none; background: transparent; border: none; padding: 4px; cursor: pointer; transition: opacity 0.15s ease;" 
                            onmouseover="this.style.opacity='0.7'" 
                            onmouseout="this.style.opacity='1'" 
                            title="Submit shape instructions for epic"
                            data-shape-icon="${submitShapeIconPath}"
                            data-exploration-icon="${submitExploreIconPath}"
                            data-scenarios-icon="${submitScenarioIconPath}"
                            data-tests-icon="${submitTestIconPath}"
                            data-code-icon="${submitCodeIconPath}"
                            data-shape-tooltip="Submit shape instructions for epic"
                            data-exploration-tooltip="Submit exploration instructions for sub-epic"
                            data-scenarios-tooltip="Submit scenarios instructions for story"
                            data-tests-tooltip="Submit tests instructions for story"
                            data-code-tooltip="Submit code instructions for story">
                        <img id="btn-submit-icon" src="${submitShapeIconPath}" style="width: 28px; height: 28px; object-fit: contain;" alt="Submit" />
                    </button>
                </div>
            </div>
        `;
        
        const linksHtml = scopeData.graphLinks && scopeData.graphLinks.length > 0
            ? scopeData.graphLinks.map(link =>
                `<span onclick="openFile('${this.escapeForJs(link.url)}')" style="color: var(--vscode-foreground); text-decoration: underline; margin-left: 6px; font-size: 12px; cursor: pointer;">${this.escapeHtml(link.text).toLowerCase()}</span>`
            ).join('')
            : '';
        
        // Always show story-graph.json and story-map.md links
        const workspaceDir = botData.workspace_directory || '';
        const storyGraphPath = workspaceDir ? `${workspaceDir}/docs/stories/story-graph.json` : '';
        const storyMapPath = workspaceDir ? `${workspaceDir}/docs/stories/story-map/story-map.md` : '';
        
        const permanentLinksHtml = `
            <span onclick="openFile('${this.escapeForJs(storyGraphPath)}')" style="color: var(--vscode-foreground); text-decoration: underline; margin-left: 12px; font-size: 12px; cursor: pointer;" title="Open story-graph.json">story graph</span>
            <span onclick="openFile('${this.escapeForJs(storyMapPath)}')" style="color: var(--vscode-foreground); text-decoration: underline; margin-left: 6px; font-size: 12px; cursor: pointer;" title="Open story-map.md">story map</span>
        `;
        
        // ===== PERFORMANCE: Content rendering =====
        const perfContentStart = performance.now();
        let contentHtml = '';
        let contentSummary = '';
        if ((scopeData.type === 'story' || scopeData.type === 'showAll') && scopeData.content) {
            // content is an object with 'epics' property, not directly an array
            const epics = scopeData.content.epics || [];
            
            const perfRootNodeStart = performance.now();
            const rootNode = this.renderRootNode(actionButtonsHtml);
            const perfRootNodeEnd = performance.now();
            log(`[StoryMapView] [PERF] renderRootNode: ${(perfRootNodeEnd - perfRootNodeStart).toFixed(2)}ms`);
            
            const perfTreeStart = performance.now();
            const treeHtml = this.renderStoryTree(epics, gearIconPath, epicIconPath, pageIconPath, testTubeIconPath, documentIconPath, plusIconPath, subtractIconPath, emptyIconPath);
            const perfTreeEnd = performance.now();
            log(`[StoryMapView] [PERF] renderStoryTree (${epics.length} epics): ${(perfTreeEnd - perfTreeStart).toFixed(2)}ms`);
            
            contentHtml = rootNode + treeHtml;
            contentSummary = `${epics.length} epic${epics.length !== 1 ? 's' : ''}`;
        } else if (scopeData.type === 'files' && scopeData.content) {
            contentHtml = this.renderFileList(scopeData.content);
            contentSummary = `${scopeData.content.length} file${scopeData.content.length !== 1 ? 's' : ''}`;
        } else {
            contentHtml = '<div class="empty-state">All files in workspace</div>';
            contentSummary = 'all files';
        }
        const perfContentEnd = performance.now();
        log(`[StoryMapView] [PERF] Content rendering: ${(perfContentEnd - perfContentStart).toFixed(2)}ms`);
        
        const filterValue = this.escapeHtml(scopeData.filter || '');
        const hasFilter = filterValue.length > 0;
        
        // ===== PERFORMANCE: Final HTML assembly =====
        const perfAssemblyStart = performance.now();
        
        // Build client-side script content using string concatenation (no backticks)
        const clientScript = 
            '        // SaveQueue and handler methods for StoryMapView optimistic updates\n' +
            '        // This runs in the webview context and coordinates with backend StoryGraphAsyncSaveController\n' +
            '        \n' +
            '        (function() {\n' +
            '            /**\n' +
            '             * Manages queued save operations with visual feedback\n' +
            '             * Client-side SaveQueue for StoryMapView - handles DOM updates and coordinates with backend\n' +
            '             * ES5-compatible: using function constructor instead of class\n' +
            '             */\n' +
            '            function SaveQueue(executeCallback, statusCallback) {\n' +
            '                this.queue = [];\n' +
            '                this.executing = false;\n' +
            '                this.executeCallback = executeCallback;\n' +
            '                this.statusCallback = statusCallback;\n' +
            '                this.debounceTimer = null;\n' +
            '            }\n' +
            '                \n' +
            '            /**\n' +
            '             * Add operation to queue and schedule processing\n' +
            '             * @param {Object} operation - {command: string, rollback: function, metadata: object}\n' +
            '             */\n' +
            '            SaveQueue.prototype.enqueue = function(operation) {\n' +
            '                console.log(\'[SaveQueue.enqueue] Operation enqueued:\', operation.metadata || \'unknown\');\n' +
            '                // ES5-compatible: manually copy properties instead of spread operator\n' +
            '                var queuedOp = {\n' +
            '                    command: operation.command,\n' +
            '                    rollback: operation.rollback,\n' +
            '                    metadata: operation.metadata\n' +
            '                };\n' +
            '                queuedOp.timestamp = Date.now();\n' +
            '                this.queue.push(queuedOp);\n' +
            '                \n' +
            '                console.log(\'[SaveQueue.enqueue] Queue length:\', this.queue.length);\n' +
            '                \n' +
            '                // Debounce: wait 500ms after last change before processing\n' +
            '                var self = this;\n' +
            '                if (this.debounceTimer) {\n' +
            '                    clearTimeout(this.debounceTimer);\n' +
            '                }\n' +
            '                \n' +
            '                this.debounceTimer = setTimeout(function() {\n' +
            '                    console.log(\'[SaveQueue.enqueue] Debounce timer fired, processing queue...\');\n' +
            '                    self.processQueue();\n' +
            '                }, 500);\n' +
            '            };\n' +
            '                \n' +
            '            /**\n' +
            '             * Process all queued operations in batch\n' +
            '             * ES5-compatible: using Promise chains instead of async/await\n' +
            '             */\n' +
            '            SaveQueue.prototype.processQueue = function() {\n' +
            '                var self = this;\n' +
            '                console.log(\'[SaveQueue.processQueue] Called - executing=\', this.executing, \'queueLength=\', this.queue.length);\n' +
            '                if (this.executing || this.queue.length === 0) {\n' +
            '                    console.log(\'[SaveQueue.processQueue] Skipping - executing=\', this.executing, \'queueLength=\', this.queue.length);\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
            '                this.executing = true;\n' +
            '                var count = this.queue.length;\n' +
            '                var message = count === 1 ? \'Saving change...\' : \'Saving \' + count + \' changes...\';\n' +
            '                console.log(\'[SaveQueue.processQueue] Calling statusCallback with saving state, message=\', message);\n' +
            '                this.statusCallback(\'saving\', message);\n' +
            '                \n' +
            '                // Update status messages for create operations\n' +
            '                for (var i = 0; i < this.queue.length; i++) {\n' +
            '                    var op = this.queue[i];\n' +
            '                    if (op.metadata && op.metadata.operation === \'create\' && op.metadata.tempNodeId) {\n' +
            '                        var statusEl = document.getElementById(op.metadata.tempNodeId + \'-status\');\n' +
            '                        if (statusEl) {\n' +
            '                            // Get the actual node name from the DOM\n' +
            '                            var nodeEl = document.getElementById(op.metadata.tempNodeId);\n' +
            '                            var nodeName = \'node\';\n' +
            '                            if (nodeEl) {\n' +
            '                                var nodeSpan = nodeEl.querySelector(\'.story-node\');\n' +
            '                                if (nodeSpan) {\n' +
            '                                    nodeName = nodeSpan.getAttribute(\'data-node-name\') || nodeSpan.textContent;\n' +
            '                                }\n' +
            '                            }\n' +
            '                            statusEl.textContent = \'Saving \' + nodeName + \'...\';\n' +
            '                        }\n' +
            '                    }\n' +
            '                }\n' +
            '                \n' +
            '                // Take snapshot of current queue (ES5-compatible: use slice instead of spread)\n' +
            '                var batch = this.queue.slice();\n' +
            '                this.queue = [];\n' +
            '                \n' +
            '                var results = {\n' +
            '                    success: [],\n' +
            '                    failed: []\n' +
            '                };\n' +
            '                \n' +
            '                // Execute all operations sequentially using Promise chain\n' +
            '                var executeNext = function(index) {\n' +
            '                    if (index >= batch.length) {\n' +
            '                        // All operations completed\n' +
            '                        if (results.failed.length === 0) {\n' +
            '                            // All succeeded - handle post-save updates\n' +
            '                            for (var i = 0; i < results.success.length; i++) {\n' +
            '                                var op = results.success[i];\n' +
            '                                if (op.metadata && op.metadata.operation === \'create\' && op.metadata.tempNodeId) {\n' +
            '                                    // Remove status messages for create operations\n' +
            '                                    var statusEl = document.getElementById(op.metadata.tempNodeId + \'-status\');\n' +
            '                                    if (statusEl) {\n' +
            '                                        statusEl.remove();\n' +
            '                                    }\n' +
            '                                    // IMPORTANT: Keep the temporary node in the DOM - it becomes the permanent node\n' +
            '                                    // The node should stay visible after save completes\n' +
            '                                    // Since optimistic operations skip panel refresh, the node will persist\n' +
            '                                    var tempNode = document.getElementById(op.metadata.tempNodeId);\n' +
            '                                    if (tempNode) {\n' +
            '                                        console.log(\'[SaveQueue.processQueue] Create operation succeeded - keeping temporary node:\', op.metadata.tempNodeId);\n' +
            '                                        // Ensure the node stays visible - mark it as saved so it won\'t be removed\n' +
            '                                        tempNode.setAttribute(\'data-saved\', \'true\');\n' +
            '                                        // The node will remain in the DOM and be replaced by the real node\n' +
            '                                        // when the panel next refreshes (which won\'t happen for optimistic operations)\n' +
            '                                    } else {\n' +
            '                                        console.error(\'[SaveQueue.processQueue] CRITICAL: Temporary node disappeared after successful save:\', op.metadata.tempNodeId);\n' +
            '                                        console.error(\'[SaveQueue.processQueue] This should not happen - the node should persist after save\');\n' +
            '                                    }\n' +
            '                                } else if (op.metadata && op.metadata.operation === \'rename\') {\n' +
            '                                    // Remove status message for rename operations\n' +
            '                                    if (op.metadata.statusId) {\n' +
            '                                        var renameStatusEl = document.getElementById(op.metadata.statusId);\n' +
            '                                        if (renameStatusEl) {\n' +
            '                                            renameStatusEl.remove();\n' +
            '                                        }\n' +
            '                                    }\n' +
            '                                    // Update data-path attributes after successful rename\n' +
            '                                    // This ensures child nodes can be found and renamed correctly\n' +
            '                                    updatePathAfterRename(op.metadata.path, op.metadata.oldName, op.metadata.newName);\n' +
            '                                } else if (op.metadata && op.metadata.operation === \'delete\') {\n' +
            '                                    // Remove status message for delete operations\n' +
            '                                    if (op.metadata.statusId) {\n' +
            '                                        var deleteStatusEl = document.getElementById(op.metadata.statusId);\n' +
            '                                        if (deleteStatusEl) {\n' +
            '                                            deleteStatusEl.remove();\n' +
            '                                        }\n' +
            '                                    }\n' +
            '                                } else if (op.metadata && op.metadata.operation === \'move\') {\n' +
            '                                    // Remove status message for move operations\n' +
            '                                    if (op.metadata.statusId) {\n' +
            '                                        var moveStatusEl = document.getElementById(op.metadata.statusId);\n' +
            '                                        if (moveStatusEl) {\n' +
            '                                            moveStatusEl.remove();\n' +
            '                                        }\n' +
            '                                    }\n' +
            '                                }\n' +
            '                            }\n' +
            '                            \n' +
            '                            self.statusCallback(\'success\', \'Saved\');\n' +
            '                            \n' +
            '                            // Auto-hide after 2 seconds\n' +
            '                            setTimeout(function() {\n' +
            '                                self.statusCallback(\'hidden\', \'\');\n' +
            '                            }, 2000);\n' +
            '                        } else {\n' +
            '                            // Some failed - rollback and show error\n' +
            '                            var failedCount = results.failed.length;\n' +
            '                            var errorMsg = failedCount === 1 \n' +
            '                                ? \'Save failed - click for details\'\n' +
            '                                : failedCount + \' saves failed - click for details\';\n' +
            '                            \n' +
            '                            var firstError = results.failed[0].error;\n' +
            '                            self.statusCallback(\'error\', errorMsg, firstError);\n' +
            '                            \n' +
            '                            // Update status messages for failed operations\n' +
            '                            for (var i = 0; i < results.failed.length; i++) {\n' +
            '                                var failed = results.failed[i];\n' +
            '                                if (failed.op.metadata && failed.op.metadata.operation === \'create\' && failed.op.metadata.tempNodeId) {\n' +
            '                                    var statusEl = document.getElementById(failed.op.metadata.tempNodeId + \'-status\');\n' +
            '                                    if (statusEl) {\n' +
            '                                        statusEl.textContent = \'Failed to save\';\n' +
            '                                        statusEl.style.color = \'#c62828\';\n' +
            '                                    }\n' +
            '                                } else if (failed.op.metadata && failed.op.metadata.operation === \'delete\' && failed.op.metadata.statusId) {\n' +
            '                                    // For delete: update status message to show failure\n' +
            '                                    var deleteStatusEl = document.getElementById(failed.op.metadata.statusId);\n' +
            '                                    if (deleteStatusEl) {\n' +
            '                                        deleteStatusEl.textContent = \'Failed to delete\';\n' +
            '                                        deleteStatusEl.style.color = \'#c62828\';\n' +
            '                                    }\n' +
            '                                } else if (failed.op.metadata && failed.op.metadata.operation === \'move\' && failed.op.metadata.statusId) {\n' +
            '                                    // For move: update status message to show failure\n' +
            '                                    var moveStatusEl = document.getElementById(failed.op.metadata.statusId);\n' +
            '                                    if (moveStatusEl) {\n' +
            '                                        moveStatusEl.textContent = \'Failed to move\';\n' +
            '                                        moveStatusEl.style.color = \'#c62828\';\n' +
            '                                    }\n' +
            '                                }\n' +
            '                            }\n' +
            '                            \n' +
            '                            // Rollback failed operations (ES5-compatible: use traditional for loop)\n' +
            '                            for (var i = 0; i < results.failed.length; i++) {\n' +
            '                                var failed = results.failed[i];\n' +
            '                                if (failed.op.rollback) {\n' +
            '                                    try {\n' +
            '                                        failed.op.rollback();\n' +
            '                                    } catch (rollbackError) {\n' +
            '                                        console.error(\'Rollback failed:\', rollbackError);\n' +
            '                                    }\n' +
            '                                }\n' +
            '                            }\n' +
            '                        }\n' +
            '                        \n' +
            '                        self.executing = false;\n' +
            '                        \n' +
            '                        // Process remaining queue if new items added during execution\n' +
            '                        if (self.queue.length > 0) {\n' +
            '                            setTimeout(function() {\n' +
            '                                self.processQueue();\n' +
            '                            }, 500);\n' +
            '                        }\n' +
            '                        return;\n' +
            '                    }\n' +
            '                    \n' +
            '                    var op = batch[index];\n' +
            '                    console.log(\'[SaveQueue.processQueue] Calling executeCallback for command:\', op.command);\n' +
            '                    var promise = self.executeCallback(op.command);\n' +
            '                    console.log(\'[SaveQueue.processQueue] executeCallback returned promise:\', typeof promise, promise && typeof promise.then === \'function\' ? \'Promise\' : \'not a Promise\');\n' +
            '                    if (promise && typeof promise.then === \'function\') {\n' +
            '                        promise.then(function(result) {\n' +
            '                            console.log(\'[SaveQueue.processQueue] Promise resolved for command:\', op.command, \'result:\', result);\n' +
            '                            results.success.push(op);\n' +
            '                            executeNext(index + 1);\n' +
            '                        }).catch(function(error) {\n' +
            '                            console.error(\'[SaveQueue.processQueue] Promise rejected for command:\', op.command, \'error:\', error);\n' +
            '                            results.failed.push({ op: op, error: error });\n' +
            '                            executeNext(index + 1);\n' +
            '                        });\n' +
            '                    } else {\n' +
            '                        // Synchronous callback\n' +
            '                        try {\n' +
            '                            promise;\n' +
            '                            results.success.push(op);\n' +
            '                        } catch (error) {\n' +
            '                            results.failed.push({ op: op, error: error });\n' +
            '                        }\n' +
            '                        executeNext(index + 1);\n' +
            '                    }\n' +
            '                };\n' +
            '                \n' +
            '                try {\n' +
            '                    executeNext(0);\n' +
            '                } catch (error) {\n' +
            '                    // Critical error - rollback everything (ES5-compatible: use traditional for loop)\n' +
            '                    this.statusCallback(\'error\', \'Save failed - click for details\', error);\n' +
            '                    \n' +
            '                    for (var i = 0; i < batch.length; i++) {\n' +
            '                        var op = batch[i];\n' +
            '                        if (op.rollback) {\n' +
            '                            try {\n' +
            '                                op.rollback();\n' +
            '                            } catch (rollbackError) {\n' +
            '                                console.error(\'Rollback failed:\', rollbackError);\n' +
            '                            }\n' +
            '                        }\n' +
            '                    }\n' +
            '                    \n' +
            '                    this.executing = false;\n' +
            '                }\n' +
            '            };\n' +
            '                \n' +
            '            /**\n' +
            '             * Update the status indicator UI\n' +
            '             * @param {string} state - \'saving\' | \'success\' | \'error\' | \'hidden\'\n' +
            '             * @param {string} message - Display message\n' +
            '             * @param {Error} error - Error object (for error state)\n' +
            '             * ES5-compatible: no default parameters\n' +
            '             */\n' +
            '            SaveQueue.prototype.updateStatus = function(state, message, error) {\n' +
            '                try {\n' +
            '                    if (error === undefined) error = null;\n' +
            '                    \n' +
            '                    console.log(\'[SaveQueue.updateStatus] Called with state=\', state, \'message=\', message);\n' +
            '                    \n' +
            '                    var indicator = document.getElementById(\'save-status-indicator\');\n' +
            '                    if (!indicator) {\n' +
            '                        console.warn(\'[SaveQueue.updateStatus] save-status-indicator element not found in DOM - status indicator may not be rendered yet\');\n' +
            '                        return;\n' +
            '                    }\n' +
            '                    \n' +
            '                    // Use IDs that match bot_header_view.js structure\n' +
            '                    var spinner = document.getElementById(\'save-status-spinner\');\n' +
            '                    var msg = document.getElementById(\'save-status-message\');\n' +
            '                    \n' +
            '                    if (!spinner || !msg) {\n' +
            '                        console.warn(\'[SaveQueue.updateStatus] Missing spinner or message element! spinner=\', !!spinner, \'msg=\', !!msg, \' - status indicator may not be fully rendered\');\n' +
            '                        return;\n' +
            '                    }\n' +
            '                    \n' +
            '                    console.log(\'[SaveQueue.updateStatus] Updating indicator - state=\', state, \'message=\', message);\n' +
            '                    \n' +
            '                    if (state === \'hidden\') {\n' +
            '                        indicator.style.display = \'none\';\n' +
            '                        indicator.onclick = null;\n' +
            '                        return;\n' +
            '                    }\n' +
            '                    \n' +
            '                    indicator.style.display = \'flex\';\n' +
            '                    // Update classes - keep main-header-status, add state class\n' +
            '                    indicator.className = \'main-header-status save-status \' + state;\n' +
            '                    \n' +
            '                    // Update spinner visibility and message\n' +
            '                    if (state === \'saving\') {\n' +
            '                        spinner.style.display = \'inline-block\';\n' +
            '                        msg.textContent = message || \'Saving...\';\n' +
            '                    } else if (state === \'success\') {\n' +
            '                        spinner.style.display = \'none\';\n' +
            '                        msg.textContent = (message || \'Saved\') + \' ✓\';\n' +
            '                        // Auto-hide after 2 seconds\n' +
            '                        setTimeout(function() {\n' +
            '                            try {\n' +
            '                                var ind = document.getElementById(\'save-status-indicator\');\n' +
            '                                if (ind && ind.className.indexOf(\'success\') !== -1) {\n' +
            '                                    ind.style.display = \'none\';\n' +
            '                                }\n' +
            '                            } catch (e) {\n' +
            '                                console.warn(\'[SaveQueue.updateStatus] Error in auto-hide timeout:\', e);\n' +
            '                            }\n' +
            '                        }, 2000);\n' +
            '                    } else if (state === \'error\') {\n' +
            '                        spinner.style.display = \'none\';\n' +
            '                        msg.textContent = (message || \'Save failed\') + \' ✗\';\n' +
            '                        \n' +
            '                        // Make clickable to show error details (ES5-compatible: use function instead of arrow)\n' +
            '                        indicator.onclick = function() {\n' +
            '                            try {\n' +
            '                                var errorDetails = error \n' +
            '                                    ? (error.message + \'\\\\n\\\\n\' + (error.stack || \'\'))\n' +
            '                                    : \'Unknown error occurred\';\n' +
            '                                \n' +
            '                                // Send to extension host to show error dialog\n' +
            '                                if (typeof vscode !== \'undefined\') {\n' +
            '                                    vscode.postMessage({\n' +
            '                                        type: \'showErrorDialog\',\n' +
            '                                        title: \'Save Failed\',\n' +
            '                                        message: errorDetails\n' +
            '                                    });\n' +
            '                                }\n' +
            '                            } catch (e) {\n' +
            '                                console.error(\'[SaveQueue.updateStatus] Error in error click handler:\', e);\n' +
            '                            }\n' +
            '                        };\n' +
            '                    }\n' +
            '                } catch (e) {\n' +
            '                    console.error(\'[SaveQueue.updateStatus] Error updating status indicator:\', e);\n' +
            '                    // Don\'t throw - prevent breaking the panel\n' +
            '                }\n' +
            '            };\n' +
            '            \n' +
            '            // Initialize SaveQueue instance for StoryMapView\n' +
            '            // Execute callback sends commands to backend via postMessage\n' +
            '            // Status callback updates DOM status indicator directly\n' +
            '            // NOTE: vscode may not be available immediately, so we use a retry mechanism\n' +
            '            function initializeSaveQueue() {\n' +
            '                // Use the global vscode instance that was already acquired in bot_panel.js\n' +
            '                // DO NOT call acquireVsCodeApi() again - it can only be called once!\n' +
            '                var vscodeApi = typeof vscode !== \'undefined\' ? vscode : null;\n' +
            '                \n' +
            '                if (!vscodeApi) {\n' +
            '                    // vscode not ready yet - retry after a short delay\n' +
            '                    console.log(\'[SaveQueue Init] vscode not available yet, retrying in 100ms...\');\n' +
            '                    setTimeout(initializeSaveQueue, 100);\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
            '                console.log(\'[SaveQueue Init] vscode is available, creating SaveQueue instance...\');\n' +
            '                window.storyMapSaveQueue = new SaveQueue(\n' +
            '                    function(cmd) {\n' +
            '                        return new Promise(function(resolve, reject) {\n' +
            '                            console.log(\'[SaveQueue.executeCallback] Sending command:\', cmd);\n' +
            '                            \n' +
            '                            // Add timeout to detect if Promise never resolves\n' +
            '                            var timeoutId = setTimeout(function() {\n' +
            '                                console.error(\'[SaveQueue.executeCallback] TIMEOUT: Promise never resolved for command:\', cmd);\n' +
            '                                window.removeEventListener(\'message\', messageListener);\n' +
            '                                reject(new Error(\'Save operation timed out after 10 seconds\'));\n' +
            '                            }, 10000);\n' +
            '                            \n' +
            '                            vscodeApi.postMessage({\n' +
            '                                command: \'executeCommand\',\n' +
            '                                commandText: cmd,\n' +
            '                                optimistic: true\n' +
            '                            });\n' +
            '                            \n' +
            '                            // Listen for save completion message (ES5-compatible: use function instead of arrow, var instead of const)\n' +
            '                            var messageListener = function(event) {\n' +
            '                                var message = event.data;\n' +
            '                                console.log(\'[SaveQueue.executeCallback] Received message:\', message.command, \'for command:\', cmd);\n' +
            '                                if (message.command === \'saveCompleted\') {\n' +
            '                                    console.log(\'[SaveQueue.executeCallback] saveCompleted received, removing listener and resolving Promise\');\n' +
            '                                    clearTimeout(timeoutId);\n' +
            '                                    window.removeEventListener(\'message\', messageListener);\n' +
            '                                    if (message.success) {\n' +
            '                                        console.log(\'[SaveQueue.executeCallback] Resolving Promise with success, result:\', message.result);\n' +
            '                                        resolve(message.result);\n' +
            '                                    } else {\n' +
            '                                        console.error(\'[SaveQueue.executeCallback] Rejecting Promise with error:\', message.error);\n' +
            '                                        reject(new Error(message.error || \'Save failed\'));\n' +
            '                                    }\n' +
            '                                }\n' +
            '                            };\n' +
            '                            window.addEventListener(\'message\', messageListener);\n' +
            '                            console.log(\'[SaveQueue.executeCallback] Message listener added for command:\', cmd);\n' +
            '                        });\n' +
            '                    },\n' +
                    '                    function(state, msg, err) {\n' +
                    '                        try {\n' +
                    '                            console.log(\'[SaveQueue.statusCallback] Called with state=\', state, \'msg=\', msg);\n' +
                    '                            // Directly call updateStatus to update the DOM (don\'t recurse!)\n' +
                    '                            if (window.storyMapSaveQueue && typeof window.storyMapSaveQueue.updateStatus === \'function\') {\n' +
                    '                                window.storyMapSaveQueue.updateStatus(state, msg, err);\n' +
                    '                            } else {\n' +
                    '                                console.warn(\'[SaveQueue.statusCallback] storyMapSaveQueue or updateStatus not available!\');\n' +
                    '                            }\n' +
                    '                        } catch (e) {\n' +
                    '                            console.error(\'[SaveQueue.statusCallback] Error in status callback:\', e);\n' +
                    '                            // Don\'t throw - prevent breaking the panel\n' +
                    '                        }\n' +
                    '                    }\n' +
            '                );\n' +
            '                console.log(\'[SaveQueue Init] SaveQueue instance created successfully, typeof window.storyMapSaveQueue:\', typeof window.storyMapSaveQueue);\n' +
            '            }\n' +
            '            \n' +
            '            // Start initialization (will retry if vscode not ready)\n' +
            '            initializeSaveQueue();\n' +
            '            \n' +
            '            /**\n' +
            '             * StoryMapView handler methods - handle optimistic updates for move/rename/delete operations\n' +
            '             */\n' +
            '            \n' +
            '            /**\n' +
            '             * Find DOM element by node path\n' +
            '             * @param {string} nodePath - e.g., "story_graph.\\"Epic1\\".\\"SubEpic1\\".\\"Story1\\""\n' +
            '             * @returns {HTMLElement|null}\n' +
            '             */\n' +
            '            function findNodeElement(nodePath) {\n' +
            '                console.log(\'[findNodeElement] Looking for node with path:\', nodePath);\n' +
            '                // Handle paths with quotes - need to search iteratively (ES5-compatible: use var)\n' +
            '                var allNodes = document.querySelectorAll(\'.story-node, [data-path]\');\n' +
            '                console.log(\'[findNodeElement] Found\', allNodes.length, \'nodes with data-path or story-node class\');\n' +
            '                for (var i = 0; i < allNodes.length; i++) {\n' +
            '                    var node = allNodes[i];\n' +
            '                    var nodePathAttr = node.getAttribute(\'data-path\');\n' +
            '                    if (nodePathAttr === nodePath) {\n' +
            '                        console.log(\'[findNodeElement] Found matching node at index\', i, \'node:\', node, \'tagName:\', node.tagName);\n' +
            '                        return node;\n' +
            '                    }\n' +
            '                }\n' +
            '                console.warn(\'[findNodeElement] No node found with path:\', nodePath);\n' +
            '                // Debug: log first few paths to help diagnose\n' +
            '                for (var j = 0; j < Math.min(allNodes.length, 5); j++) {\n' +
            '                    console.log(\'[findNodeElement] Sample node\', j, \'path:\', allNodes[j].getAttribute(\'data-path\'), \'type:\', allNodes[j].getAttribute(\'data-node-type\'));\n' +
            '                }\n' +
            '                return null;\n' +
            '            }\n' +
            '            \n' +
            '            /**\n' +
            '             * Find the wrapper div for a story-node span\n' +
            '             * Story nodes are <span> elements wrapped in <div> containers\n' +
            '             * @param {HTMLElement} storyNodeSpan - The <span> element with class story-node\n' +
            '             * @returns {HTMLElement} The wrapper <div> or the span itself if no wrapper found\n' +
            '             */\n' +
            '            function findNodeWrapper(storyNodeSpan) {\n' +
            '                if (!storyNodeSpan) return null;\n' +
            '                \n' +
            '                // Walk up the DOM tree to find the wrapper div\n' +
            '                // The wrapper is typically a direct parent <div> that contains the story-node\n' +
            '                var current = storyNodeSpan.parentElement;\n' +
            '                \n' +
            '                while (current && current !== document.body) {\n' +
            '                    // Stop if we hit a collapsible-content container (that\'s the parent of all nodes)\n' +
            '                    if (current.classList && current.classList.contains(\'collapsible-content\')) {\n' +
            '                        break;\n' +
            '                    }\n' +
            '                    \n' +
            '                    // Check if current is a div element and contains our story-node\n' +
            '                    // This avoids using querySelector with data-path (which breaks with quotes)\n' +
            '                    if (current.tagName && current.tagName.toLowerCase() === \'div\' && current.contains && current.contains(storyNodeSpan)) {\n' +
            '                        // Check if this div directly contains the story-node or has it as a descendant\n' +
            '                        // The wrapper div should contain exactly one story-node with our data-path\n' +
            '                        var hasStoryNode = false;\n' +
            '                        var storyNodes = current.querySelectorAll ? current.querySelectorAll(\'.story-node\') : [];\n' +
            '                        for (var i = 0; i < storyNodes.length; i++) {\n' +
            '                            if (storyNodes[i] === storyNodeSpan) {\n' +
            '                                hasStoryNode = true;\n' +
            '                                break;\n' +
            '                            }\n' +
            '                        }\n' +
            '                        if (hasStoryNode) {\n' +
            '                            // Found the wrapper div that contains our story-node\n' +
            '                            return current;\n' +
            '                        }\n' +
            '                    }\n' +
            '                    current = current.parentElement;\n' +
            '                }\n' +
            '                \n' +
            '                // If no wrapper found, return the span itself\n' +
            '                return storyNodeSpan;\n' +
            '            }\n' +
            '            \n' +
            '            /**\n' +
            '             * Pure DOM manipulation for moving nodes\n' +
            '             * @param {HTMLElement} sourceNode - Node to move\n' +
            '             * @param {HTMLElement} targetParent - Parent container to move into\n' +
            '             * @param {number} position - Position index (used when targetNode is not provided)\n' +
            '             * @param {HTMLElement} targetNode - Optional: specific node to insert after (for "after" dropZone)\n' +
            '             */\n' +
            '            /**\n' +
            '             * Recalculate margin-left for a node and all its children based on new parent depth\n' +
            '             * Uses the EXACT same formula as backend: marginLeft = 7 + (depth * 7)\n' +
            '             * @param {HTMLElement} nodeWrapper - The wrapper div containing the node\n' +
            '             * @param {HTMLElement} newParent - The new parent node element\n' +
            '             */\n' +
            '            function recalculateMarginLeftForMovedNode(nodeWrapper, newParent) {\n' +
            '                if (!nodeWrapper || !newParent) {\n' +
            '                    console.warn(\'[recalculateMarginLeftForMovedNode] Missing nodeWrapper or newParent\');\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
            '                // Find the story-node span inside the wrapper\n' +
            '                var storyNode = nodeWrapper.querySelector ? nodeWrapper.querySelector(\'.story-node\') : null;\n' +
            '                if (!storyNode) {\n' +
            '                    console.warn(\'[recalculateMarginLeftForMovedNode] Cannot find story-node in wrapper\');\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
            '                var nodeType = storyNode.getAttribute ? storyNode.getAttribute(\'data-node-type\') : null;\n' +
            '                if (!nodeType) {\n' +
            '                    console.warn(\'[recalculateMarginLeftForMovedNode] Cannot determine node type\');\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
            '                // Epics always have margin-left 0\n' +
            '                if (nodeType === \'epic\') {\n' +
            '                    nodeWrapper.style.marginLeft = \'0px\';\n' +
            '                    console.log(\'[recalculateMarginLeftForMovedNode] Epic node, set margin-left to 0px\');\n' +
            '                    // Still need to update children\n' +
            '                } else {\n' +
            '                    // Calculate margin-left based on new parent\'s depth\n' +
            '                    var marginLeft = 0;\n' +
            '                    \n' +
            '                    // First: try to copy from an existing sibling of the same type\n' +
            '                    var parentContainer = nodeWrapper.parentElement;\n' +
            '                    if (parentContainer) {\n' +
            '                        var containerChildren = Array.prototype.slice.call(parentContainer.children);\n' +
            '                        for (var i = 0; i < containerChildren.length; i++) {\n' +
            '                            var sibling = containerChildren[i];\n' +
            '                            if (sibling === nodeWrapper) continue; // Skip self\n' +
            '                            var siblingNode = sibling.querySelector ? sibling.querySelector(\'.story-node[data-node-type="\' + nodeType + \'"]\') : null;\n' +
            '                            if (siblingNode) {\n' +
            '                                if (sibling.style && sibling.style.marginLeft) {\n' +
            '                                    var siblingMargin = sibling.style.marginLeft;\n' +
            '                                    var marginMatch = siblingMargin.match(/(\\d+)px/);\n' +
            '                                    if (marginMatch) {\n' +
            '                                        marginLeft = parseInt(marginMatch[1], 10);\n' +
            '                                        console.log(\'[recalculateMarginLeftForMovedNode] Copied margin-left from sibling:\', marginLeft, \'px\');\n' +
            '                                        break;\n' +
            '                                    }\n' +
            '                                }\n' +
            '                            }\n' +
            '                        }\n' +
            '                    }\n' +
            '                    \n' +
            '                    // Fallback: calculate using backend formula if no sibling found\n' +
            '                    if (!marginLeft) {\n' +
            '                        var newParentWrapper = findNodeWrapper(newParent);\n' +
            '                        var parentMarginLeft = 0;\n' +
            '                        \n' +
            '                        if (newParentWrapper && newParentWrapper.style && newParentWrapper.style.marginLeft) {\n' +
            '                            var parentMargin = newParentWrapper.style.marginLeft;\n' +
            '                            var parentMatch = parentMargin.match(/(\\d+)px/);\n' +
            '                            if (parentMatch) {\n' +
            '                                parentMarginLeft = parseInt(parentMatch[1], 10);\n' +
            '                            }\n' +
            '                        }\n' +
            '                        \n' +
            '                        if (nodeType === \'sub-epic\') {\n' +
            '                            // Backend formula: marginLeft = 7 + (depth * 7)\n' +
            '                            // Calculate depth from parent\'s margin-left\n' +
            '                            // parentMarginLeft = 7 + (parentDepth * 7)\n' +
            '                            // So: parentDepth = (parentMarginLeft - 7) / 7\n' +
            '                            var parentDepth = parentMarginLeft >= 7 ? (parentMarginLeft - 7) / 7 : 0;\n' +
            '                            var depth = parentDepth + 1;\n' +
            '                            marginLeft = 7 + (depth * 7);\n' +
            '                            console.log(\'[recalculateMarginLeftForMovedNode] Calculated depth:\', depth, \'marginLeft:\', marginLeft, \'px (backend formula: 7 + (depth * 7))\');\n' +
            '                        } else {\n' +
            '                            // For stories/scenarios: use parent\'s margin + 7\n' +
            '                            marginLeft = parentMarginLeft + 7;\n' +
            '                            console.log(\'[recalculateMarginLeftForMovedNode] Story/scenario, marginLeft:\', marginLeft, \'px (parent + 7)\');\n' +
            '                        }\n' +
            '                    }\n' +
            '                    \n' +
            '                    nodeWrapper.style.marginLeft = marginLeft + \'px\';\n' +
            '                }\n' +
            '                \n' +
            '                // Recursively update all children\n' +
            '                var collapsibleContent = nodeWrapper.querySelector ? nodeWrapper.querySelector(\'.collapsible-content\') : null;\n' +
            '                if (collapsibleContent) {\n' +
            '                    var childWrappers = collapsibleContent.querySelectorAll ? collapsibleContent.querySelectorAll(\'> div\') : [];\n' +
            '                    for (var j = 0; j < childWrappers.length; j++) {\n' +
            '                        var childWrapper = childWrappers[j];\n' +
            '                        var childStoryNode = childWrapper.querySelector ? childWrapper.querySelector(\'.story-node\') : null;\n' +
            '                        if (childStoryNode) {\n' +
            '                            // Recursively recalculate for this child (using moved node as its new parent)\n' +
            '                            recalculateMarginLeftForMovedNode(childWrapper, storyNode);\n' +
            '                        }\n' +
            '                    }\n' +
            '                }\n' +
            '            }\n' +
            '            \n' +
            '            function moveNodeInDOM(sourceNode, targetParent, position, targetNode) {\n' +
            '                console.log(\'[moveNodeInDOM] Called - sourceNode:\', sourceNode, \'targetParent:\', targetParent, \'targetNode:\', targetNode);\n' +
            '                \n' +
            '                // Story nodes are <span> elements wrapped in <div> containers\n' +
            '                // We need to move the wrapper <div>, not just the <span>\n' +
            '                var nodeToMove = findNodeWrapper(sourceNode);\n' +
            '                console.log(\'[moveNodeInDOM] Node to move:\', nodeToMove, \'isWrapper:\', nodeToMove !== sourceNode);\n' +
            '                \n' +
            '                if (!nodeToMove) {\n' +
            '                    console.error(\'[moveNodeInDOM] Cannot find wrapper for sourceNode\');\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
            '                // Remove from current position\n' +
            '                if (nodeToMove.parentElement) {\n' +
            '                    nodeToMove.parentElement.removeChild(nodeToMove);\n' +
            '                }\n' +
            '                \n' +
            '                // If targetNode is provided (dropZone === "after"), insert right after it\n' +
            '                if (targetNode && targetNode.parentElement) {\n' +
            '                    // Find the wrapper div for targetNode\n' +
            '                    var targetNodeToUse = findNodeWrapper(targetNode);\n' +
            '                    \n' +
            '                    if (!targetNodeToUse) {\n' +
            '                        console.error(\'[moveNodeInDOM] Cannot find wrapper for targetNode\');\n' +
            '                        return;\n' +
            '                    }\n' +
            '                    \n' +
            '                    // Find the parent container (should be collapsible-content)\n' +
            '                    var targetParentContainer = targetNodeToUse.parentElement;\n' +
            '                    \n' +
            '                    if (!targetParentContainer) {\n' +
            '                        console.error(\'[moveNodeInDOM] targetNodeToUse has no parent\');\n' +
            '                        return;\n' +
            '                    }\n' +
            '                    \n' +
            '                    // Find the next sibling of targetNodeToUse\n' +
            '                    var nextSibling = targetNodeToUse.nextSibling;\n' +
            '                    \n' +
            '                    // Skip text nodes and whitespace\n' +
            '                    while (nextSibling && nextSibling.nodeType !== 1) {\n' +
            '                        nextSibling = nextSibling.nextSibling;\n' +
            '                    }\n' +
            '                    \n' +
            '                    console.log(\'[moveNodeInDOM] Inserting after targetNodeToUse, nextSibling:\', nextSibling, \'parent:\', targetParentContainer);\n' +
            '                    \n' +
            '                    if (nextSibling) {\n' +
            '                        targetParentContainer.insertBefore(nodeToMove, nextSibling);\n' +
            '                    } else {\n' +
            '                        // targetNode is the last child, append to end\n' +
            '                        targetParentContainer.appendChild(nodeToMove);\n' +
            '                    }\n' +
            '                    console.log(\'[moveNodeInDOM] Node moved successfully after target\');\n' +
            '                    \n' +
            '                    // Recalculate margin-left for moved node and all its children based on new parent depth\n' +
            '                    recalculateMarginLeftForMovedNode(nodeToMove, targetParent);\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
                '                // Fallback: use position-based insertion (for "inside" dropZone)\n' +
                '                // Find the collapsible-content container that holds child nodes\n' +
                '                var targetContainer = null;\n' +
                '                \n' +
                '                // If targetParent is a story-node, find its collapsible-content child\n' +
                '                if (targetParent.classList && targetParent.classList.contains(\'story-node\')) {\n' +
                '                    // Use the same logic as create operations: find wrapper, then find collapsible-content\n' +
                '                    var targetParentWrapper = findNodeWrapper(targetParent);\n' +
                '                    if (targetParentWrapper) {\n' +
                '                        // Look for collapsible-content as next sibling of wrapper\n' +
                '                        var nextSibling = targetParentWrapper.nextSibling;\n' +
                '                        while (nextSibling) {\n' +
                '                            if (nextSibling.nodeType === 1 && nextSibling.classList && nextSibling.classList.contains(\'collapsible-content\')) {\n' +
                '                                targetContainer = nextSibling;\n' +
                '                                break;\n' +
                '                            }\n' +
                '                            nextSibling = nextSibling.nextSibling;\n' +
                '                        }\n' +
                '                        // If not found as sibling, check if wrapper contains it\n' +
                '                        if (!targetContainer) {\n' +
                '                            targetContainer = targetParentWrapper.querySelector ? targetParentWrapper.querySelector(\'.collapsible-content\') : null;\n' +
                '                        }\n' +
                '                    }\n' +
                '                } else if (targetParent.classList && targetParent.classList.contains(\'collapsible-content\')) {\n' +
                '                    // Already the right container\n' +
                '                    targetContainer = targetParent;\n' +
                '                } else {\n' +
                '                    // Search for collapsible-content in children\n' +
                '                    targetContainer = targetParent.querySelector ? targetParent.querySelector(\'.collapsible-content\') : null;\n' +
                '                    if (!targetContainer) {\n' +
                '                        targetContainer = targetParent;\n' +
                '                    }\n' +
                '                }\n' +
                '                \n' +
                '                if (!targetContainer) {\n' +
                '                    console.error(\'[moveNodeInDOM] Cannot find target container\');\n' +
                '                    return;\n' +
                '                }\n' +
                '                \n' +
                '                console.log(\'[moveNodeInDOM] Using targetContainer:\', targetContainer);\n' +
                '                \n' +
                '                // Insert at new position (ES5-compatible: use slice instead of Array.from)\n' +
                '                var targetChildren = Array.prototype.slice.call(targetContainer.children);\n' +
                '                // Filter to only div wrappers (skip other elements)\n' +
                '                var wrapperChildren = targetChildren.filter(function(child) {\n' +
                '                    return child.nodeType === 1 && (child.querySelector && child.querySelector(\'.story-node\') || child.classList && child.classList.contains(\'story-node\'));\n' +
                '                });\n' +
                '                \n' +
                '                console.log(\'[moveNodeInDOM] targetChildren.length:\', targetChildren.length, \'wrapperChildren.length:\', wrapperChildren.length, \'position:\', position);\n' +
                '                \n' +
                '                if (position >= wrapperChildren.length) {\n' +
                '                    targetContainer.appendChild(nodeToMove);\n' +
                '                } else {\n' +
                '                    targetContainer.insertBefore(nodeToMove, wrapperChildren[position]);\n' +
                '                }\n' +
                '                console.log(\'[moveNodeInDOM] Node moved successfully at position\');\n' +
                '                \n' +
                '                // Recalculate margin-left for moved node and all its children based on new parent depth\n' +
                '                recalculateMarginLeftForMovedNode(nodeToMove, targetParent);\n' +
            '            }\n' +
            '            \n' +
            '            /**\n' +
            '             * Build Python command for move operation\n' +
            '             * @param {string} sourceNodePath - Full path like "story_graph.\\"Epic\\".\\"SubEpic\\""\n' +
            '             * @param {string} targetParentPath - Full path to target parent\n' +
            '             * @param {number} position - Target position\n' +
            '             * @returns {string} Command string\n' +
            '             */\n' +
            '            function buildMoveCommand(sourceNodePath, targetParentPath, position) {\n' +
            '                // Extract target name from targetParentPath\n' +
            '                // targetParentPath is like: story_graph."Epic1"."SubEpic1"\n' +
            '                // We need: story_graph."Epic1"."SubEpic1".move_to target:"SubEpic1" at_position:1\n' +
            '                // ES5-compatible: use var\n' +
            '                var targetMatch = targetParentPath.match(/"([^"]+)"/g);\n' +
            '                var targetName = targetMatch && targetMatch.length > 0 \n' +
            '                    ? targetMatch[targetMatch.length - 1].replace(/"/g, \'\')\n' +
            '                    : \'\';\n' +
            '                \n' +
            '                // Build command using the source path\n' +
            '                return sourceNodePath + \'.move_to target:\' + targetParentPath.replace(/^story_graph\\./, \'\') + \' at_position:\' + position;\n' +
            '            }\n' +
            '            \n' +
            '            /**\n' +
            '             * Update data-path attribute after successful rename\n' +
            '             * Also updates all child nodes\' paths to reflect parent\'s new name\n' +
            '             * @param {string} oldPath - Old full path (e.g., \'story_graph."OldEpicName"\')\n' +
            '             * @param {string} oldName - Old node name\n' +
            '             * @param {string} newName - New node name\n' +
            '             */\n' +
            '            function updatePathAfterRename(oldPath, oldName, newName) {\n' +
            '                // Calculate new path by replacing old name with new name\n' +
            '                // Handle quoted names in path: story_graph."OldName" -> story_graph."NewName"\n' +
            '                var newPath = oldPath.replace(new RegExp(\'"\' + oldName.replace(/[.*+?^${}()|[\\]\\\\]/g, \'\\\\$&\') + \'"\', \'g\'), \'"\' + newName + \'"\');\n' +
            '                \n' +
            '                // Find the renamed node element\n' +
            '                var nodeElement = findNodeElement(oldPath);\n' +
            '                if (nodeElement) {\n' +
            '                    // Update the renamed node\'s data-path\n' +
            '                    nodeElement.setAttribute(\'data-path\', newPath);\n' +
            '                    console.log(\'[updatePathAfterRename] Updated node path:\', oldPath, \'->\', newPath);\n' +
            '                    \n' +
            '                    // Update window.selectedNode if this node is currently selected\n' +
            '                    if (window.selectedNode && window.selectedNode.path === oldPath) {\n' +
            '                        window.selectedNode.name = newName;\n' +
            '                        window.selectedNode.path = newPath;\n' +
            '                        console.log(\'[updatePathAfterRename] Updated window.selectedNode:\', JSON.stringify(window.selectedNode));\n' +
            '                    }\n' +
            '                    \n' +
            '                    // Find all child nodes and update their paths\n' +
            '                    // Child paths contain the parent\'s name, so we need to update them too\n' +
            '                    var allNodes = document.querySelectorAll(\'.story-node[data-path]\');\n' +
            '                    for (var i = 0; i < allNodes.length; i++) {\n' +
            '                        var childNode = allNodes[i];\n' +
            '                        var childPath = childNode.getAttribute(\'data-path\');\n' +
            '                        if (childPath && childPath.indexOf(oldPath) === 0) {\n' +
            '                            // This is a child node - update its path\n' +
            '                            var updatedChildPath = childPath.replace(new RegExp(\'"\' + oldName.replace(/[.*+?^${}()|[\\]\\\\]/g, \'\\\\$&\') + \'"\', \'g\'), \'"\' + newName + \'"\');\n' +
            '                            childNode.setAttribute(\'data-path\', updatedChildPath);\n' +
            '                            console.log(\'[updatePathAfterRename] Updated child path:\', childPath, \'->\', updatedChildPath);\n' +
            '                            \n' +
            '                            // Also update window.selectedNode if a child is selected\n' +
            '                            if (window.selectedNode && window.selectedNode.path === childPath) {\n' +
            '                                window.selectedNode.path = updatedChildPath;\n' +
            '                                console.log(\'[updatePathAfterRename] Updated window.selectedNode path for child:\', updatedChildPath);\n' +
            '                            }\n' +
            '                        }\n' +
            '                    }\n' +
            '                } else {\n' +
            '                    console.warn(\'[updatePathAfterRename] Could not find node with path:\', oldPath);\n' +
            '                }\n' +
            '            }\n' +
            '            \n' +
            '            /**\n' +
            '             * Build Python command for rename operation\n' +
            '             * @param {string} nodePath - Full path to node\n' +
            '             * @param {string} oldName - Old name\n' +
            '             * @param {string} newName - New name\n' +
            '             * @returns {string} Command string\n' +
            '             */\n' +
            '            function buildRenameCommand(nodePath, oldName, newName) {\n' +
            '                return nodePath + \'.rename("\' + newName + \'")\';\n' +
            '            }\n' +
            '            \n' +
            '            /**\n' +
            '             * Build Python command for delete operation\n' +
            '             * @param {string} nodePath - Full path to node\n' +
            '             * @returns {string} Command string\n' +
            '             */\n' +
            '            function buildDeleteCommand(nodePath) {\n' +
            '                // Delete ALWAYS includes children - no version without children\n' +
            '                // Backend delete() method defaults to cascade=True\n' +
            '                return nodePath + \'.delete()\';\n' +
            '            }\n' +
            '            \n' +
            '            /**\n' +
            '             * Build Python command for create operation\n' +
            '             * @param {string} parentPath - Parent node path\n' +
            '             * @param {string} nodeType - Type of node to create (epic, sub-epic, story, etc.)\n' +
            '             * @returns {string} Command string\n' +
            '             */\n' +
            '            function buildCreateCommand(parentPath, nodeType, placeholderName) {\n' +
            '                // Helper function to check if parentPath is the root story_graph (with or without quotes)\n' +
            '                function isRootStoryGraph(path) {\n' +
            '                    return path === \'story_graph\' || path === \'story_graph."Story Map"\' || path === \'story_graph."root"\';\n' +
            '                }\n' +
            '                \n' +
            '                if (nodeType === \'epic\') {\n' +
            '                    // Include the name parameter so backend creates epic with the same name as frontend\n' +
            '                    if (placeholderName) {\n' +
            '                        return \'story_graph.create_epic name:"\' + placeholderName + \'"\';\n' +
            '                    }\n' +
            '                    return \'story_graph.create_epic\';\n' +
            '                } else if (nodeType === \'sub-epic\') {\n' +
            '                    // Sub-epics can be created on epics or other sub-epics, but not on story_graph\n' +
            '                    if (isRootStoryGraph(parentPath)) {\n' +
            '                        console.error(\'[buildCreateCommand] Cannot create sub-epic on story_graph root. Select an epic first.\');\n' +
            '                        return null; // Invalid command\n' +
            '                    }\n' +
            '                    // Include name parameter if provided\n' +
            '                    if (placeholderName) {\n' +
            '                        return parentPath + \'.create name:"\' + placeholderName + \'"\';\n' +
            '                    }\n' +
            '                    return parentPath + \'.create\';\n' +
            '                } else if (nodeType === \'story\') {\n' +
            '                    // Stories can only be created on epics or sub-epics, not on story_graph\n' +
            '                    if (isRootStoryGraph(parentPath)) {\n' +
            '                        console.error(\'[buildCreateCommand] Cannot create story on story_graph root. Select an epic or sub-epic first.\');\n' +
            '                        return null; // Invalid command\n' +
            '                    }\n' +
            '                    // Include name parameter if provided\n' +
            '                    if (placeholderName) {\n' +
            '                        return parentPath + \'.create_story name:"\' + placeholderName + \'"\';\n' +
            '                    }\n' +
            '                    return parentPath + \'.create_story\';\n' +
            '                } else if (nodeType === \'scenario\') {\n' +
            '                    // Scenarios can only be created on stories, not on story_graph\n' +
            '                    if (isRootStoryGraph(parentPath)) {\n' +
            '                        console.error(\'[buildCreateCommand] Cannot create scenario on story_graph root. Select a story first.\');\n' +
            '                        return null; // Invalid command\n' +
            '                    }\n' +
            '                    // Include name parameter if provided\n' +
            '                    if (placeholderName) {\n' +
            '                        return parentPath + \'.create_scenario name:"\' + placeholderName + \'"\';\n' +
            '                    }\n' +
            '                    return parentPath + \'.create_scenario\';\n' +
            '                } else if (nodeType === \'acceptance-criteria\') {\n' +
            '                    // Acceptance criteria can only be created on stories, not on story_graph\n' +
            '                    if (isRootStoryGraph(parentPath)) {\n' +
            '                        console.error(\'[buildCreateCommand] Cannot create acceptance-criteria on story_graph root. Select a story first.\');\n' +
            '                        return null; // Invalid command\n' +
            '                    }\n' +
            '                    // Include name parameter if provided\n' +
            '                    if (placeholderName) {\n' +
            '                        return parentPath + \'.create_acceptance_criteria name:"\' + placeholderName + \'"\';\n' +
            '                    }\n' +
            '                    return parentPath + \'.create_acceptance_criteria\';\n' +
            '                }\n' +
            '                return parentPath + \'.create\';\n' +
            '            }\n' +
            '            \n' +
            '            /**\n' +
            '             * Handle node move with optimistic update\n' +
            '             * @param {Object} message - {sourceNodePath, targetParentPath, position}\n' +
            '             */\n' +
            '            window.handleMoveNode = function(message) {\n' +
            '                console.log(\'[handleMoveNode] Called with:\', JSON.stringify(message));\n' +
            '                console.log(\'[handleMoveNode] storyMapSaveQueue exists:\', typeof window.storyMapSaveQueue !== \'undefined\');\n' +
            '                \n' +
            '                // ES5-compatible: use var instead of const\n' +
            '                var sourceNodePath = message.sourceNodePath;\n' +
            '                var targetParentPath = message.targetParentPath;\n' +
            '                var position = message.position;\n' +
            '                var targetNodePath = message.targetNodePath;  // Optional: for "after" dropZone\n' +
            '                var dropZone = message.dropZone || \'inside\';\n' +
            '                \n' +
            '                // Find DOM elements\n' +
            '                var sourceNode = findNodeElement(sourceNodePath);\n' +
            '                var targetParent = findNodeElement(targetParentPath);\n' +
            '                var targetNode = targetNodePath ? findNodeElement(targetNodePath) : null;\n' +
            '                \n' +
            '                console.log(\'[handleMoveNode] Found nodes - source:\', !!sourceNode, \'targetParent:\', !!targetParent, \'targetNode:\', !!targetNode);\n' +
            '                \n' +
            '                if (!sourceNode || !targetParent) {\n' +
            '                    console.error(\'Move failed: Could not find nodes\', {\n' +
            '                        sourceNodePath: sourceNodePath,\n' +
            '                        targetParentPath: targetParentPath,\n' +
            '                        targetNodePath: targetNodePath,\n' +
            '                        foundSource: !!sourceNode,\n' +
            '                        foundTarget: !!targetParent,\n' +
            '                        foundTargetNode: !!targetNode\n' +
            '                    });\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
                '                // 1. Capture current state for rollback (ES5-compatible: use slice instead of Array.from)\n' +
                '                // Find the wrapper div for rollback\n' +
                '                var sourceWrapper = findNodeWrapper(sourceNode);\n' +
                '                if (!sourceWrapper) {\n' +
                '                    console.error(\'[handleMoveNode] Cannot find wrapper for sourceNode\');\n' +
                '                    return;\n' +
                '                }\n' +
                '                \n' +
                '                var childrenArray = Array.prototype.slice.call(sourceWrapper.parentElement.children);\n' +
                '                var rollback = {\n' +
                '                    originalParent: sourceWrapper.parentElement,\n' +
                '                    originalPosition: childrenArray.indexOf(sourceWrapper),\n' +
                '                    sourceNode: sourceWrapper  // Store wrapper for rollback\n' +
                '                };\n' +
            '                \n' +
            '                // 2. Optimistic UI update (immediate)\n' +
            '                // For "after" dropZone, pass targetNode to insert after it\n' +
            '                // For "inside" dropZone, use position-based insertion\n' +
            '                if (dropZone === \'after\' && targetNode) {\n' +
            '                    moveNodeInDOM(sourceNode, targetParent, position, targetNode);\n' +
            '                } else {\n' +
            '                    moveNodeInDOM(sourceNode, targetParent, position);\n' +
            '                }\n' +
            '                \n' +
            '                // Create status message - show beside moved node, or beside parent if node is hidden\n' +
            '                var statusId = \'move-status-\' + Date.now() + \'-\' + Math.random().toString(36).substr(2, 9);\n' +
            '                var statusSpan = document.createElement(\'span\');\n' +
            '                statusSpan.id = statusId;\n' +
            '                statusSpan.style.cssText = \'font-size: 11px; color: #666; font-style: italic; margin-left: 8px;\';\n' +
            '                var nodeName = sourceNode.getAttribute ? sourceNode.getAttribute(\'data-node-name\') : (sourceNode.textContent || \'node\');\n' +
            '                statusSpan.textContent = \'Moving \' + nodeName + \'...\';\n' +
            '                \n' +
            '                // Try to insert after moved node, or after parent if node is hidden/collapsed\n' +
            '                var movedWrapper = findNodeWrapper(sourceNode);\n' +
            '                var statusParent = null;\n' +
            '                if (movedWrapper && movedWrapper.parentElement && movedWrapper.offsetParent !== null) {\n' +
            '                    // Node is visible, insert after it\n' +
            '                    statusParent = movedWrapper.parentElement;\n' +
            '                    var nextSibling = movedWrapper.nextSibling;\n' +
            '                    // Skip collapsible-content if present\n' +
            '                    while (nextSibling && nextSibling.nodeType === 1 && nextSibling.classList && nextSibling.classList.contains(\'collapsible-content\')) {\n' +
            '                        nextSibling = nextSibling.nextSibling;\n' +
            '                    }\n' +
            '                    if (nextSibling) {\n' +
            '                        statusParent.insertBefore(statusSpan, nextSibling);\n' +
            '                    } else {\n' +
            '                        statusParent.appendChild(statusSpan);\n' +
            '                    }\n' +
            '                } else {\n' +
            '                    // Node is hidden, show beside parent\n' +
            '                    var targetParentWrapper = findNodeWrapper(targetParent);\n' +
            '                    if (targetParentWrapper && targetParentWrapper.parentElement) {\n' +
            '                        statusParent = targetParentWrapper.parentElement;\n' +
            '                        var parentNextSibling = targetParentWrapper.nextSibling;\n' +
            '                        while (parentNextSibling && parentNextSibling.nodeType === 1 && parentNextSibling.classList && parentNextSibling.classList.contains(\'collapsible-content\')) {\n' +
            '                            parentNextSibling = parentNextSibling.nextSibling;\n' +
            '                        }\n' +
            '                        if (parentNextSibling) {\n' +
            '                            statusParent.insertBefore(statusSpan, parentNextSibling);\n' +
            '                        } else {\n' +
            '                            statusParent.appendChild(statusSpan);\n' +
            '                        }\n' +
            '                    }\n' +
            '                }\n' +
            '                \n' +
            '                // 3. Build command\n' +
            '                var command = buildMoveCommand(sourceNodePath, targetParentPath, position);\n' +
            '                \n' +
            '                // 4. Queue backend save (async) (ES5-compatible: use function instead of arrow)\n' +
            '                if (window.storyMapSaveQueue) {\n' +
            '                    window.storyMapSaveQueue.enqueue({\n' +
            '                        command: command,\n' +
            '                        rollback: function() {\n' +
                '                            // Restore original position in DOM\n' +
                '                            var parent = rollback.originalParent;\n' +
                '                            var pos = rollback.originalPosition;\n' +
                '                            var nodeToRestore = rollback.sourceNode;\n' +
                '                            \n' +
                '                            // Make sure node is not already in the DOM\n' +
                '                            if (nodeToRestore.parentElement) {\n' +
                '                                nodeToRestore.parentElement.removeChild(nodeToRestore);\n' +
                '                            }\n' +
                '                            \n' +
                '                            if (pos >= parent.children.length) {\n' +
                '                                parent.appendChild(nodeToRestore);\n' +
                '                            } else {\n' +
                '                                parent.insertBefore(nodeToRestore, parent.children[pos]);\n' +
                '                            }\n' +
                '                        },\n' +
            '                        metadata: {\n' +
            '                            operation: \'move\',\n' +
            '                            source: sourceNodePath,\n' +
            '                            target: targetParentPath,\n' +
            '                            position: position,\n' +
            '                            statusId: statusId\n' +
            '                        }\n' +
            '                    });\n' +
            '                } else {\n' +
            '                    console.error(\'handleMoveNode: storyMapSaveQueue not available - save will not occur\');\n' +
            '                }\n' +
            '            };\n' +
            '            \n' +
            '            /**\n' +
            '             * Handle node rename with optimistic update\n' +
            '             * @param {Object} message - {nodePath, oldName, newName}\n' +
            '             */\n' +
            '            window.handleRenameNode = function(message) {\n' +
            '                // ES5-compatible: use var instead of const\n' +
            '                var nodePath = message.nodePath;\n' +
            '                var oldName = message.oldName;\n' +
            '                var newName = message.newName;\n' +
            '                \n' +
            '                var nodeElement = findNodeElement(nodePath);\n' +
            '                if (!nodeElement) {\n' +
            '                    console.error(\'Rename failed: Could not find node\', nodePath);\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
            '                // Create status message span (similar to create operations)\n' +
            '                var statusId = \'rename-status-\' + Date.now() + \'-\' + Math.random().toString(36).substr(2, 9);\n' +
            '                var statusSpan = document.createElement(\'span\');\n' +
            '                statusSpan.id = statusId;\n' +
            '                statusSpan.style.cssText = \'font-size: 11px; color: #666; font-style: italic; margin-left: 8px;\';\n' +
            '                statusSpan.textContent = \'saving...\';\n' +
            '                \n' +
            '                // Insert status message after the node element\n' +
            '                if (nodeElement.parentElement) {\n' +
            '                    nodeElement.parentElement.insertBefore(statusSpan, nodeElement.nextSibling);\n' +
            '                } else {\n' +
            '                    // Fallback: append to node element if no parent\n' +
            '                    nodeElement.appendChild(statusSpan);\n' +
            '                }\n' +
            '                \n' +
            '                // 1. Capture for rollback - use the node element itself (it contains the name)\n' +
            '                var rollback = {\n' +
            '                    element: nodeElement,\n' +
            '                    oldName: oldName,\n' +
            '                    statusSpan: statusSpan\n' +
            '                };\n' +
            '                \n' +
            '                // 2. Optimistic UI update\n' +
            '                nodeElement.textContent = newName;\n' +
            '                nodeElement.setAttribute(\'data-node-name\', newName);\n' +
            '                \n' +
            '                // 3. Build command\n' +
            '                var command = buildRenameCommand(nodePath, oldName, newName);\n' +
            '                \n' +
            '                // 4. Queue save (ES5-compatible: use function instead of arrow)\n' +
            '                if (window.storyMapSaveQueue) {\n' +
            '                    window.storyMapSaveQueue.enqueue({\n' +
            '                        command: command,\n' +
            '                        rollback: function() {\n' +
            '                            rollback.element.textContent = rollback.oldName;\n' +
            '                            rollback.element.setAttribute(\'data-node-name\', rollback.oldName);\n' +
            '                            if (rollback.statusSpan && rollback.statusSpan.parentElement) {\n' +
            '                                rollback.statusSpan.remove();\n' +
            '                            }\n' +
            '                        },\n' +
            '                        metadata: {\n' +
            '                            operation: \'rename\',\n' +
            '                            path: nodePath,\n' +
            '                            oldName: oldName,\n' +
            '                            newName: newName,\n' +
            '                            statusId: statusId\n' +
            '                        }\n' +
            '                    });\n' +
            '                }\n' +
            '            };\n' +
            '            \n' +
            '            /**\n' +
            '             * Handle node delete with optimistic update\n' +
            '             * @param {Object} message - {nodePath}\n' +
            '             */\n' +
            '            window.handleDeleteNode = function(message) {\n' +
            '                console.log(\'[handleDeleteNode] START - Called with:\', JSON.stringify(message));\n' +
            '                \n' +
            '                // ES5-compatible: use var instead of const/let, use slice instead of Array.from\n' +
            '                var nodePath = message.nodePath;\n' +
            '                // Delete ALWAYS includes children - no version without children\n' +
            '                \n' +
            '                console.log(\'[handleDeleteNode] Looking for node with path:\', nodePath);\n' +
            '                var nodeElement = findNodeElement(nodePath);\n' +
            '                if (!nodeElement) {\n' +
            '                    console.error(\'[handleDeleteNode] Delete failed: Could not find node element for path:\', nodePath);\n' +
            '                    console.error(\'[handleDeleteNode] Available nodes in DOM:\');\n' +
            '                    var allNodes = document.querySelectorAll(\'[data-path]\');\n' +
            '                    for (var i = 0; i < Math.min(allNodes.length, 10); i++) {\n' +
            '                        console.error(\'[handleDeleteNode]   Node:\', allNodes[i].getAttribute(\'data-path\'));\n' +
            '                    }\n' +
            '                    return;\n' +
            '                }\n' +
            '                console.log(\'[handleDeleteNode] Found nodeElement:\', nodeElement, \'tagName:\', nodeElement.tagName, \'className:\', nodeElement.className);\n' +
            '                \n' +
            '                // 1. Capture entire node HTML for rollback\n' +
            '                // Find the wrapper div (like handleMoveNode does)\n' +
            '                console.log(\'[handleDeleteNode] Finding wrapper for nodeElement...\');\n' +
            '                var wrapper = findNodeWrapper(nodeElement);\n' +
            '                if (!wrapper) {\n' +
            '                    console.error(\'[handleDeleteNode] Cannot find wrapper for nodeElement\');\n' +
            '                    console.error(\'[handleDeleteNode] nodeElement parent:\', nodeElement.parentElement);\n' +
            '                    console.error(\'[handleDeleteNode] nodeElement parent tagName:\', nodeElement.parentElement ? nodeElement.parentElement.tagName : \'null\');\n' +
            '                    return;\n' +
            '                }\n' +
            '                console.log(\'[handleDeleteNode] Found wrapper:\', wrapper, \'tagName:\', wrapper.tagName, \'id:\', wrapper.id);\n' +
            '                \n' +
            '                var parent = wrapper.parentElement;\n' +
            '                console.log(\'[handleDeleteNode] Parent container:\', parent, \'tagName:\', parent ? parent.tagName : \'null\', \'className:\', parent ? parent.className : \'null\');\n' +
            '                if (!parent) {\n' +
            '                    console.error(\'[handleDeleteNode] Wrapper has no parent element!\');\n' +
            '                    return;\n' +
            '                }\n' +
            '                var childrenArray = Array.prototype.slice.call(parent.children);\n' +
            '                var position = childrenArray.indexOf(wrapper);\n' +
            '                console.log(\'[handleDeleteNode] Wrapper position in parent:\', position, \'total children:\', childrenArray.length);\n' +
            '                \n' +
            '                // Delete ALWAYS includes children - capture all nested nodes\n' +
            '                var nodeHTML = wrapper.outerHTML;\n' +
            '                // The outerHTML already includes all children, so we\'re good\n' +
            '                \n' +
            '                // Find and capture collapsible-content sibling before removal\n' +
            '                var collapsibleContent = null;\n' +
            '                var nextSibling = wrapper.nextSibling;\n' +
            '                while (nextSibling) {\n' +
            '                    if (nextSibling.nodeType === 1 && nextSibling.classList && nextSibling.classList.contains(\'collapsible-content\')) {\n' +
            '                        collapsibleContent = nextSibling;\n' +
            '                        break;\n' +
            '                    }\n' +
            '                    nextSibling = nextSibling.nextSibling;\n' +
            '                }\n' +
            '                var collapsibleHTML = collapsibleContent ? collapsibleContent.outerHTML : null;\n' +
            '                \n' +
            '                // Create status message span - show beside parent (not the node being deleted)\n' +
            '                var statusId = \'delete-status-\' + Date.now() + \'-\' + Math.random().toString(36).substr(2, 9);\n' +
            '                var statusSpan = document.createElement(\'span\');\n' +
            '                statusSpan.id = statusId;\n' +
            '                statusSpan.style.cssText = \'font-size: 11px; color: #666; font-style: italic; margin-left: 8px;\';\n' +
            '                var nodeName = nodeElement.getAttribute ? nodeElement.getAttribute(\'data-node-name\') : (nodeElement.textContent || \'node\');\n' +
            '                statusSpan.textContent = \'Deleting \' + nodeName + \'...\';\n' +
            '                \n' +
            '                // Find parent node element to show status beside it\n' +
            '                // The parent container is the collapsible-content, we need to find the parent\'s node element\n' +
            '                var parentNodeElement = null;\n' +
            '                if (parent && parent.classList && parent.classList.contains(\'collapsible-content\')) {\n' +
            '                    // Find the parent wrapper that contains this collapsible-content\n' +
            '                    var parentWrapper = parent.previousSibling;\n' +
            '                    while (parentWrapper) {\n' +
            '                        if (parentWrapper.nodeType === 1) {\n' +
            '                            var parentNode = parentWrapper.querySelector ? parentWrapper.querySelector(\'.story-node\') : null;\n' +
            '                            if (parentNode) {\n' +
            '                                parentNodeElement = parentNode;\n' +
            '                                break;\n' +
            '                            }\n' +
            '                        }\n' +
            '                        parentWrapper = parentWrapper.previousSibling;\n' +
            '                    }\n' +
            '                }\n' +
            '                \n' +
            '                // Insert status message beside parent node element, or in parent container if parent not found\n' +
            '                if (parentNodeElement && parentNodeElement.parentElement) {\n' +
            '                    // Insert after parent node element\n' +
            '                    var parentParent = parentNodeElement.parentElement;\n' +
            '                    var parentNextSibling = parentNodeElement.nextSibling;\n' +
            '                    if (parentNextSibling) {\n' +
            '                        parentParent.insertBefore(statusSpan, parentNextSibling);\n' +
            '                    } else {\n' +
            '                        parentParent.appendChild(statusSpan);\n' +
            '                    }\n' +
            '                } else if (parent) {\n' +
            '                    // Fallback: insert at start of parent container\n' +
            '                    if (parent.firstChild) {\n' +
            '                        parent.insertBefore(statusSpan, parent.firstChild);\n' +
            '                    } else {\n' +
            '                        parent.appendChild(statusSpan);\n' +
            '                    }\n' +
            '                }\n' +
            '                \n' +
            '                var rollback = {\n' +
            '                    parent: parent,\n' +
            '                    position: position,\n' +
            '                    nodeHTML: nodeHTML,\n' +
            '                    collapsibleHTML: collapsibleHTML,\n' +
            '                    statusSpan: statusSpan\n' +
            '                };\n' +
            '                \n' +
            '                // 2. Optimistic UI update (remove wrapper and collapsible-content from DOM)\n' +
            '                console.log(\'[handleDeleteNode] About to remove wrapper from DOM...\');\n' +
            '                console.log(\'[handleDeleteNode] Wrapper still in DOM before remove:\', wrapper.parentElement === parent);\n' +
            '                console.log(\'[handleDeleteNode] Wrapper still has parent:\', !!wrapper.parentElement);\n' +
            '                \n' +
            '                // Use remove() if available, fallback to removeChild() for compatibility\n' +
            '                if (wrapper.remove && typeof wrapper.remove === \'function\') {\n' +
            '                    wrapper.remove();\n' +
            '                    console.log(\'[handleDeleteNode] Used wrapper.remove()\');\n' +
            '                } else if (wrapper.parentElement && wrapper.parentElement.removeChild) {\n' +
            '                    wrapper.parentElement.removeChild(wrapper);\n' +
            '                    console.log(\'[handleDeleteNode] Used parent.removeChild(wrapper)\');\n' +
            '                } else {\n' +
            '                    console.error(\'[handleDeleteNode] Cannot remove wrapper - no remove method available!\');\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
            '                console.log(\'[handleDeleteNode] After wrapper removal:\');\n' +
            '                console.log(\'[handleDeleteNode] Wrapper still has parent:\', !!wrapper.parentElement);\n' +
            '                console.log(\'[handleDeleteNode] Wrapper in parent.children:\', parent.children ? Array.prototype.slice.call(parent.children).indexOf(wrapper) : \'N/A\');\n' +
            '                console.log(\'[handleDeleteNode] Parent children count:\', parent.children ? parent.children.length : \'N/A\');\n' +
            '                \n' +
            '                if (collapsibleContent) {\n' +
            '                    console.log(\'[handleDeleteNode] Removing collapsible-content:\', collapsibleContent);\n' +
            '                    if (collapsibleContent.remove && typeof collapsibleContent.remove === \'function\') {\n' +
            '                        collapsibleContent.remove();\n' +
            '                    } else if (collapsibleContent.parentElement && collapsibleContent.parentElement.removeChild) {\n' +
            '                        collapsibleContent.parentElement.removeChild(collapsibleContent);\n' +
            '                    }\n' +
            '                    console.log(\'[handleDeleteNode] Collapsible-content removed, still has parent:\', !!collapsibleContent.parentElement);\n' +
            '                } else {\n' +
            '                    console.log(\'[handleDeleteNode] No collapsible-content to remove\');\n' +
            '                }\n' +
            '                \n' +
            '                // 3. Build command - ALWAYS delete including children\n' +
            '                var command = buildDeleteCommand(nodePath);\n' +
            '                console.log(\'[handleDeleteNode] Built command:\', command);\n' +
            '                \n' +
            '                // 4. Queue save (ES5-compatible: use function instead of arrow)\n' +
            '                console.log(\'[handleDeleteNode] Checking storyMapSaveQueue...\');\n' +
            '                if (window.storyMapSaveQueue) {\n' +
            '                    console.log(\'[handleDeleteNode] storyMapSaveQueue exists, enqueueing delete operation...\');\n' +
            '                    window.storyMapSaveQueue.enqueue({\n' +
            '                        command: command,\n' +
            '                        rollback: function() {\n' +
            '                            // Restore deleted node (both wrapper and collapsible-content)\n' +
            '                            var tempDiv = document.createElement(\'div\');\n' +
            '                            tempDiv.innerHTML = rollback.nodeHTML;\n' +
            '                            var restoredNode = tempDiv.firstChild;\n' +
            '                            \n' +
            '                            if (rollback.position >= rollback.parent.children.length) {\n' +
            '                                rollback.parent.appendChild(restoredNode);\n' +
            '                            } else {\n' +
            '                                rollback.parent.insertBefore(restoredNode, rollback.parent.children[rollback.position]);\n' +
            '                            }\n' +
            '                            \n' +
            '                            // Restore collapsible-content if it existed\n' +
            '                            if (rollback.collapsibleHTML) {\n' +
            '                                var collapsibleTempDiv = document.createElement(\'div\');\n' +
            '                                collapsibleTempDiv.innerHTML = rollback.collapsibleHTML;\n' +
            '                                var restoredCollapsible = collapsibleTempDiv.firstChild;\n' +
            '                                // Insert after the restored node\n' +
            '                                if (restoredNode.nextSibling) {\n' +
            '                                    rollback.parent.insertBefore(restoredCollapsible, restoredNode.nextSibling);\n' +
            '                                } else {\n' +
            '                                    rollback.parent.appendChild(restoredCollapsible);\n' +
            '                                }\n' +
            '                            }\n' +
            '                        },\n' +
            '                        metadata: {\n' +
            '                            operation: \'delete\',\n' +
            '                            path: nodePath,\n' +
            '                            statusId: statusId\n' +
            '                        }\n' +
            '                    });\n' +
            '                    console.log(\'[handleDeleteNode] Delete operation enqueued successfully\');\n' +
            '                } else {\n' +
            '                    console.error(\'[handleDeleteNode] storyMapSaveQueue not available - delete will not be saved!\');\n' +
            '                    console.error(\'[handleDeleteNode] typeof window.storyMapSaveQueue:\', typeof window.storyMapSaveQueue);\n' +
            '                }\n' +
            '                \n' +
            '                // Final verification - check if node is still in DOM\n' +
            '                setTimeout(function() {\n' +
            '                    var stillExists = findNodeElement(nodePath);\n' +
            '                    if (stillExists) {\n' +
            '                        console.error(\'[handleDeleteNode] WARNING: Node still exists in DOM after removal! Path:\', nodePath);\n' +
            '                        console.error(\'[handleDeleteNode] Node element:\', stillExists);\n' +
            '                    } else {\n' +
            '                        console.log(\'[handleDeleteNode] SUCCESS: Node successfully removed from DOM\');\n' +
            '                    }\n' +
            '                }, 100);\n' +
            '            };\n' +
            '            \n' +
            '            /**\n' +
            '             * Handle delete button click - calls handleDeleteNode with selected node\n' +
            '             */\n' +
            '            window.handleDelete = function() {\n' +
            '                console.log(\'[handleDelete] Called, selectedNode:\', window.selectedNode);\n' +
            '                \n' +
            '                if (!window.selectedNode || !window.selectedNode.name) {\n' +
            '                    console.error(\'[handleDelete] No node selected for delete\');\n' +
            '                    if (typeof vscode !== \'undefined\') {\n' +
            '                        vscode.postMessage({\n' +
            '                            type: \'showErrorDialog\',\n' +
            '                            title: \'Delete Failed\',\n' +
            '                            message: \'No node selected for deletion.\'\n' +
            '                        });\n' +
            '                    }\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
            '                // Build node path\n' +
            '                var nodePath = window.selectedNode.path;\n' +
            '                if (!nodePath || nodePath.length <= \'story_graph.\'.length) {\n' +
            '                    // Fallback: construct path from name\n' +
            '                    nodePath = \'story_graph."\' + window.selectedNode.name + \'"\';\n' +
            '                }\n' +
            '                \n' +
            '                console.log(\'[handleDelete] Calling handleDeleteNode with path:\', nodePath);\n' +
            '                \n' +
            '                // Call handleDeleteNode for optimistic update (this removes from DOM and queues save)\n' +
            '                // Delete ALWAYS includes children\n' +
            '                window.handleDeleteNode({\n' +
            '                    nodePath: nodePath\n' +
            '                });\n' +
            '            };\n' +
            '            \n' +
            '            /**\n' +
            '             * Update parent node\'s collapse icon when it gets its first child\n' +
            '             * Replaces empty placeholder with collapse icon (+)\n' +
            '             * @param {string} parentPath - Path to parent node\n' +
            '             */\n' +
            '            function updateParentCollapseIcon(parentPath) {\n' +
            '                console.log(\'[updateParentCollapseIcon] Updating parent collapse icon for:\', parentPath);\n' +
            '                \n' +
            '                var parentElement = findNodeElement(parentPath);\n' +
            '                if (!parentElement) {\n' +
            '                    console.warn(\'[updateParentCollapseIcon] Parent element not found:\', parentPath);\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
            '                var parentWrapper = findNodeWrapper(parentElement);\n' +
            '                if (!parentWrapper) {\n' +
            '                    console.warn(\'[updateParentCollapseIcon] Parent wrapper not found\');\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
            '                // Find the collapse icon span (first child of wrapper, or first span)\n' +
            '                var collapseIconSpan = parentWrapper.querySelector ? parentWrapper.querySelector(\'span:first-child\') : null;\n' +
            '                if (!collapseIconSpan) {\n' +
            '                    console.warn(\'[updateParentCollapseIcon] Collapse icon span not found\');\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
            '                // Check if it has an empty placeholder (img with empty alt)\n' +
            '                var emptyImg = collapseIconSpan.querySelector ? collapseIconSpan.querySelector(\'img[alt=""]\') : null;\n' +
            '                if (!emptyImg) {\n' +
            '                    // Already has a collapse icon, nothing to do\n' +
            '                    console.log(\'[updateParentCollapseIcon] Parent already has collapse icon\');\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
            '                // Find plus icon path from existing nodes\n' +
            '                var plusIconPath = null;\n' +
            '                var existingEpicIcon = document.querySelector(\'#epic-0-icon img.collapse-icon\');\n' +
            '                if (existingEpicIcon) {\n' +
            '                    plusIconPath = existingEpicIcon.src;\n' +
            '                }\n' +
            '                \n' +
            '                if (!plusIconPath) {\n' +
            '                    console.warn(\'[updateParentCollapseIcon] Plus icon path not found\');\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
            '                // Find the collapsible-content div that follows the wrapper\n' +
            '                // This is where children are stored\n' +
            '                var parentCollapsibleContent = null;\n' +
            '                var nextSibling = parentWrapper.nextSibling;\n' +
            '                while (nextSibling) {\n' +
            '                    if (nextSibling.nodeType === 1 && nextSibling.classList && nextSibling.classList.contains(\'collapsible-content\')) {\n' +
            '                        parentCollapsibleContent = nextSibling;\n' +
            '                        break;\n' +
            '                    }\n' +
            '                    nextSibling = nextSibling.nextSibling;\n' +
            '                }\n' +
            '                \n' +
            '                if (!parentCollapsibleContent) {\n' +
            '                    console.warn(\'[updateParentCollapseIcon] Parent collapsible-content not found - parent may not support children\');\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
            '                var parentId = parentCollapsibleContent.id;\n' +
            '                if (!parentId) {\n' +
            '                    console.warn(\'[updateParentCollapseIcon] Parent collapsible-content has no ID\');\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
            '                console.log(\'[updateParentCollapseIcon] Replacing empty placeholder with collapse icon, parentId:\', parentId);\n' +
            '                \n' +
            '                // Clear the span and add collapse icon\n' +
            '                collapseIconSpan.innerHTML = \'\';\n' +
            '                collapseIconSpan.id = parentId + \'-icon\';\n' +
            '                collapseIconSpan.style.cssText = \'display: inline-block; min-width: 9px; cursor: pointer;\';\n' +
            '                collapseIconSpan.setAttribute(\'onclick\', \'event.stopPropagation(); toggleCollapse("\' + parentId + \'")\');\n' +
            '                collapseIconSpan.setAttribute(\'data-plus\', plusIconPath);\n' +
            '                collapseIconSpan.setAttribute(\'data-subtract\', plusIconPath.replace(\'plus\', \'subtract\'));\n' +
            '                \n' +
            '                // Create collapse icon image\n' +
            '                var collapseImg = document.createElement(\'img\');\n' +
            '                collapseImg.className = \'collapse-icon\';\n' +
            '                collapseImg.src = plusIconPath;\n' +
            '                collapseImg.setAttribute(\'data-state\', \'collapsed\');\n' +
            '                collapseImg.style.cssText = \'width: 9px; height: 9px; vertical-align: middle;\';\n' +
            '                collapseImg.alt = \'Expand\';\n' +
            '                collapseIconSpan.appendChild(collapseImg);\n' +
            '                \n' +
            '                // Update data-has-children attribute\n' +
            '                if (parentElement.setAttribute) {\n' +
            '                    parentElement.setAttribute(\'data-has-children\', \'true\');\n' +
            '                }\n' +
            '                \n' +
            '                console.log(\'[updateParentCollapseIcon] Successfully updated parent collapse icon\');\n' +
            '            }\n' +
            '            \n' +
            '            /**\n' +
            '             * Handle node create with optimistic update\n' +
            '             * @param {Object} message - {parentPath, nodeType, placeholderName}\n' +
            '             */\n' +
            '            window.handleCreateNode = function(message) {\n' +
            '                console.log(\'[handleCreateNode] Called with:\', JSON.stringify(message));\n' +
            '                \n' +
            '                var parentPath = message.parentPath || \'story_graph\';\n' +
            '                var nodeType = message.nodeType || \'epic\';\n' +
            '                \n' +
            '                // Generate name matching backend pattern (Epic1, Epic2, Child1, Story1, etc.)\n' +
            '                var placeholderName = message.placeholderName;\n' +
            '                if (!placeholderName) {\n' +
            '                    // Backend uses: Epic1, Child1 (for sub-epics), Story1, etc.\n' +
            '                    var baseName = nodeType === \'epic\' ? \'Epic\' : (nodeType === \'sub-epic\' ? \'Child\' : (nodeType === \'story\' ? \'Story\' : nodeType.charAt(0).toUpperCase() + nodeType.slice(1)));\n' +
            '                    \n' +
            '                    // Find existing nodes of same type to determine next number\n' +
            '                    // Need to check ALL nodes including optimistically created ones\n' +
            '                    var existingNodes = null;\n' +
            '                    console.log(\'[handleCreateNode] Starting name generation for\', nodeType, \'parentPath:\', parentPath);\n' +
            '                    \n' +
            '                    if (nodeType === \'sub-epic\' && parentPath !== \'story_graph\') {\n' +
            '                        // Find parent element and its collapsible-content\n' +
            '                        var parentEl = findNodeElement(parentPath);\n' +
            '                        if (parentEl) {\n' +
            '                            var parentWrapper = findNodeWrapper(parentEl);\n' +
            '                            if (parentWrapper) {\n' +
            '                                var nextSibling = parentWrapper.nextSibling;\n' +
            '                                while (nextSibling) {\n' +
            '                                    if (nextSibling.nodeType === 1 && nextSibling.classList && nextSibling.classList.contains(\'collapsible-content\')) {\n' +
            '                                        existingNodes = nextSibling.querySelectorAll(\'.story-node[data-node-type="sub-epic"]\');\n' +
            '                                        break;\n' +
            '                                    }\n' +
            '                                    nextSibling = nextSibling.nextSibling;\n' +
            '                                }\n' +
            '                            }\n' +
            '                        }\n' +
            '                    } else if (nodeType === \'story\' && parentPath !== \'story_graph\') {\n' +
            '                        // Stories are nested under sub-epics - find parent element and its collapsible-content\n' +
            '                        var parentEl = findNodeElement(parentPath);\n' +
            '                        if (parentEl) {\n' +
            '                            var parentWrapper = findNodeWrapper(parentEl);\n' +
            '                            if (parentWrapper) {\n' +
            '                                var nextSibling = parentWrapper.nextSibling;\n' +
            '                                while (nextSibling) {\n' +
            '                                    if (nextSibling.nodeType === 1 && nextSibling.classList && nextSibling.classList.contains(\'collapsible-content\')) {\n' +
            '                                        existingNodes = nextSibling.querySelectorAll(\'.story-node[data-node-type="story"]\');\n' +
            '                                        console.log(\'[handleCreateNode] Found\', existingNodes.length, \'stories in parent sub-epic\');\n' +
            '                                        break;\n' +
            '                                    }\n' +
            '                                    nextSibling = nextSibling.nextSibling;\n' +
            '                                }\n' +
            '                            }\n' +
            '                        }\n' +
            '                    }\n' +
            '                    \n' +
            '                    if (!existingNodes) {\n' +
            '                        // Query ALL nodes of this type in the DOM (including optimistically created ones)\n' +
            '                        // For epics at root, search within scope-content container where epics are rendered\n' +
            '                        if (nodeType === \'epic\' && parentPath === \'story_graph\') {\n' +
            '                            console.log(\'[handleCreateNode] Searching for epic nodes in scope-content...\');\n' +
            '                            // Epics are rendered inside #scope-content (has class collapsible-content)\n' +
            '                            var scopeContent = document.getElementById(\'scope-content\');\n' +
            '                            console.log(\'[handleCreateNode] scope-content element:\', scopeContent ? \'found\' : \'NOT FOUND\');\n' +
            '                            if (scopeContent) {\n' +
            '                                // Debug: Check what\'s actually in scope-content\n' +
            '                                var allStoryNodes = scopeContent.querySelectorAll(\'.story-node\');\n' +
            '                                console.log(\'[handleCreateNode] DEBUG: Found\', allStoryNodes.length, \'total .story-node elements in scope-content\');\n' +
            '                                // Check first few nodes to see their types\n' +
            '                                var nodeTypeCounts = {};\n' +
            '                                for (var i = 0; i < Math.min(allStoryNodes.length, 10); i++) {\n' +
            '                                    var nodeType = allStoryNodes[i].getAttribute(\'data-node-type\');\n' +
            '                                    nodeTypeCounts[nodeType] = (nodeTypeCounts[nodeType] || 0) + 1;\n' +
            '                                }\n' +
            '                                console.log(\'[handleCreateNode] DEBUG: Node type counts (first 10):\', nodeTypeCounts);\n' +
            '                                if (allStoryNodes.length > 0) {\n' +
            '                                    console.log(\'[handleCreateNode] DEBUG: First story-node attributes:\', {\n' +
            '                                        \'data-node-type\': allStoryNodes[0].getAttribute(\'data-node-type\'),\n' +
            '                                        \'data-node-name\': allStoryNodes[0].getAttribute(\'data-node-name\'),\n' +
            '                                        className: allStoryNodes[0].className\n' +
            '                                    });\n' +
            '                                    // Also check if we can find epic nodes with a different approach\n' +
            '                                    var epicNodesByClass = scopeContent.querySelectorAll(\'.story-node[data-node-type="epic"]\');\n' +
            '                                    console.log(\'[handleCreateNode] DEBUG: Direct epic query in scope-content:\', epicNodesByClass.length);\n' +
            '                                    if (epicNodesByClass.length === 0) {\n' +
            '                                        // Try finding epic nodes by checking all nodes\n' +
            '                                        var epicNodesFound = [];\n' +
            '                                        for (var j = 0; j < Math.min(allStoryNodes.length, 50); j++) {\n' +
            '                                            if (allStoryNodes[j].getAttribute(\'data-node-type\') === \'epic\') {\n' +
            '                                                epicNodesFound.push({\n' +
            '                                                    name: allStoryNodes[j].getAttribute(\'data-node-name\'),\n' +
            '                                                    index: j\n' +
            '                                                });\n' +
            '                                            }\n' +
            '                                        }\n' +
            '                                        console.log(\'[handleCreateNode] DEBUG: Epic nodes found by manual check (first 50):\', epicNodesFound);\n' +
            '                                    }\n' +
            '                                }\n' +
            '                                \n' +
            '                                // Try querySelectorAll first\n' +
            '                                existingNodes = scopeContent.querySelectorAll(\'.story-node[data-node-type="\' + nodeType + \']\');\n' +
            '                                console.log(\'[handleCreateNode] Found\', existingNodes.length, \'epic nodes in scope-content container (querySelectorAll)\');\n' +
            '                                // If querySelectorAll fails, manually filter all story-node elements\n' +
            '                                if (existingNodes.length === 0 && allStoryNodes.length > 0) {\n' +
            '                                    var manualEpicNodes = [];\n' +
            '                                    for (var k = 0; k < allStoryNodes.length; k++) {\n' +
            '                                        if (allStoryNodes[k].getAttribute(\'data-node-type\') === nodeType) {\n' +
            '                                            manualEpicNodes.push(allStoryNodes[k]);\n' +
            '                                        }\n' +
            '                                    }\n' +
            '                                    console.log(\'[handleCreateNode] Found\', manualEpicNodes.length, \'epic nodes by manual filtering\');\n' +
            '                                    if (manualEpicNodes.length > 0) {\n' +
            '                                        // Convert array to NodeList-like object\n' +
            '                                        existingNodes = manualEpicNodes;\n' +
            '                                    }\n' +
            '                                }\n' +
            '                                // Also check card-secondary inside scope-content\n' +
            '                                if (existingNodes.length === 0) {\n' +
            '                                    var cardSecondary = scopeContent.querySelector(\'.card-secondary\');\n' +
            '                                    console.log(\'[handleCreateNode] DEBUG: card-secondary element:\', cardSecondary ? \'found\' : \'NOT FOUND\');\n' +
            '                                    if (cardSecondary) {\n' +
            '                                        var cardStoryNodes = cardSecondary.querySelectorAll(\'.story-node\');\n' +
            '                                        console.log(\'[handleCreateNode] DEBUG: Found\', cardStoryNodes.length, \'total .story-node elements in card-secondary\');\n' +
            '                                        existingNodes = cardSecondary.querySelectorAll(\'.story-node[data-node-type="\' + nodeType + \']\');\n' +
            '                                        console.log(\'[handleCreateNode] Found\', existingNodes.length, \'epic nodes in card-secondary\');\n' +
            '                                    }\n' +
            '                                }\n' +
            '                            }\n' +
            '                            // Also search entire document as fallback (for optimistically created nodes that might be elsewhere)\n' +
            '                            if (!existingNodes || existingNodes.length === 0) {\n' +
            '                                var allDocStoryNodes = document.querySelectorAll(\'.story-node\');\n' +
            '                                console.log(\'[handleCreateNode] DEBUG: Found\', allDocStoryNodes.length, \'total .story-node elements in entire document\');\n' +
            '                                existingNodes = document.querySelectorAll(\'.story-node[data-node-type="\' + nodeType + \']\');\n' +
            '                                console.log(\'[handleCreateNode] Fallback: Found\', existingNodes.length, \'epic nodes in entire document\');\n' +
            '                            }\n' +
            '                        } else {\n' +
            '                            existingNodes = document.querySelectorAll(\'.story-node[data-node-type="\' + nodeType + \']\');\n' +
            '                            console.log(\'[handleCreateNode] Searched entire document, found\', existingNodes.length, nodeType, \'nodes\');\n' +
            '                        }\n' +
            '                    }\n' +
            '                    \n' +
            '                    // Ensure existingNodes is initialized (should never be null at this point)\n' +
            '                    if (!existingNodes) {\n' +
            '                        existingNodes = document.querySelectorAll(\'.story-node[data-node-type="\' + nodeType + \']\');\n' +
            '                        console.log(\'[handleCreateNode] Final fallback: Found\', existingNodes.length, nodeType, \'nodes\');\n' +
            '                    }\n' +
            '                    \n' +
            '                    console.log(\'[handleCreateNode] Found\', existingNodes.length, \'existing\', nodeType, \'nodes for name generation\');\n' +
            '                    \n' +
            '                    var maxNum = 0;\n' +
            '                    var foundNames = [];\n' +
            '                    for (var i = 0; i < existingNodes.length; i++) {\n' +
            '                        var nodeName = existingNodes[i].getAttribute(\'data-node-name\');\n' +
            '                        console.log(\'[handleCreateNode] Node\', i, \'name:\', nodeName, \'element:\', existingNodes[i]);\n' +
            '                        if (nodeName) {\n' +
            '                            foundNames.push(nodeName);\n' +
            '                            // Match pattern like "Epic1", "Epic2", "Child3", "Story1", etc.\n' +
            '                            // Also handle "Epic 1" with space (though backend uses "Epic1")\n' +
            '                            var match = nodeName.match(new RegExp(\'^\' + baseName + \'[\\s]*([0-9]+)$\'));\n' +
            '                            if (match) {\n' +
            '                                var num = parseInt(match[1], 10);\n' +
            '                                console.log(\'[handleCreateNode] Found\', nodeType, \'with number:\', num, \'name:\', nodeName);\n' +
            '                                if (num > maxNum) maxNum = num;\n' +
            '                            }\n' +
            '                        }\n' +
            '                    }\n' +
            '                    \n' +
            '                    // Also check for optimistically created nodes in SaveQueue (both queue and currently executing)\n' +
            '                    if (window.storyMapSaveQueue) {\n' +
            '                        // Check currently executing operation\n' +
            '                        if (window.storyMapSaveQueue.currentlyExecuting && window.storyMapSaveQueue.currentlyExecuting.metadata) {\n' +
            '                            var execOp = window.storyMapSaveQueue.currentlyExecuting.metadata;\n' +
            '                            if (execOp.operation === \'create\' && execOp.nodeType === nodeType) {\n' +
            '                                var execNodeEl = document.getElementById(execOp.tempNodeId);\n' +
            '                                if (execNodeEl) {\n' +
            '                                    var execNodeSpan = execNodeEl.querySelector(\'.story-node\');\n' +
            '                                    if (execNodeSpan) {\n' +
            '                                        var execName = execNodeSpan.getAttribute(\'data-node-name\');\n' +
            '                                        if (execName) {\n' +
            '                                            foundNames.push(\'[executing]\' + execName);\n' +
            '                                            var execMatch = execName.match(new RegExp(\'^\' + baseName + \'[\\s]*([0-9]+)$\'));\n' +
            '                                            if (execMatch) {\n' +
            '                                                var execNum = parseInt(execMatch[1], 10);\n' +
            '                                                console.log(\'[handleCreateNode] Found executing\', nodeType, \'with number:\', execNum);\n' +
            '                                                if (execNum > maxNum) maxNum = execNum;\n' +
            '                                            }\n' +
            '                                        }\n' +
            '                                    }\n' +
            '                                }\n' +
            '                            }\n' +
            '                        }\n' +
            '                        // Check queue\n' +
            '                        if (window.storyMapSaveQueue.queue) {\n' +
            '                            console.log(\'[handleCreateNode] Checking SaveQueue queue, length:\', window.storyMapSaveQueue.queue.length);\n' +
            '                            for (var j = 0; j < window.storyMapSaveQueue.queue.length; j++) {\n' +
            '                                var queuedOp = window.storyMapSaveQueue.queue[j];\n' +
            '                                if (queuedOp.metadata && queuedOp.metadata.operation === \'create\' && queuedOp.metadata.nodeType === nodeType) {\n' +
            '                                    var queuedNodeEl = document.getElementById(queuedOp.metadata.tempNodeId);\n' +
            '                                    if (queuedNodeEl) {\n' +
            '                                        var queuedNodeSpan = queuedNodeEl.querySelector(\'.story-node\');\n' +
            '                                        if (queuedNodeSpan) {\n' +
            '                                            var queuedName = queuedNodeSpan.getAttribute(\'data-node-name\');\n' +
            '                                            if (queuedName) {\n' +
            '                                                foundNames.push(\'[queued]\' + queuedName);\n' +
            '                                                var queuedMatch = queuedName.match(new RegExp(\'^\' + baseName + \'[\\s]*([0-9]+)$\'));\n' +
            '                                                if (queuedMatch) {\n' +
            '                                                    var queuedNum = parseInt(queuedMatch[1], 10);\n' +
            '                                                    console.log(\'[handleCreateNode] Found queued\', nodeType, \'with number:\', queuedNum);\n' +
            '                                                    if (queuedNum > maxNum) maxNum = queuedNum;\n' +
            '                                                }\n' +
            '                                            }\n' +
            '                                        }\n' +
            '                                    } else {\n' +
            '                                        console.log(\'[handleCreateNode] Queued operation found but DOM element not found for tempNodeId:\', queuedOp.metadata.tempNodeId);\n' +
            '                                    }\n' +
            '                                }\n' +
            '                            }\n' +
            '                        }\n' +
            '                    }\n' +
            '                    \n' +
            '                    placeholderName = baseName + (maxNum + 1);\n' +
            '                    console.log(\'[handleCreateNode] Generated name:\', placeholderName, \'based on maxNum:\', maxNum, \'found names:\', foundNames.join(\', \'));\n' +
            '                }\n' +
            '                \n' +
            '                // Find parent element\n' +
            '                var parentElement = null;\n' +
            '                var parentContainer = null;\n' +
            '                \n' +
            '                if (parentPath === \'story_graph\') {\n' +
            '                    // Creating epic at root - epics are rendered inside #scope-content\n' +
            '                    parentContainer = document.getElementById(\'scope-content\');\n' +
            '                    if (!parentContainer) {\n' +
            '                        // Fallback: try to find card-secondary inside scope-content\n' +
            '                        var scopeContent = document.querySelector(\'#scope-content\');\n' +
            '                        if (scopeContent) {\n' +
            '                            parentContainer = scopeContent.querySelector(\'.card-secondary\');\n' +
            '                        }\n' +
            '                    }\n' +
            '                } else {\n' +
            '                    // Find parent node and its collapsible-content\n' +
            '                    parentElement = findNodeElement(parentPath);\n' +
            '                    if (parentElement) {\n' +
            '                        // Find the collapsible-content div for this parent\n' +
            '                        var parentWrapper = findNodeWrapper(parentElement);\n' +
            '                        if (parentWrapper) {\n' +
            '                            // Look for collapsible-content within or after the wrapper\n' +
            '                            var nextSibling = parentWrapper.nextSibling;\n' +
            '                            while (nextSibling) {\n' +
            '                                if (nextSibling.nodeType === 1 && nextSibling.classList && nextSibling.classList.contains(\'collapsible-content\')) {\n' +
            '                                    parentContainer = nextSibling;\n' +
            '                                    break;\n' +
            '                                }\n' +
            '                                nextSibling = nextSibling.nextSibling;\n' +
            '                            }\n' +
            '                            // If not found after, check if wrapper contains it\n' +
            '                            if (!parentContainer) {\n' +
            '                                parentContainer = parentWrapper.querySelector(\'.collapsible-content\');\n' +
            '                            }\n' +
            '                        }\n' +
            '                    }\n' +
            '                }\n' +
            '                \n' +
            '                if (!parentContainer) {\n' +
            '                    console.error(\'[handleCreateNode] Cannot find parent container for:\', parentPath);\n' +
            '                    // Fallback: refresh the panel\n' +
            '                    if (typeof vscode !== \'undefined\') {\n' +
            '                        vscode.postMessage({ command: \'refresh\' });\n' +
            '                    }\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
            '                // Create real node in DOM immediately\n' +
            '                // Generate a temporary path for the new node (will be updated by backend)\n' +
            '                var tempNodeId = \'temp-\' + Date.now() + \'-\' + Math.random().toString(36).substr(2, 9);\n' +
            '                var tempPath = parentPath === \'story_graph\' \n' +
            '                    ? \'story_graph."\' + placeholderName + \'"\'\n' +
            '                    : parentPath + \'."\' + placeholderName + \'"\';\n' +
            '                \n' +
            '                // Calculate position (append at end)\n' +
            '                var existingChildren = Array.prototype.slice.call(parentContainer.children);\n' +
            '                var position = existingChildren.length;\n' +
            '                \n' +
            '                // Find icon paths from existing DOM elements\n' +
            '                var plusIconPath = null;\n' +
            '                var epicIconPath = null;\n' +
            '                var gearIconPath = null;\n' +
            '                var emptyIconPath = null;\n' +
            '                var documentIconPath = null;\n' +
            '                \n' +
            '                // Find plus icon from existing epic collapse icon\n' +
            '                var existingEpicIcon = document.querySelector(\'#epic-0-icon img.collapse-icon\');\n' +
            '                if (existingEpicIcon) {\n' +
            '                    plusIconPath = existingEpicIcon.src;\n' +
            '                }\n' +
            '                \n' +
            '                // Find epic icon from existing epic\n' +
            '                var existingEpic = document.querySelector(\'.story-node[data-node-type="epic"]\');\n' +
            '                if (existingEpic && existingEpic.previousSibling && existingEpic.previousSibling.tagName === \'IMG\') {\n' +
            '                    epicIconPath = existingEpic.previousSibling.src;\n' +
            '                } else if (existingEpic) {\n' +
            '                    // Look for img before the epic node\n' +
            '                    var parent = existingEpic.parentElement;\n' +
            '                    if (parent) {\n' +
            '                        var epicImg = parent.querySelector(\'img[alt="Epic"]\');\n' +
            '                        if (epicImg) epicIconPath = epicImg.src;\n' +
            '                    }\n' +
            '                }\n' +
            '                \n' +
            '                // Find gear icon from existing sub-epic\n' +
            '                var existingSubEpic = document.querySelector(\'.story-node[data-node-type="sub-epic"]\');\n' +
            '                if (existingSubEpic) {\n' +
            '                    var parent = existingSubEpic.parentElement;\n' +
            '                    if (parent) {\n' +
            '                        var gearImg = parent.querySelector(\'img[alt="Sub-Epic"]\');\n' +
            '                        if (gearImg) gearIconPath = gearImg.src;\n' +
            '                    }\n' +
            '                }\n' +
            '                \n' +
            '                // Find empty icon from existing story without scenarios (uses empty placeholder)\n' +
            '                var existingStory = document.querySelector(\'.story-node[data-node-type="story"]\');\n' +
            '                if (existingStory) {\n' +
            '                    var storyParent = existingStory.parentElement;\n' +
            '                    if (storyParent) {\n' +
            '                        // Look for empty icon span (sibling before story node)\n' +
            '                        var emptySpan = storyParent.querySelector(\'span[style*="min-width: 9px"] img[alt=""]\');\n' +
            '                        if (emptySpan) {\n' +
            '                            emptyIconPath = emptySpan.src;\n' +
            '                        }\n' +
            '                        // Find document icon from story\n' +
            '                        var documentImg = storyParent.querySelector(\'img[alt="Story"]\');\n' +
            '                        if (documentImg) {\n' +
            '                            documentIconPath = documentImg.src;\n' +
            '                        }\n' +
            '                    }\n' +
            '                }\n' +
            '                \n' +
            '                // Use EXACT same margin-top values as backend rendering\n' +
            '                // Backend uses: epic=8px, sub-epic=4px, story=2px, scenario=2px\n' +
            '                var marginTop = nodeType === \'epic\' ? \'8px\' : (nodeType === \'story\' || nodeType === \'scenario\' ? \'2px\' : \'4px\');\n' +
            '                \n' +
            '                // Calculate margin-left by copying from existing sibling (most reliable - uses backend-calculated value)\n' +
            '                // If no sibling exists, calculate using EXACT same formula as backend: marginLeft = 7 + (depth * 7)\n' +
            '                var marginLeft = 0;\n' +
            '                if (nodeType === \'epic\') {\n' +
            '                    marginLeft = 0;\n' +
            '                } else if (parentContainer) {\n' +
            '                    // First: try to find an existing node of the same type and copy its margin-left\n' +
            '                    // This ensures we use the exact same value the backend calculated\n' +
            '                    var existingNodeDiv = null;\n' +
            '                    var containerChildren = Array.prototype.slice.call(parentContainer.children);\n' +
            '                    for (var i = 0; i < containerChildren.length; i++) {\n' +
            '                        var child = containerChildren[i];\n' +
            '                        var matchingNode = child.querySelector ? child.querySelector(\'.story-node[data-node-type="\' + nodeType + \'"]\') : null;\n' +
            '                        if (matchingNode) {\n' +
            '                            existingNodeDiv = child;\n' +
            '                            break;\n' +
            '                        }\n' +
            '                    }\n' +
            '                    \n' +
            '                    if (existingNodeDiv && existingNodeDiv.style && existingNodeDiv.style.marginLeft) {\n' +
            '                        // Copy exact margin-left from existing node (already calculated by backend)\n' +
            '                        var existingMargin = existingNodeDiv.style.marginLeft;\n' +
            '                        var marginMatch = existingMargin.match(/(\\d+)px/);\n' +
            '                        if (marginMatch) {\n' +
            '                            marginLeft = parseInt(marginMatch[1], 10);\n' +
            '                            console.log(\'[handleCreateNode] Copied margin-left from existing node:\', marginLeft, \'px\');\n' +
            '                        }\n' +
            '                    }\n' +
            '                    \n' +
            '                    // Fallback: calculate using backend formula if no existing node found\n' +
            '                    if (!existingNodeDiv || !marginLeft) {\n' +
            '                        if (nodeType === \'sub-epic\') {\n' +
            '                            // Backend formula: marginLeft = 7 + (depth * 7)\n' +
            '                            // Calculate depth by counting sub-epic ancestors\n' +
            '                            var depth = 0;\n' +
            '                            if (parentElement) {\n' +
            '                                var parentType = parentElement.getAttribute ? parentElement.getAttribute(\'data-node-type\') : null;\n' +
            '                                if (parentType === \'sub-epic\') {\n' +
            '                                    // Parent is a sub-epic, so we need to find its depth\n' +
            '                                    var parentWrapper = findNodeWrapper(parentElement);\n' +
            '                                    console.log(\'[handleCreateNode] Parent wrapper found:\', !!parentWrapper, \'parentType:\', parentType);\n' +
            '                                    if (parentWrapper) {\n' +
            '                                        // Try multiple ways to read margin-left (cssText, style.marginLeft, computed style)\n' +
            '                                        var parentMarginLeft = 0;\n' +
            '                                        if (parentWrapper.style && parentWrapper.style.marginLeft) {\n' +
            '                                            var parentMargin = parentWrapper.style.marginLeft;\n' +
            '                                            var parentMatch = parentMargin.match(/(\\d+)px/);\n' +
            '                                            if (parentMatch) {\n' +
            '                                                parentMarginLeft = parseInt(parentMatch[1], 10);\n' +
            '                                            }\n' +
            '                                        }\n' +
            '                                        // Fallback: try reading from cssText\n' +
            '                                        if (!parentMarginLeft && parentWrapper.style && parentWrapper.style.cssText) {\n' +
            '                                            var cssTextMatch = parentWrapper.style.cssText.match(/margin-left:\\s*(\\d+)px/);\n' +
            '                                            if (cssTextMatch) {\n' +
            '                                                parentMarginLeft = parseInt(cssTextMatch[1], 10);\n' +
            '                                            }\n' +
            '                                        }\n' +
            '                                        // Fallback: try computed style\n' +
            '                                        if (!parentMarginLeft && typeof window.getComputedStyle !== \'undefined\') {\n' +
            '                                            try {\n' +
            '                                                var computedStyle = window.getComputedStyle(parentWrapper);\n' +
            '                                                var computedMargin = computedStyle.marginLeft;\n' +
            '                                                var computedMatch = computedMargin.match(/(\\d+)px/);\n' +
            '                                                if (computedMatch) {\n' +
            '                                                    parentMarginLeft = parseInt(computedMatch[1], 10);\n' +
            '                                                }\n' +
            '                                            } catch (e) {\n' +
            '                                                console.warn(\'[handleCreateNode] Error reading computed style:\', e);\n' +
            '                                            }\n' +
            '                                        }\n' +
            '                                        \n' +
            '                                        console.log(\'[handleCreateNode] Parent margin-left read:\', parentMarginLeft, \'px\');\n' +
            '                                        \n' +
            '                                        if (parentMarginLeft >= 7) {\n' +
            '                                            // Calculate parent\'s depth: parentMarginLeft = 7 + (parentDepth * 7)\n' +
            '                                            // So: parentDepth = (parentMarginLeft - 7) / 7\n' +
            '                                            var parentDepth = (parentMarginLeft - 7) / 7;\n' +
            '                                            // Our depth is parent depth + 1\n' +
            '                                            depth = parentDepth + 1;\n' +
            '                                            console.log(\'[handleCreateNode] Calculated parentDepth:\', parentDepth, \'new depth:\', depth);\n' +
            '                                        } else if (parentMarginLeft === 0) {\n' +
            '                                            // Parent is epic (margin-left 0), so depth is 0\n' +
            '                                            depth = 0;\n' +
            '                                            console.log(\'[handleCreateNode] Parent is epic (margin-left 0), depth:\', depth);\n' +
            '                                        } else {\n' +
            '                                            // Unexpected margin-left value, try to infer depth\n' +
            '                                            console.warn(\'[handleCreateNode] Unexpected parent margin-left:\', parentMarginLeft, \'assuming depth 1\');\n' +
            '                                            depth = 1;\n' +
            '                                        }\n' +
            '                                    } else {\n' +
            '                                        // Parent wrapper not found, try to infer from parent type\n' +
            '                                        console.warn(\'[handleCreateNode] Parent wrapper not found for sub-epic parent, assuming depth 1\');\n' +
            '                                        depth = 1;\n' +
            '                                    }\n' +
            '                                } else if (parentType === \'epic\') {\n' +
            '                                    // Parent is epic, so depth is 0\n' +
            '                                    depth = 0;\n' +
            '                                }\n' +
            '                            }\n' +
            '                            // Use EXACT same formula as backend: marginLeft = 7 + (depth * 7)\n' +
            '                            marginLeft = 7 + (depth * 7);\n' +
            '                            console.log(\'[handleCreateNode] Calculated depth:\', depth, \'marginLeft:\', marginLeft, \'px (backend formula: 7 + (depth * 7))\');\n' +
            '                        } else {\n' +
            '                            // For stories: use parent\'s margin + 7\n' +
            '                            if (parentElement) {\n' +
            '                                var parentWrapper = findNodeWrapper(parentElement);\n' +
            '                                if (parentWrapper && parentWrapper.style && parentWrapper.style.marginLeft) {\n' +
            '                                    var parentMargin = parentWrapper.style.marginLeft;\n' +
            '                                    var parentMatch = parentMargin.match(/(\\d+)px/);\n' +
            '                                    if (parentMatch) {\n' +
            '                                        marginLeft = parseInt(parentMatch[1], 10) + 7;\n' +
            '                                    } else {\n' +
            '                                        marginLeft = 14;\n' +
            '                                    }\n' +
            '                                } else {\n' +
            '                                    marginLeft = 14;\n' +
            '                                }\n' +
            '                            } else {\n' +
            '                                marginLeft = 14;\n' +
            '                            }\n' +
            '                        }\n' +
            '                    }\n' +
            '                } else {\n' +
            '                    // No parent container - use defaults\n' +
            '                    marginLeft = nodeType === \'epic\' ? 0 : (nodeType === \'sub-epic\' ? 7 : 14);\n' +
            '                }\n' +
            '                \n' +
            '                // Create collapse icon span OR empty placeholder (matching backend logic)\n' +
            '                // Backend: Only show collapse icon if node has children, otherwise use empty placeholder\n' +
            '                // Since this is a new node, it has no children yet, so use empty placeholder\n' +
            '                var collapseIconSpan = document.createElement(\'span\');\n' +
            '                var collapsibleId = tempNodeId + \'-content\';\n' +
            '                collapseIconSpan.style.cssText = \'display: inline-block; min-width: 9px;\';\n' +
            '                \n' +
            '                // New nodes don\'t have children yet, so use empty placeholder (matches backend line 2266)\n' +
            '                if (emptyIconPath) {\n' +
            '                    var emptyImg = document.createElement(\'img\');\n' +
            '                    emptyImg.src = emptyIconPath;\n' +
            '                    emptyImg.style.cssText = \'width: 9px; height: 9px; vertical-align: middle;\';\n' +
            '                    emptyImg.alt = \'\';\n' +
            '                    collapseIconSpan.appendChild(emptyImg);\n' +
            '                } else {\n' +
            '                    // Fallback: create empty span with same width if icon not found\n' +
            '                    collapseIconSpan.style.cssText = \'display: inline-block; min-width: 9px;\';\n' +
            '                }\n' +
            '                \n' +
            '                // Create icon image (epic, gear, or document) - matching backend logic\n' +
            '                var iconImg = null;\n' +
            '                if (nodeType === \'epic\' && epicIconPath) {\n' +
            '                    iconImg = document.createElement(\'img\');\n' +
            '                    iconImg.src = epicIconPath;\n' +
            '                    iconImg.style.cssText = \'width: 14px; height: 14px; vertical-align: middle; margin-right: 4px;\';\n' +
            '                    iconImg.alt = \'Epic\';\n' +
            '                } else if (nodeType === \'sub-epic\' && gearIconPath) {\n' +
            '                    iconImg = document.createElement(\'img\');\n' +
            '                    iconImg.src = gearIconPath;\n' +
            '                    iconImg.style.cssText = \'width: 14px; height: 14px; vertical-align: middle; margin-right: 4px;\';\n' +
            '                    iconImg.alt = \'Sub-Epic\';\n' +
            '                } else if (nodeType === \'story\' && documentIconPath) {\n' +
            '                    // Stories always get document icon (backend line 2250, 2275)\n' +
            '                    iconImg = document.createElement(\'img\');\n' +
            '                    iconImg.src = documentIconPath;\n' +
            '                    iconImg.style.cssText = \'width: 14px; height: 14px; vertical-align: middle; margin-right: 4px;\';\n' +
            '                    iconImg.alt = \'Story\';\n' +
            '                }\n' +
            '                \n' +
            '                // Create story-node span\n' +
            '                var nodeSpan = document.createElement(\'span\');\n' +
            '                nodeSpan.className = \'story-node\';\n' +
            '                nodeSpan.setAttribute(\'draggable\', \'true\');\n' +
            '                nodeSpan.setAttribute(\'data-node-type\', nodeType);\n' +
            '                nodeSpan.setAttribute(\'data-node-name\', placeholderName);\n' +
            '                nodeSpan.setAttribute(\'data-path\', tempPath);\n' +
            '                nodeSpan.setAttribute(\'data-position\', position.toString());\n' +
            '                nodeSpan.setAttribute(\'data-has-children\', \'false\');\n' +
            '                nodeSpan.style.cssText = \'cursor: pointer;\';\n' +
            '                // For stories: icon goes INSIDE the span (backend line 2275: ${storyIcon}${name})\n' +
            '                // For epics/sub-epics: icon goes OUTSIDE the span\n' +
            '                if (nodeType === \'story\' && iconImg) {\n' +
            '                    nodeSpan.appendChild(iconImg);\n' +
            '                    nodeSpan.appendChild(document.createTextNode(placeholderName));\n' +
            '                } else {\n' +
            '                    nodeSpan.textContent = placeholderName;\n' +
            '                }\n' +
            '                \n' +
            '                // Add click handler for selection\n' +
            '                nodeSpan.onclick = function() {\n' +
            '                    if (typeof selectNode === \'function\') {\n' +
            '                        selectNode(nodeType, placeholderName, { path: tempPath });\n' +
            '                    }\n' +
            '                };\n' +
            '                \n' +
            '                // Create status message span\n' +
            '                var statusSpan = document.createElement(\'span\');\n' +
            '                statusSpan.id = tempNodeId + \'-status\';\n' +
            '                statusSpan.style.cssText = \'font-size: 11px; color: #666; font-style: italic; margin-left: 8px;\';\n' +
            '                // Use the actual placeholderName in the status message\n' +
            '                statusSpan.textContent = placeholderName + \' creating...\';\n' +
            '                \n' +
            '                // Build the node structure matching epic/sub-epic format\n' +
            '                // For epics: <div style="margin-top: 8px">...</div> followed by <div class="collapsible-content">...</div>\n' +
            '                // For sub-epics: similar but with margin-left\n' +
            '                \n' +
            '                // Create the main node line div (matches exact backend structure)\n' +
            '                // Backend format: <div style="margin-left: Xpx; margin-top: 4px; font-size: 12px;">\n' +
            '                //                <span id="...-icon" ...><img .../></span> ${icon}${nameHtml}\n' +
            '                //                </div>\n' +
            '                var nodeLineDiv = document.createElement(\'div\');\n' +
            '                // Use exact same style format as backend: margin-left in px, margin-top in px, font-size: 12px\n' +
            '                nodeLineDiv.style.cssText = \'margin-left: \' + marginLeft + \'px; margin-top: \' + marginTop + \'; font-size: 12px;\';\n' +
            '                \n' +
            '                // Build structure EXACTLY like backend: collapse icon span, SPACE, then icon img (for epics/sub-epics), then node span\n' +
            '                // For stories: icon goes INSIDE the node span (backend line 2275: ${storyIcon}${name})\n' +
            '                // Backend format: </span> ${icon}${name} - note the space after </span>\n' +
            '                nodeLineDiv.appendChild(collapseIconSpan);\n' +
            '                // Add space text node to match backend rendering (space between collapse icon and gear/epic icon)\n' +
            '                // For epics and sub-epics: icon is outside span, for stories: icon is inside span\n' +
            '                if (iconImg && nodeType !== \'story\') {\n' +
            '                    nodeLineDiv.appendChild(document.createTextNode(\' \'));\n' +
            '                    nodeLineDiv.appendChild(iconImg);\n' +
            '                }\n' +
            '                nodeLineDiv.appendChild(nodeSpan);\n' +
            '                // Add status span after node name (doesn\'t affect collapse icon alignment)\n' +
            '                nodeLineDiv.appendChild(statusSpan);\n' +
            '                \n' +
            '                // Insert node line at end of parent container\n' +
            '                parentContainer.appendChild(nodeLineDiv);\n' +
            '                \n' +
            '                // For epics and sub-epics, add empty collapsible-content div as sibling\n' +
            '                if (collapsibleId) {\n' +
            '                    var collapsibleDiv = document.createElement(\'div\');\n' +
            '                    collapsibleDiv.id = collapsibleId;\n' +
            '                    collapsibleDiv.className = \'collapsible-content\';\n' +
            '                    collapsibleDiv.style.display = \'none\';\n' +
            '                    // Insert as sibling after nodeLineDiv\n' +
            '                    parentContainer.appendChild(collapsibleDiv);\n' +
            '                }\n' +
            '                \n' +
            '                // Store nodeLineDiv ID in metadata for rollback\n' +
            '                nodeLineDiv.id = tempNodeId;\n' +
            '                \n' +
            '                // Build command (include placeholderName so backend uses same name as frontend)\n' +
            '                var command = buildCreateCommand(parentPath, nodeType, placeholderName);\n' +
            '                \n' +
            '                // Validate command - if null, the operation is invalid\n' +
            '                if (!command) {\n' +
            '                    console.error(\'[handleCreateNode] Invalid create command for\', nodeType, \'on\', parentPath);\n' +
            '                    // Remove optimistically created node\n' +
            '                    var createdNode = document.getElementById(tempNodeId);\n' +
            '                    if (createdNode) {\n' +
            '                        createdNode.remove();\n' +
            '                    }\n' +
            '                    var collapsibleNode = document.getElementById(tempNodeId + \'-content\');\n' +
            '                    if (collapsibleNode) {\n' +
            '                        collapsibleNode.remove();\n' +
            '                    }\n' +
            '                    // Show error message to user\n' +
            '                    var errorMsg = \'Cannot create \' + nodeType + \' on Story Map root. Please select an epic or sub-epic first.\';\n' +
            '                    if (typeof vscode !== \'undefined\') {\n' +
            '                        vscode.postMessage({\n' +
            '                            type: \'showErrorDialog\',\n' +
            '                            title: \'Invalid Operation\',\n' +
            '                            message: errorMsg\n' +
            '                        });\n' +
            '                    } else {\n' +
            '                        alert(errorMsg);\n' +
            '                    }\n' +
            '                    return;\n' +
            '                }\n' +
            '                \n' +
            '                // Update parent\'s collapse icon if this is its first child\n' +
            '                // Only update for nodes that can have children (epics, sub-epics, stories with scenarios)\n' +
            '                if (parentPath !== \'story_graph\' && (nodeType === \'sub-epic\' || nodeType === \'story\' || nodeType === \'scenario\')) {\n' +
            '                    updateParentCollapseIcon(parentPath);\n' +
            '                }\n' +
            '                \n' +
            '                // Queue save\n' +
            '                if (window.storyMapSaveQueue) {\n' +
            '                    window.storyMapSaveQueue.enqueue({\n' +
            '                        command: command,\n' +
            '                        rollback: function() {\n' +
            '                            // Remove created node on error (both node line and collapsible-content)\n' +
            '                            var createdNode = document.getElementById(tempNodeId);\n' +
            '                            if (createdNode) {\n' +
            '                                createdNode.remove();\n' +
            '                            }\n' +
            '                            var collapsibleNode = document.getElementById(tempNodeId + \'-content\');\n' +
            '                            if (collapsibleNode) {\n' +
            '                                collapsibleNode.remove();\n' +
            '                            }\n' +
            '                            // If this was the parent\'s only child, restore empty placeholder\n' +
            '                            // (This is complex - for now, just leave the collapse icon)\n' +
            '                        },\n' +
            '                        metadata: {\n' +
            '                            operation: \'create\',\n' +
            '                            parentPath: parentPath,\n' +
            '                            nodeType: nodeType,\n' +
            '                            tempNodeId: tempNodeId\n' +
            '                        }\n' +
            '                    });\n' +
            '                } else {\n' +
            '                    console.error(\'[handleCreateNode] storyMapSaveQueue not available\');\n' +
            '                }\n' +
            '            };\n' +
            '        })();\n';
        
        const result = `
    <div class="section scope-section card-primary">
        <div class="collapsible-section expanded">
            <div class="collapsible-header" onclick="toggleSection('scope-content')" style="
                cursor: pointer;
                padding: 4px 5px;
                background-color: transparent;
                border-left: none;
                border-radius: 2px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                user-select: none;
            ">
                <div style="display: flex; align-items: center; flex: 1;">
                    <span class="expand-icon" style="margin-right: 8px; font-size: 28px; transition: transform 0.15s;">▸</span>
                    ${magnifyingGlassIconPath ? `<img src="${magnifyingGlassIconPath}" style="margin-right: 8px; width: 28px; height: 28px; object-fit: contain;" alt="Story Map Icon" />` : ''}
                    <span style="font-weight: 600; font-size: 20px;">Story Map</span>
                    <div style="flex: 1;"></div>
                    ${showAllIconPath ? `<button onclick="event.stopPropagation(); showAllScope();" style="
                        background: transparent;
                        border: none;
                        padding: 4px 8px;
                        margin-left: 12px;
                        cursor: pointer;
                        display: flex;
                        align-items: center;
                        transition: opacity 0.15s ease;
                    " 
                    onmouseover="this.style.opacity='0.7'" 
                    onmouseout="this.style.opacity='1'"
                    title="Show all scope (scope showall)">
                        <img src="${showAllIconPath}" style="width: 28px; height: 28px; object-fit: contain;" alt="Show All" />
                    </button>` : ''}
                    ${hasFilter && clearIconPath ? `<button onclick="event.stopPropagation(); clearScopeFilter();" style="
                        background: transparent;
                        border: none;
                        padding: 4px 8px;
                        margin-left: 6px;
                        cursor: pointer;
                        display: flex;
                        align-items: center;
                        transition: opacity 0.15s ease;
                    " 
                    onmouseover="this.style.opacity='0.7'" 
                    onmouseout="this.style.opacity='1'"
                    title="Clear scope filter (show all)">
                        <img src="${clearIconPath}" style="width: 24px; height: 24px; object-fit: contain;" alt="Clear Filter" />
                    </button>` : hasFilter ? `<button onclick="event.stopPropagation(); clearScopeFilter();" style="
                        background: transparent;
                        border: none;
                        padding: 4px 8px;
                        margin-left: 6px;
                        cursor: pointer;
                        display: flex;
                        align-items: center;
                        transition: opacity 0.15s ease;
                    " 
                    onmouseover="this.style.opacity='0.7'" 
                    onmouseout="this.style.opacity='1'"
                    title="Clear scope filter (show all)">
                        ✕
                    </button>` : ''}
                </div>
                <div onclick="event.stopPropagation();" style="display: flex; align-items: center;">
                    <div id="save-status-indicator" class="save-status" style="display: none; margin-left: 12px;">
                        <span class="save-icon"></span>
                        <span class="save-message"></span>
                    </div>
                    ${linksHtml}
                    ${permanentLinksHtml}
                </div>
            </div>
            <div id="scope-content" class="collapsible-content" style="max-height: 2000px; overflow: hidden; transition: max-height 0.3s ease;">
                <div class="card-secondary" style="padding: 5px;">
                    <div class="input-container" style="margin-bottom: 6px;">
                        <div class="input-header">Filter</div>
                        <input type="text" id="scopeFilterInput" 
                               value="${filterValue}" 
                               placeholder="Epic or Story name"
                               onchange="console.log('[ScopeInput] onchange fired with:', this.value); updateFilter(this.value)"
                               onkeydown="console.log('[ScopeInput] Key pressed:', event.key, 'Value:', this.value); if(event.key === 'Enter') { event.preventDefault(); console.log('[ScopeInput] Enter key - calling updateFilter'); updateFilter(this.value); }" />
                    </div>
                    ${contentHtml}
                </div>
            </div>
        </div>
    </div>
    <script>
${clientScript}    </script>`;
        const perfAssemblyEnd = performance.now();
        log(`[StoryMapView] [PERF] HTML assembly: ${(perfAssemblyEnd - perfAssemblyStart).toFixed(2)}ms`);
        
        // ===== PERFORMANCE: Log total render time =====
        const perfRenderEnd = performance.now();
        const totalRenderTime = (perfRenderEnd - perfRenderStart).toFixed(2);
        log(`[StoryMapView] [PERF] TOTAL render() duration: ${totalRenderTime}ms`);
        
        return result;
    }
    
    /**
     * Render root "Story Map" node with contextual action buttons.
     * 
     * @param {string} actionButtonsHtml - HTML for contextual action buttons
     * @returns {string} HTML string
     */
    renderRootNode(actionButtonsHtml) {
        return `<div style="margin-top: 8px; margin-bottom: 4px; font-size: 12px; font-weight: 600; display: flex; align-items: center;">
            <span class="story-node" data-node-type="root" data-node-name="Story Map" style="display: inline-block; cursor: pointer;" onclick="selectNode('root', null)">Story Map</span>
            ${actionButtonsHtml}
        </div>`;
    }
    
    /**
     * Render story tree (epics -> sub-epics -> stories -> scenarios).
     * 
     * @param {Array} epics - Epics array
     * @returns {string} HTML string
     */
    renderStoryTree(epics, gearIconPath, epicIconPath, pageIconPath, testTubeIconPath, documentIconPath, plusIconPath, subtractIconPath, emptyIconPath) {
        return epics.map((epic, epicIndex) => {
            const epicId = `epic-${epicIndex}`;
            const epicIcon = epicIconPath ? `<img src="${epicIconPath}" style="width: 14px; height: 14px; vertical-align: middle; margin-right: 4px;" alt="Epic" />` : '';
            
            // Find document and test links for epic
            const epicDocLink = epic.links && epic.links.find(l => l.icon === 'document');
            const epicTestLink = epic.links && epic.links.find(l => l.icon === 'test_tube');
            
            // Check if epic has children
            const epicHasChildren = (epic.sub_epics && epic.sub_epics.length > 0) || (epic.story_groups && epic.story_groups.some(sg => sg.stories && sg.stories.length > 0));
            
            // Make epic name a hyperlink if document exists, clickable to select, double-click to edit
            // CRITICAL: Escape the ENTIRE path including quotes - HTML parser stops at unescaped quotes
            const epicPath = this.escapeHtml(`story_graph."${epic.name}"`);
            const epicBehavior = epic.behavior_needed || '';
            const epicNameHtml = epicDocLink
                ? `<span class="story-node" draggable="true" data-node-type="epic" data-node-name="${this.escapeHtml(epic.name)}" data-behavior-needed="${epicBehavior}" data-has-children="${epicHasChildren}" data-position="${epicIndex}" data-path="${epicPath}" data-file-link="${this.escapeHtml(epicDocLink.url)}" style="text-decoration: underline; cursor: pointer;">${this.escapeHtml(epic.name)}</span>`
                : `<span class="story-node" draggable="true" data-node-type="epic" data-node-name="${this.escapeHtml(epic.name)}" data-behavior-needed="${epicBehavior}" data-has-children="${epicHasChildren}" data-position="${epicIndex}" data-path="${epicPath}" style="cursor: pointer;">${this.escapeHtml(epic.name)}</span>`;
            
            // Render test tube icon for epic test link
            const epicTestIcon = (epicTestLink && testTubeIconPath)
                ? ` <span onclick="openFile('${this.escapeForJs(epicTestLink.url)}')" style="cursor: pointer;"><img src="${testTubeIconPath}" style="width: 20px; height: 20px; vertical-align: middle;" alt="Test" /></span>`
                : '';
            
            // Epic nodes - no inline action buttons (all actions are in the toolbar)
            let html = `<div style="margin-top: 8px; font-size: 12px;"><span id="${epicId}-icon" onclick="event.stopPropagation(); toggleCollapse('${epicId}')" style="display: inline-block; min-width: 9px; cursor: pointer;" data-plus="${plusIconPath}" data-subtract="${subtractIconPath}"><img class="collapse-icon" src="${plusIconPath}" data-state="collapsed" style="width: 9px; height: 9px; vertical-align: middle;" alt="Expand" /></span> ${epicIcon}${epicNameHtml}${epicTestIcon}</div>`;
            
            html += `<div id="${epicId}" class="collapsible-content" style="display: none;">`;
            // Helper function to recursively render a sub-epic (can be nested any number of levels)
            const renderSubEpic = (subEpic, subEpicIndex, parentPath, depth = 0, parentStoryGraphPath = null) => {
                const subEpicId = `${parentPath}-${subEpicIndex}`;
                const subEpicIcon = gearIconPath ? `<img src="${gearIconPath}" style="width: 14px; height: 14px; vertical-align: middle; margin-right: 4px;" alt="Sub-Epic" />` : '';
                
                // Find document and test links
                const subEpicDocLink = subEpic.links && subEpic.links.find(l => l.icon === 'document');
                const subEpicTestLink = subEpic.links && subEpic.links.find(l => l.icon === 'test_tube');
                
                // Build the full path to this SubEpic
                // For first-level: story_graph."Epic"."SubEpic"
                // For nested: story_graph."Epic"."ParentSubEpic"."NestedSubEpic"
                // CRITICAL: Escape the ENTIRE path including quotes - HTML parser stops at unescaped quotes
                const baseStoryGraphPath = parentStoryGraphPath || `story_graph."${epic.name}"`;
                const subEpicPath = this.escapeHtml(`${baseStoryGraphPath}."${subEpic.name}"`);
                
                // Determine which buttons to show for SubEpic based on children
                const nestedSubEpics = subEpic.sub_epics || [];
                const hasStories = subEpic.story_groups && subEpic.story_groups.some(sg => sg.stories && sg.stories.length > 0);
                const hasNestedSubEpics = nestedSubEpics.length > 0;
                const hasNoChildren = !hasStories && !hasNestedSubEpics;
                const subEpicHasChildren = hasStories || hasNestedSubEpics;
                
                // Make sub-epic name a hyperlink if document exists, clickable to select, double-click to edit
                const subEpicBehavior = subEpic.behavior_needed || '';
                const subEpicNameHtml = subEpicDocLink
                    ? `<span class="story-node" draggable="true" data-node-type="sub-epic" data-node-name="${this.escapeHtml(subEpic.name)}" data-behavior-needed="${subEpicBehavior}" data-has-children="${subEpicHasChildren}" data-has-stories="${hasStories}" data-has-nested-sub-epics="${hasNestedSubEpics}" data-position="${subEpicIndex}" data-path="${subEpicPath}" data-file-link="${this.escapeHtml(subEpicDocLink.url)}" style="text-decoration: underline; cursor: pointer;">${this.escapeHtml(subEpic.name)}</span>`
                    : `<span class="story-node" draggable="true" data-node-type="sub-epic" data-node-name="${this.escapeHtml(subEpic.name)}" data-behavior-needed="${subEpicBehavior}" data-has-children="${subEpicHasChildren}" data-has-stories="${hasStories}" data-has-nested-sub-epics="${hasNestedSubEpics}" data-position="${subEpicIndex}" data-path="${subEpicPath}" style="cursor: pointer;">${this.escapeHtml(subEpic.name)}</span>`;
                
                // Only render test tube icon for test links
                const subEpicTestIcon = (subEpicTestLink && testTubeIconPath)
                    ? ` <span onclick="openFile('${this.escapeForJs(subEpicTestLink.url)}')" style="cursor: pointer;"><img src="${testTubeIconPath}" style="width: 20px; height: 20px; vertical-align: middle;" alt="Test" /></span>`
                    : '';
                
                // No inline action buttons (all actions are in the toolbar)
                const marginLeft = 7 + (depth * 7); // Increase margin for nested sub-epics
                
                html += `<div style="margin-left: ${marginLeft}px; margin-top: 4px; font-size: 12px;"><span id="${subEpicId}-icon" onclick="event.stopPropagation(); toggleCollapse('${subEpicId}')" style="display: inline-block; min-width: 9px; cursor: pointer;" data-plus="${plusIconPath}" data-subtract="${subtractIconPath}"><img class="collapse-icon" src="${plusIconPath}" data-state="collapsed" style="width: 9px; height: 9px; vertical-align: middle;" alt="Expand" /></span> ${subEpicIcon}${subEpicNameHtml}${subEpicTestIcon}</div>`;
                
                html += `<div id="${subEpicId}" class="collapsible-content" style="display: none;">`;
                
                // Render nested sub_epics if they exist (recursive)
                // Pass the current sub-epic's full path as the parent for nested children
                if (nestedSubEpics.length > 0) {
                    const currentSubEpicStoryGraphPath = `${baseStoryGraphPath}."${subEpic.name}"`;
                    nestedSubEpics.forEach((nested, nestedIndex) => {
                        renderSubEpic(nested, nestedIndex, subEpicId, depth + 1, currentSubEpicStoryGraphPath);
                    });
                }
                
                // Render story_groups with stories if they exist
                if (subEpic.story_groups && subEpic.story_groups.length > 0) {
                    subEpic.story_groups.forEach(storyGroup => {
                        if (storyGroup.stories && storyGroup.stories.length > 0) {
                            storyGroup.stories.forEach((story, storyIndex) => {
                                const storyId = `${subEpicId}-story-${storyIndex}`;
                                const storyIcon = documentIconPath ? `<img src="${documentIconPath}" style="width: 14px; height: 14px; vertical-align: middle; margin-right: 4px;" alt="Story" />` : '';
                                
                                // Check if story has scenarios - if so, make it collapsible
                                const hasScenarios = story.scenarios && story.scenarios.length > 0;
                                
                                // Build story path for edit mode - use full parent chain for nested sub-epics
                                // CRITICAL: Escape the ENTIRE path including quotes - HTML parser stops at unescaped quotes
                                const storyPath = this.escapeHtml(`${baseStoryGraphPath}."${subEpic.name}"."${story.name}"`);
                                
                                html += `<div style="margin-left: ${marginLeft + 7}px; margin-top: 2px; font-size: 12px;">`;
                                
                                if (hasScenarios) {
                                    // Collapsible story with scenarios - only icon is clickable
                                    html += `<span id="${storyId}-icon" onclick="event.stopPropagation(); toggleCollapse('${storyId}')" style="display: inline-block; min-width: 9px; cursor: pointer;" data-plus="${plusIconPath}" data-subtract="${subtractIconPath}"><img class="collapse-icon" src="${plusIconPath}" data-state="collapsed" style="width: 9px; height: 9px; vertical-align: middle;" alt="Expand" /></span> `;
                                } else {
                                    // Empty placeholder for alignment
                                    html += `<span style="display: inline-block; min-width: 9px;"><img src="${emptyIconPath}" style="width: 9px; height: 9px; vertical-align: middle;" alt="" /></span> `;
                                }
                                
                                // Find story doc link (if exists)
                                const storyDocLink = story.links && story.links.find(l => l.text === 'story');
                                
                                // Story name with double-click to edit, clickable to select
                                const storyBehavior = story.behavior_needed || '';
                                if (storyDocLink) {
                                    html += `<span class="story-node" draggable="true" data-node-type="story" data-node-name="${this.escapeHtml(story.name)}" data-behavior-needed="${storyBehavior}" data-has-children="${hasScenarios}" data-position="${storyIndex}" data-path="${storyPath}" data-file-link="${this.escapeHtml(storyDocLink.url)}" style="text-decoration: underline; cursor: pointer;">${storyIcon}${this.escapeHtml(story.name)}</span>`;
                                } else {
                                    html += `<span class="story-node" draggable="true" data-node-type="story" data-node-name="${this.escapeHtml(story.name)}" data-behavior-needed="${storyBehavior}" data-has-children="${hasScenarios}" data-position="${storyIndex}" data-path="${storyPath}" style="cursor: pointer;">${storyIcon}${this.escapeHtml(story.name)}</span>`;
                                }
                                
                                // Render test tube icon for test link
                                if (story.links && story.links.length > 0) {
                                    const testLink = story.links.find(l => l.icon === 'test_tube');
                                    if (testLink && testTubeIconPath) {
                                        html += ` <span onclick="openFile('${this.escapeForJs(testLink.url)}')" style="cursor: pointer;"><img src="${testTubeIconPath}" style="width: 20px; height: 20px; vertical-align: middle;" alt="Test" /></span>`;
                                    }
                                }
                                
                                // No inline action buttons (all actions are in the toolbar)
                                html += '</div>';
                                
                                // Render scenarios if they exist
                                if (hasScenarios) {
                                    html += `<div id="${storyId}" class="collapsible-content" style="display: none;">`;
                                    story.scenarios.forEach((scenario, scenarioIndex) => {
                                        html += `<div style="margin-left: ${marginLeft + 21}px; margin-top: 2px; font-size: 12px;">`;
                                        
                                        // Empty placeholder for alignment (scenarios don't have children)
                                        html += `<span style="display: inline-block; min-width: 9px;"><img src="${emptyIconPath}" style="width: 9px; height: 9px; vertical-align: middle;" alt="" /></span> `;
                                        
                                        // Create scenario anchor ID from scenario name (matches synchronizer format)
                                        const scenarioAnchor = this.createScenarioAnchor(scenario.name);
                                        // CRITICAL: Escape the ENTIRE path including quotes - HTML parser stops at unescaped quotes
                                        const scenarioPath = this.escapeHtml(`${baseStoryGraphPath}."${subEpic.name}"."${story.name}"."${scenario.name}"`);
                                        
                                        // Link scenario name to story file with scenario anchor
                                        // Make scenarios draggable and renameable like other nodes
                                        const scenarioBehavior = scenario.behavior_needed || '';
                                        if (storyDocLink) {
                                            const scenarioLink = `${storyDocLink.url}#${scenarioAnchor}`;
                                            html += `<span class="story-node" draggable="true" data-node-type="scenario" data-node-name="${this.escapeHtml(scenario.name)}" data-behavior-needed="${scenarioBehavior}" data-has-children="false" data-position="${scenarioIndex}" data-path="${scenarioPath}" data-file-link="${this.escapeHtml(scenarioLink)}" style="text-decoration: underline; cursor: pointer;">${this.escapeHtml(scenario.name)}</span>`;
                                        } else {
                                            // No story doc link - just display scenario name with drag/rename support
                                            html += `<span class="story-node" draggable="true" data-node-type="scenario" data-node-name="${this.escapeHtml(scenario.name)}" data-behavior-needed="${scenarioBehavior}" data-has-children="false" data-position="${scenarioIndex}" data-path="${scenarioPath}" style="cursor: pointer;">${this.escapeHtml(scenario.name)}</span>`;
                                        }
                                        
                                        // Render test tube icon for test link (separate from scenario name link)
                                        // Scenarios have test_method, backend sets test_file with full path + anchor when test_method exists
                                        if (scenario.test_file && testTubeIconPath) {
                                            html += ` <span onclick="openFile('${this.escapeForJs(scenario.test_file)}')" style="cursor: pointer;"><img src="${testTubeIconPath}" style="width: 20px; height: 20px; vertical-align: middle;" alt="Test" /></span>`;
                                        }
                                        
                                        html += '</div>';
                                    });
                                    html += '</div>'; // Close scenario collapsible-content
                                }
                            });
                        }
                    });
                }
                
                html += '</div>'; // Close sub-epic collapsible-content
            };
            
            // Render sub-epics under this epic
            const subEpics = epic.sub_epics || [];
            subEpics.forEach((subEpic, subEpicIndex) => {
                renderSubEpic(subEpic, subEpicIndex, `epic-${epicIndex}`, 0);
            });
            html += '</div>'; // Close epic collapsible-content
            
            return html;
        }).join('');
    }
    
    /**
     * Render file list.
     * 
     * @param {Array} files - Files array
     * @returns {string} HTML string
     */
    renderFileList(files) {
        return '<div style="margin-top: 5px;">' + files.map(file => 
            `<div style="margin-left: 5px; font-family: monospace; font-size: 12px; margin-top: 2px;">- ${this.escapeHtml(file.path)}</div>`
        ).join('') + '</div>';
    }
    
    
    /**
     * Handle events.
     * 
     * @param {string} eventType - Event type
     * @param {Object} eventData - Event data
     * @returns {Promise<Object>} Result
     */
    async handleEvent(eventType, eventData) {
        if (eventType === 'updateFilter') {
            const filterValue = eventData.filter || '';
            // Execute scope command with filter value
            const command = filterValue ? `scope "${filterValue}"` : 'scope';
            const result = await this.execute(command);
            return result;
        }
        throw new Error(`Unknown event type: ${eventType}`);
    }
}

module.exports = StoryMapView;


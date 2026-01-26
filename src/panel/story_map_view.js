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
                            data-explore-icon="${submitExploreIconPath}"
                            data-scenario-icon="${submitScenarioIconPath}"
                            data-test-icon="${submitTestIconPath}"
                            data-code-icon="${submitCodeIconPath}"
                            data-shape-tooltip="Submit shape instructions for epic"
                            data-explore-tooltip="Submit explore instructions for sub-epic"
                            data-scenario-tooltip="Submit scenario instructions for story"
                            data-test-tooltip="Submit test instructions for story"
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
    </div>`;
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


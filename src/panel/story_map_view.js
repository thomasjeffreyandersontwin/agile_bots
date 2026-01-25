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

class StoryMapView extends PanelView {
    /**
     * Story map view with filtering and editing.
     * 
     * @param {string|PanelView} botPathOrCli - Bot path or CLI instance
     * @param {Object} webview - VS Code webview instance (optional)
     * @param {Object} extensionUri - Extension URI (optional)
     */
    constructor(botPathOrCli, webview, extensionUri) {
        super(botPathOrCli);
        this.webview = webview || null;
        this.extensionUri = extensionUri || null;
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
        const botData = await this.execute('status');
        const scopeData = botData.scope || { type: 'all', filter: '', content: null, graphLinks: [] };
        const vscode = require('vscode');
        
        // Get the proper webview URIs for icons
        let magnifyingGlassIconPath = '';
        let clearIconPath = '';
        let showAllIconPath = '';
        let plusIconPath = '';
        let subtractIconPath = '';
        let gearIconPath = '';
        let epicIconPath = '';
        let pageIconPath = '';
        let testTubeIconPath = '';
        let documentIconPath = '';
        let addEpicIconPath = '';
        let addSubEpicIconPath = '';
        let addStoryIconPath = '';
        let addTestsIconPath = '';
        let addAcceptanceCriteriaIconPath = '';
        let deleteIconPath = '';
        let deleteChildrenIconPath = '';
        let scopeToIconPath = '';
        let submitShapeIconPath = '';
        let submitExploreIconPath = '';
        let submitScenariosIconPath = '';
        let submitTestsIconPath = '';
        let submitCodeIconPath = '';
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
                
                const addAcceptanceCriteriaUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'clipboard.png');
                addAcceptanceCriteriaIconPath = this.webview.asWebviewUri(addAcceptanceCriteriaUri).toString();
                
                const deleteUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'delete.png');
                deleteIconPath = this.webview.asWebviewUri(deleteUri).toString();
                
                const deleteChildrenUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'delete_children.png');
                deleteChildrenIconPath = this.webview.asWebviewUri(deleteChildrenUri).toString();
                
                const scopeToUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'bullseye.png');
                scopeToIconPath = this.webview.asWebviewUri(scopeToUri).toString();
                
                // Submit button icons
                const submitShapeUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'submit_subepic.png');
                submitShapeIconPath = this.webview.asWebviewUri(submitShapeUri).toString();
                
                const submitExploreUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'submit_story.png');
                submitExploreIconPath = this.webview.asWebviewUri(submitExploreUri).toString();
                
                const submitScenariosUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'submit_ac.png');
                submitScenariosIconPath = this.webview.asWebviewUri(submitScenariosUri).toString();
                
                const submitTestsUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'submit_tests.png');
                submitTestsIconPath = this.webview.asWebviewUri(submitTestsUri).toString();
                
                const submitCodeUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'submit_code.png');
                submitCodeIconPath = this.webview.asWebviewUri(submitCodeUri).toString();
            } catch (err) {
                console.error('Failed to create icon URIs:', err);
            }
        } else {
            // Fallback for test environment (no webview)
            submitShapeIconPath = 'submit_subepic.png';
            submitExploreIconPath = 'submit_story.png';
            submitScenariosIconPath = 'submit_ac.png';
            submitTestsIconPath = 'submit_tests.png';
            submitCodeIconPath = 'submit_code.png';
        }
        
        // Determine submit button icon based on scope filter
        let submitIconPath = submitCodeIconPath;
        try {
            const submitIconInfo = this.getSubmitIconForScope(scopeData.filter);
            submitIconPath = this.getSubmitIconPath(submitIconInfo.behavior, {
                shape: submitShapeIconPath,
                explore: submitExploreIconPath,
                scenarios: submitScenariosIconPath,
                tests: submitTestsIconPath,
                code: submitCodeIconPath
            });
        } catch (err) {
            console.error('Failed to determine submit icon:', err);
        }
        
        // Create contextual action buttons toolbar
        const actionButtonsHtml = `
            <div id="contextual-actions" style="display: flex; align-items: center; margin-left: 12px; gap: 6px;">
                <!-- Create buttons with tight spacing -->
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
                </div>
                
                <!-- Delete button -->
                <div style="display: flex; align-items: center;">
                    <button id="btn-delete" onclick="event.stopPropagation(); handleDelete();" style="display: none; background: transparent; border: none; padding: 4px; cursor: pointer; transition: opacity 0.15s ease;" onmouseover="this.style.opacity='0.7'" onmouseout="this.style.opacity='1'" title="Delete (including children)">
                        <img src="${deleteIconPath}" style="width: 28px; height: 28px; object-fit: contain;" alt="Delete" />
                    </button>
                </div>
                
                <!-- Scope buttons group with space for additional scope buttons -->
                <div style="display: flex; align-items: center; gap: 2px; margin-left: 10px;">
                    <button id="btn-scope-to" onclick="event.stopPropagation(); handleScopeTo();" style="display: none; background: transparent; border: none; padding: 4px; cursor: pointer; transition: opacity 0.15s ease;" onmouseover="this.style.opacity='0.7'" onmouseout="this.style.opacity='1'" title="Scope to selected node">
                        <img src="${scopeToIconPath}" style="width: 28px; height: 28px; object-fit: contain;" alt="Scope To" />
                    </button>
                    <button id="btn-submit" onclick="event.stopPropagation(); handleSubmitScope();" style="display: none; background: transparent; border: none; padding: 4px; cursor: pointer; transition: opacity 0.15s ease;" onmouseover="this.style.opacity='0.7'" onmouseout="this.style.opacity='1'" title="Submit scope and start work">
                        <img src="${submitIconPath}" style="width: 28px; height: 28px; object-fit: contain;" alt="Submit" />
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
        
        let contentHtml = '';
        let contentSummary = '';
        if ((scopeData.type === 'story' || scopeData.type === 'showAll') && scopeData.content) {
            // content is an object with 'epics' property, not directly an array
            const epics = scopeData.content.epics || [];
            const rootNode = this.renderRootNode(actionButtonsHtml);
            const treeHtml = this.renderStoryTree(epics, gearIconPath, epicIconPath, pageIconPath, testTubeIconPath, documentIconPath, plusIconPath, subtractIconPath);
            contentHtml = rootNode + treeHtml;
            contentSummary = `${epics.length} epic${epics.length !== 1 ? 's' : ''}`;
        } else if (scopeData.type === 'files' && scopeData.content) {
            contentHtml = this.renderFileList(scopeData.content);
            contentSummary = `${scopeData.content.length} file${scopeData.content.length !== 1 ? 's' : ''}`;
        } else {
            contentHtml = '<div class="empty-state">All files in workspace</div>';
            contentSummary = 'all files';
        }
        
        const filterValue = this.escapeHtml(scopeData.filter || '');
        const hasFilter = filterValue.length > 0;
        
        return `
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
    renderStoryTree(epics, gearIconPath, epicIconPath, pageIconPath, testTubeIconPath, documentIconPath, plusIconPath, subtractIconPath) {
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
            const epicNameHtml = epicDocLink
                ? `<span class="story-node" draggable="true" data-node-type="epic" data-node-name="${this.escapeHtml(epic.name)}" data-has-children="${epicHasChildren}" data-position="${epicIndex}" data-path="${epicPath}" data-file-link="${this.escapeHtml(epicDocLink.url)}" style="text-decoration: underline; cursor: pointer;">${this.escapeHtml(epic.name)}</span>`
                : `<span class="story-node" draggable="true" data-node-type="epic" data-node-name="${this.escapeHtml(epic.name)}" data-has-children="${epicHasChildren}" data-position="${epicIndex}" data-path="${epicPath}" style="cursor: pointer;">${this.escapeHtml(epic.name)}</span>`;
            
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
                const subEpicNameHtml = subEpicDocLink
                    ? `<span class="story-node" draggable="true" data-node-type="sub-epic" data-node-name="${this.escapeHtml(subEpic.name)}" data-has-children="${subEpicHasChildren}" data-has-stories="${hasStories}" data-has-nested-sub-epics="${hasNestedSubEpics}" data-position="${subEpicIndex}" data-path="${subEpicPath}" data-file-link="${this.escapeHtml(subEpicDocLink.url)}" style="text-decoration: underline; cursor: pointer;">${this.escapeHtml(subEpic.name)}</span>`
                    : `<span class="story-node" draggable="true" data-node-type="sub-epic" data-node-name="${this.escapeHtml(subEpic.name)}" data-has-children="${subEpicHasChildren}" data-has-stories="${hasStories}" data-has-nested-sub-epics="${hasNestedSubEpics}" data-position="${subEpicIndex}" data-path="${subEpicPath}" style="cursor: pointer;">${this.escapeHtml(subEpic.name)}</span>`;
                
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
                                }
                                
                                // Find story doc link (if exists)
                                const storyDocLink = story.links && story.links.find(l => l.text === 'story');
                                
                                // Story name with double-click to edit, clickable to select
                                if (storyDocLink) {
                                    html += `<span class="story-node" draggable="true" data-node-type="story" data-node-name="${this.escapeHtml(story.name)}" data-has-children="${hasScenarios}" data-position="${storyIndex}" data-path="${storyPath}" data-file-link="${this.escapeHtml(storyDocLink.url)}" style="text-decoration: underline; cursor: pointer;">${storyIcon}${this.escapeHtml(story.name)}</span>`;
                                } else {
                                    html += `<span class="story-node" draggable="true" data-node-type="story" data-node-name="${this.escapeHtml(story.name)}" data-has-children="${hasScenarios}" data-position="${storyIndex}" data-path="${storyPath}" style="cursor: pointer;">${storyIcon}${this.escapeHtml(story.name)}</span>`;
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
                                        
                                        // Create scenario anchor ID from scenario name (matches synchronizer format)
                                        const scenarioAnchor = this.createScenarioAnchor(scenario.name);
                                        // CRITICAL: Escape the ENTIRE path including quotes - HTML parser stops at unescaped quotes
                                        const scenarioPath = this.escapeHtml(`${baseStoryGraphPath}."${subEpic.name}"."${story.name}"."${scenario.name}"`);
                                        
                                        // Link scenario name to story file with scenario anchor
                                        // Make scenarios draggable and renameable like other nodes
                                        if (storyDocLink) {
                                            const scenarioLink = `${storyDocLink.url}#${scenarioAnchor}`;
                                            html += `<span class="story-node" draggable="true" data-node-type="scenario" data-node-name="${this.escapeHtml(scenario.name)}" data-has-children="false" data-position="${scenarioIndex}" data-path="${scenarioPath}" data-file-link="${this.escapeHtml(scenarioLink)}" style="text-decoration: underline; cursor: pointer;">${this.escapeHtml(scenario.name)}</span>`;
                                        } else {
                                            // No story doc link - just display scenario name with drag/rename support
                                            html += `<span class="story-node" draggable="true" data-node-type="scenario" data-node-name="${this.escapeHtml(scenario.name)}" data-has-children="false" data-position="${scenarioIndex}" data-path="${scenarioPath}" style="cursor: pointer;">${this.escapeHtml(scenario.name)}</span>`;
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
     * Determine submit icon and behavior for the current scope filter.
     * 
     * @param {string} scopeFilter - Current scope filter (node name)
     * @returns {Object} Object with behavior and description
     */
    getSubmitIconForScope(scopeFilter) {
        if (!scopeFilter) {
            return { behavior: 'shape', description: 'No scope selected' };
        }
        
        // This is a simplified version - in production, would query bot to analyze node
        // For now, return default behavior based on naming patterns
        const filterLower = scopeFilter.toLowerCase();
        
        if (filterLower.includes('product') || filterLower.includes('management')) {
            return { behavior: 'shape', description: 'Empty epic needs structure' };
        }
        
        if (filterLower.includes('reporting')) {
            return { behavior: 'explore', description: 'Story needs exploration' };
        }
        
        if (filterLower.includes('authentication')) {
            return { behavior: 'scenarios', description: 'Story needs scenarios' };
        }
        
        if (filterLower.includes('export')) {
            return { behavior: 'tests', description: 'Story needs tests' };
        }
        
        if (filterLower.includes('upload') || filterLower.includes('search')) {
            return { behavior: 'code', description: 'Story needs code' };
        }
        
        return { behavior: 'code', description: 'Default: code' };
    }
    
    /**
     * Get submit icon path for a specific behavior.
     * 
     * @param {string} behavior - Behavior name (shape, explore, scenarios, tests, code)
     * @param {Object} iconPaths - Object with icon paths for each behavior
     * @returns {string} Icon path for the behavior
     */
    getSubmitIconPath(behavior, iconPaths) {
        const iconMap = {
            'shape': iconPaths.shape,
            'explore': iconPaths.explore,
            'scenarios': iconPaths.scenarios,
            'tests': iconPaths.tests,
            'code': iconPaths.code
        };
        
        return iconMap[behavior] || iconPaths.code;
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


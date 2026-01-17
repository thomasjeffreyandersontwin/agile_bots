/**
 * ScopeSection - Renders scope section with filter and story tree or file list.
 * 
 * Epic: Invoke Bot Through Panel
 * Sub-Epic: Manage Scope Through Panel
 * Story: Display Story Scope Hierarchy, Filter Story Scope
 */

const PanelView = require('./panel_view');

class ScopeSection extends PanelView {
    /**
     * Scope section view.
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
            } catch (err) {
                console.error('Failed to create icon URIs:', err);
            }
        }
        
        const linksHtml = scopeData.graphLinks && scopeData.graphLinks.length > 0
            ? scopeData.graphLinks.map(link =>
                `<span onclick="openFile('${this.escapeForJs(link.url)}')" style="color: var(--vscode-foreground); text-decoration: underline; margin-left: 6px; font-size: 12px; cursor: pointer;">${this.escapeHtml(link.text).toLowerCase()}</span>`
            ).join('')
            : '';
        
        // Always show story-graph.json and story-map.md links
        const workspaceDir = botData.workspace_directory || '';
        const storyGraphPath = workspaceDir ? `${workspaceDir}/agile_bot/docs/stories/story-graph.json` : '';
        const storyMapPath = workspaceDir ? `${workspaceDir}/agile_bot/docs/stories/story-map/story-map.md` : '';
        
        const permanentLinksHtml = `
            <span onclick="openFile('${this.escapeForJs(storyGraphPath)}')" style="color: var(--vscode-foreground); text-decoration: underline; margin-left: 12px; font-size: 12px; cursor: pointer;" title="Open story-graph.json">story graph</span>
            <span onclick="openFile('${this.escapeForJs(storyMapPath)}')" style="color: var(--vscode-foreground); text-decoration: underline; margin-left: 6px; font-size: 12px; cursor: pointer;" title="Open story-map.md">story map</span>
        `;
        
        let contentHtml = '';
        let contentSummary = '';
        if ((scopeData.type === 'story' || scopeData.type === 'showAll') && scopeData.content) {
            // content is an object with 'epics' property, not directly an array
            const epics = scopeData.content.epics || [];
            contentHtml = this.renderStoryTree(epics, gearIconPath, epicIconPath, pageIconPath, testTubeIconPath, documentIconPath, plusIconPath, subtractIconPath);
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
                <div style="display: flex; align-items: center;">
                    <span class="expand-icon" style="margin-right: 8px; font-size: 28px; transition: transform 0.15s;">▸</span>
                    ${magnifyingGlassIconPath ? `<img src="${magnifyingGlassIconPath}" style="margin-right: 8px; width: 28px; height: 28px; object-fit: contain;" alt="Scope Icon" />` : ''}
                    <span style="font-weight: 600; font-size: 20px;">Scope</span>
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
            
            // Make epic name a hyperlink if document exists
            const epicNameHtml = epicDocLink
                ? `<span onclick="openFile('${this.escapeForJs(epicDocLink.url)}')" style="text-decoration: underline; cursor: pointer;">${this.escapeHtml(epic.name)}</span>`
                : this.escapeHtml(epic.name);
            
            // Render test tube icon for epic test link
            const epicTestIcon = (epicTestLink && testTubeIconPath)
                ? ` <span onclick="openFile('${this.escapeForJs(epicTestLink.url)}')" style="cursor: pointer;"><img src="${testTubeIconPath}" style="width: 20px; height: 20px; vertical-align: middle;" alt="Test" /></span>`
                : '';
            
            let html = `<div style="margin-top: 8px; font-size: 12px;">
        <span class="collapsible-header" onclick="toggleCollapse('${epicId}')" style="cursor: pointer; user-select: none;">
          <span id="${epicId}-icon" style="display: inline-block; min-width: 9px;" data-plus="${plusIconPath}" data-subtract="${subtractIconPath}"><img class="collapse-icon" src="${plusIconPath}" data-state="collapsed" style="width: 9px; height: 9px; vertical-align: middle;" alt="Expand" /></span> ${epicIcon}${epicNameHtml}${epicTestIcon}
        </span>
      </div>`;
            
            html += `<div id="${epicId}" class="collapsible-content" style="display: none;">`;
            // Helper function to recursively render a sub-epic (can be nested any number of levels)
            const renderSubEpic = (subEpic, subEpicIndex, parentPath, depth = 0) => {
                const subEpicId = `${parentPath}-${subEpicIndex}`;
                const subEpicIcon = gearIconPath ? `<img src="${gearIconPath}" style="width: 14px; height: 14px; vertical-align: middle; margin-right: 4px;" alt="Sub-Epic" />` : '';
                
                // Find document and test links
                const subEpicDocLink = subEpic.links && subEpic.links.find(l => l.icon === 'document');
                const subEpicTestLink = subEpic.links && subEpic.links.find(l => l.icon === 'test_tube');
                
                // Make sub-epic name a hyperlink if document exists
                const subEpicNameHtml = subEpicDocLink
                    ? `<span onclick="openFile('${this.escapeForJs(subEpicDocLink.url)}')" style="text-decoration: underline; cursor: pointer;">${this.escapeHtml(subEpic.name)}</span>`
                    : this.escapeHtml(subEpic.name);
                
                // Only render test tube icon for test links
                const subEpicTestIcon = (subEpicTestLink && testTubeIconPath)
                    ? ` <span onclick="openFile('${this.escapeForJs(subEpicTestLink.url)}')" style="cursor: pointer;"><img src="${testTubeIconPath}" style="width: 20px; height: 20px; vertical-align: middle;" alt="Test" /></span>`
                    : '';
                
                const marginLeft = 7 + (depth * 7); // Increase margin for nested sub-epics
                
                html += `<div style="margin-left: ${marginLeft}px; margin-top: 4px; font-size: 12px;"><span class="collapsible-header" onclick="toggleCollapse('${subEpicId}')" style="cursor: pointer; user-select: none;"><span id="${subEpicId}-icon" style="display: inline-block; min-width: 9px;" data-plus="${plusIconPath}" data-subtract="${subtractIconPath}"><img class="collapse-icon" src="${plusIconPath}" data-state="collapsed" style="width: 9px; height: 9px; vertical-align: middle;" alt="Expand" /></span> ${subEpicIcon}${subEpicNameHtml}${subEpicTestIcon}</span></div>`;
                
                html += `<div id="${subEpicId}" class="collapsible-content" style="display: none;">`;
                
                // Render nested sub_epics if they exist (recursive)
                const nestedSubEpics = subEpic.sub_epics || [];
                if (nestedSubEpics.length > 0) {
                    nestedSubEpics.forEach((nested, nestedIndex) => {
                        renderSubEpic(nested, nestedIndex, subEpicId, depth + 1);
                    });
                }
                
                // Render story_groups with stories if they exist
                if (subEpic.story_groups && subEpic.story_groups.length > 0) {
                    subEpic.story_groups.forEach(storyGroup => {
                        if (storyGroup.stories && storyGroup.stories.length > 0) {
                            storyGroup.stories.forEach((story, storyIndex) => {
                                const storyId = `${subEpicId}-story-${storyIndex}`;
                                const storyIcon = pageIconPath ? `<img src="${pageIconPath}" style="width: 14px; height: 14px; vertical-align: middle; margin-right: 4px;" alt="Story" />` : '';
                                
                                // Check if story has scenarios - if so, make it collapsible
                                const hasScenarios = story.scenarios && story.scenarios.length > 0;
                                
                                html += `<div style="margin-left: ${marginLeft + 7}px; margin-top: 2px; font-size: 12px;">`;
                                
                                if (hasScenarios) {
                                    // Collapsible story with scenarios
                                    html += `<span class="collapsible-header" onclick="toggleCollapse('${storyId}')" style="cursor: pointer; user-select: none;">`;
                                    html += `<span id="${storyId}-icon" style="display: inline-block; min-width: 9px;" data-plus="${plusIconPath}" data-subtract="${subtractIconPath}"><img class="collapse-icon" src="${plusIconPath}" data-state="collapsed" style="width: 9px; height: 9px; vertical-align: middle;" alt="Expand" /></span> `;
                                }
                                
                                // Find story doc link (if exists)
                                const storyDocLink = story.links && story.links.find(l => l.text === 'story');
                                
                                if (storyDocLink) {
                                    html += `<span onclick="openFile('${this.escapeForJs(storyDocLink.url)}')" style="text-decoration: underline; cursor: pointer;">${storyIcon}${this.escapeHtml(story.name)}</span>`;
                                } else {
                                    html += `${storyIcon}${this.escapeHtml(story.name)}`;
                                }
                                
                                // Render test tube icon for test link
                                if (story.links && story.links.length > 0) {
                                    const testLink = story.links.find(l => l.icon === 'test_tube');
                                    if (testLink && testTubeIconPath) {
                                        html += ` <span onclick="openFile('${this.escapeForJs(testLink.url)}')" style="cursor: pointer;"><img src="${testTubeIconPath}" style="width: 20px; height: 20px; vertical-align: middle;" alt="Test" /></span>`;
                                    }
                                }
                                
                                if (hasScenarios) {
                                    html += `</span>`; // Close collapsible-header span
                                }
                                
                                html += '</div>';
                                
                                // Render scenarios if they exist
                                if (hasScenarios) {
                                    html += `<div id="${storyId}" class="collapsible-content" style="display: none;">`;
                                    story.scenarios.forEach((scenario, scenarioIndex) => {
                                        html += `<div style="margin-left: ${marginLeft + 21}px; margin-top: 2px; font-size: 12px;">`;
                                        
                                        // Create scenario anchor ID from scenario name (matches synchronizer format)
                                        const scenarioAnchor = this.createScenarioAnchor(scenario.name);
                                        
                                        // Link scenario name to story file with scenario anchor
                                        if (storyDocLink) {
                                            const scenarioLink = `${storyDocLink.url}#${scenarioAnchor}`;
                                            html += `<span onclick="openFile('${this.escapeForJs(scenarioLink)}')" style="text-decoration: underline; cursor: pointer;">${this.escapeHtml(scenario.name)}</span>`;
                                        } else {
                                            // No story doc link - just display scenario name
                                            html += `${this.escapeHtml(scenario.name)}`;
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
                
                // LEGACY: Also check for direct stories array (old format)
                if (subEpic.stories && subEpic.stories.length > 0) {
                    subEpic.stories.forEach((story, storyIndex) => {
                        const storyId = `${subEpicId}-story-${storyIndex}`;
                        const storyIcon = pageIconPath ? `<img src="${pageIconPath}" style="width: 14px; height: 14px; vertical-align: middle; margin-right: 4px;" alt="Story" />` : '';
                        
                        // Check if story has scenarios - if so, make it collapsible
                        const hasScenarios = story.scenarios && story.scenarios.length > 0;
                        
                        html += `<div style="margin-left: ${marginLeft + 7}px; margin-top: 2px; font-size: 12px;">`;
                        
                        if (hasScenarios) {
                            // Collapsible story with scenarios
                            html += `<span class="collapsible-header" onclick="toggleCollapse('${storyId}')" style="cursor: pointer; user-select: none;">`;
                            html += `<span id="${storyId}-icon" style="display: inline-block; min-width: 9px;" data-plus="${plusIconPath}" data-subtract="${subtractIconPath}"><img class="collapse-icon" src="${plusIconPath}" data-state="collapsed" style="width: 9px; height: 9px; vertical-align: middle;" alt="Expand" /></span> `;
                        }
                        
                        // Find story doc link (if exists)
                        const storyDocLink = story.links && story.links.find(l => l.text === 'story');
                        
                        if (storyDocLink) {
                            html += `<span onclick="openFile('${this.escapeForJs(storyDocLink.url)}')" style="text-decoration: underline; cursor: pointer;">${storyIcon}${this.escapeHtml(story.name)}</span>`;
                        } else {
                            html += `${storyIcon}${this.escapeHtml(story.name)}`;
                        }
                        
                        // Render test tube icon for test link
                        if (story.links && story.links.length > 0) {
                            const testLink = story.links.find(l => l.icon === 'test_tube');
                            if (testLink && testTubeIconPath) {
                                html += ` <span onclick="openFile('${this.escapeForJs(testLink.url)}')" style="cursor: pointer;"><img src="${testTubeIconPath}" style="width: 20px; height: 20px; vertical-align: middle;" alt="Test" /></span>`;
                            }
                        }
                        
                        if (hasScenarios) {
                            html += `</span>`; // Close collapsible-header span
                        }
                        
                        html += '</div>';
                        
                        // Render scenarios if they exist
                        if (hasScenarios) {
                            html += `<div id="${storyId}" class="collapsible-content" style="display: none;">`;
                            story.scenarios.forEach((scenario, scenarioIndex) => {
                                html += `<div style="margin-left: ${marginLeft + 21}px; margin-top: 2px; font-size: 12px;">`;
                                
                                // Create scenario anchor ID from scenario name (matches synchronizer format)
                                const scenarioAnchor = this.createScenarioAnchor(scenario.name);
                                
                                // Link scenario name to story file with scenario anchor
                                if (storyDocLink) {
                                    const scenarioLink = `${storyDocLink.url}#${scenarioAnchor}`;
                                    html += `<span onclick="openFile('${this.escapeForJs(scenarioLink)}')" style="text-decoration: underline; cursor: pointer;">${this.escapeHtml(scenario.name)}</span>`;
                                } else {
                                    // No story doc link - just display scenario name
                                    html += `${this.escapeHtml(scenario.name)}`;
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

module.exports = ScopeSection;


/**
 * BotHeaderView - Renders bot header section with bot name, version, refresh button, and bot selector.
 * 
 * Epic: Invoke Bot Through Panel
 * Sub-Epic: Manage Panel Session
 * Story: Open Panel, Display Session Status, Switch Bot
 */

const PanelView = require('./panel_view');

class BotHeaderView extends PanelView {
    /**
     * Bot header view.
     * 
     * @param {string|PanelView} botPathOrCli - Bot path or CLI instance
     * @param {string} panelVersion - Panel extension version (optional)
     * @param {Object} webview - VS Code webview instance (optional)
     * @param {Object} extensionUri - Extension URI (optional)
     * @param {Object} parentView - Parent BotView (optional, for accessing cached botData)
     */
    constructor(botPathOrCli, panelVersion, webview, extensionUri, parentView = null) {
        super(botPathOrCli);
        this.panelVersion = panelVersion || null;
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
     * Get bot icon based on bot name.
     * 
     * @param {string} botName - Bot name
     * @returns {string} Icon emoji or empty string
     */
    getBotIcon(botName) {
        // No emoji fallbacks - use images only
        return '';
    }
    
    /**
     * Truncate path with ellipsis if too long
     */
    truncatePath(path, maxLength) {
        if (!path || path.length <= maxLength) return path;
        const ellipsis = '...';
        const prefixLength = Math.floor((maxLength - ellipsis.length) / 2);
        const suffixLength = maxLength - ellipsis.length - prefixLength;
        return path.substring(0, prefixLength) + ellipsis + path.substring(path.length - suffixLength);
    }
    
    /**
     * Render bot header HTML.
     * 
     * @returns {string} HTML string
     */
    async render() {
        console.log('[BotHeaderView] Starting render');
        console.log('[BotHeaderView] Panel version:', this.panelVersion);
        console.log('[BotHeaderView] Has webview:', !!this.webview);
        console.log('[BotHeaderView] Has extensionUri:', !!this.extensionUri);
        
        // Use cached botData from parent if available, otherwise fetch it
        const botData = this.parentView?.botData || await this.execute('status');
        console.log('[BotHeaderView] Bot data source:', this.parentView?.botData ? 'cached' : 'fetched');
        console.log('[BotHeaderView] Status response:', JSON.stringify(botData).substring(0, 300));
        
        const vscode = require('vscode');
        const maxPathLength = 80;
        
        // NO FALLBACKS - let it fail if data is missing
        if (!botData) throw new Error('[BotHeaderView] botData is null/undefined');
        if (!botData.name && !botData.bot_name) throw new Error('[BotHeaderView] No bot name in response');
        if (!botData.bot_directory) throw new Error('[BotHeaderView] No bot_directory in response');
        if (!botData.workspace_directory) throw new Error('[BotHeaderView] No workspace_directory in response');
        
        const currentBot = botData.name || botData.bot_name;
        const availableBots = botData.available_bots || [];
        const safeBotName = this.escapeHtml(currentBot);
        const safeBotDir = this.escapeHtml(botData.bot_directory);
        const safeWorkspaceDir = this.escapeHtml(botData.workspace_directory);
        
        // AC: Truncate very long directory paths
        const displayBotDir = this.truncatePath(safeBotDir, maxPathLength);
        const displayWorkspaceDir = this.truncatePath(safeWorkspaceDir, maxPathLength);
        
        // Build bot selector links
        let botLinksHtml = '';
        if (availableBots && availableBots.length > 0) {
            botLinksHtml = availableBots.map(botName => {
                const isActive = botName === currentBot;
                const activeClass = isActive ? ' active' : '';
                return `<a href="javascript:void(0)" class="bot-link${activeClass}" onclick="switchBot('${this.escapeHtml(botName)}')">${this.escapeHtml(botName)}</a>`;
            }).join('\n                ');
        }
        
        // Get the proper webview URIs for images (bundled in extension)
        let imagePath = '';
        let refreshIconPath = '';
        let storyIconPath = '';
        let crcIconPath = '';
        if (this.webview && this.extensionUri) {
            try {
                const iconUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'company_icon.png');
                imagePath = this.webview.asWebviewUri(iconUri).toString();
                console.log('[BotHeaderView] Company icon URI:', imagePath);
                
                const refreshUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'refresh.png');
                refreshIconPath = this.webview.asWebviewUri(refreshUri).toString();
                console.log('[BotHeaderView] Refresh icon URI:', refreshIconPath);
                
                const storyUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'story.png');
                storyIconPath = this.webview.asWebviewUri(storyUri).toString();
                console.log('[BotHeaderView] Story icon URI:', storyIconPath);
                
                const crcUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'crc.png');
                crcIconPath = this.webview.asWebviewUri(crcUri).toString();
                console.log('[BotHeaderView] CRC icon URI:', crcIconPath);
            } catch (err) {
                console.error('[BotHeaderView] Failed to create icon URI:', err);
                console.error('[BotHeaderView] webview:', !!this.webview, 'extensionUri:', !!this.extensionUri, 'extensionUri value:', this.extensionUri?.toString());
            }
        } else {
            console.warn('[BotHeaderView] Missing webview or extensionUri:', { hasWebview: !!this.webview, hasExtensionUri: !!this.extensionUri });
        }
        
        const versionHtml = this.panelVersion 
            ? `<span style="font-size: 14px; opacity: 0.7; margin-left: 6px;">v${this.escapeHtml(this.panelVersion)}</span>`
            : '';
        
        return `
    <div class="section card-primary" style="border-top: none; padding-top: 0;">
        <div class="main-header">
            ${imagePath ? `<img src="${imagePath}" class="main-header-icon" alt="Company Icon" onerror="console.error('Failed to load icon:', this.src); this.style.border='1px solid red';" />` : ''}
            <span class="main-header-title">Agile Bots ${versionHtml}</span>
            <button class="main-header-refresh" onclick="refreshStatus()" title="Refresh">
                ${refreshIconPath ? `<img src="${refreshIconPath}" style="width: 36px; height: 36px; object-fit: contain; filter: saturate(1.3) brightness(0.95) hue-rotate(-5deg);" alt="Refresh" />` : ''}
            </button>
        </div>
        <div class="collapsible-section expanded">
            <div class="collapsible-header" onclick="toggleSection('header-content')" style="
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
                    ${this.currentBot === 'story_bot' && storyIconPath
                        ? `<img src="${storyIconPath}" style="margin-right: 8px; width: 36px; height: 36px; object-fit: contain;" alt="Story Bot Icon" />`
                        : this.currentBot === 'crc_bot' && crcIconPath
                        ? `<img src="${crcIconPath}" style="margin-right: 8px; width: 36px; height: 36px; object-fit: contain;" alt="CRC Bot Icon" />`
                        : ''}
                    <span style="font-weight: 600; font-size: 20px;">${safeBotName}</span>
                </div>
                <div class="bot-links" onclick="event.stopPropagation();" style="gap: 6px;">
                    ${botLinksHtml}
                </div>
            </div>
            <div id="header-content" class="collapsible-content" style="max-height: 2000px; overflow: hidden; transition: max-height 0.3s ease;">
                <div class="card-secondary" style="padding: 1px 5px 2px 5px;">
                    <div class="input-container" style="margin-top: 0;">
                        <div class="input-header">Workspace</div>
                        <input type="text" id="workspacePathInput" 
                               value="${safeWorkspaceDir}" 
                               placeholder="Path to workspace"
                               onchange="updateWorkspace(this.value)"
                               onkeydown="if(event.key === 'Enter') { event.preventDefault(); updateWorkspace(this.value); }"
                               title="${safeWorkspaceDir}" />
                    </div>
                    <div class="info-display" style="margin-top: 4px;" title="${safeBotDir}">
                        <span class="label">Bot Path:</span>
                        <span class="value">${displayBotDir}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>`;
    }
    
    /**
     * Handle events.
     * 
     * @param {string} eventType - Event type
     * @param {Object} eventData - Event data
     * @returns {Promise<Object>} Result
     */
    async handleEvent(eventType, eventData) {
        if (eventType === 'switchBot') {
            // Execute CLI command to switch bot
            const botName = eventData.botName;
            PanelView._log(`[BotHeaderView] Switching bot to: ${botName}`);
            
            try {
                const result = await this.execute(`bot ${botName}`);
                PanelView._log(`[BotHeaderView] Bot switch result: ${JSON.stringify(result)}`);
                return result;
            } catch (error) {
                PanelView._log(`[BotHeaderView] ERROR switching bot: ${error.message}`);
                throw error;
            }
        }
        if (eventType === 'updateWorkspace') {
            // Execute CLI command to change workspace
            const workspacePath = eventData.workspacePath;
            PanelView._log(`[BotHeaderView] Executing workspace command: workspace ${workspacePath}`);
            
            try {
                const result = await this.execute(`workspace ${workspacePath}`);
                PanelView._log(`[BotHeaderView] Workspace command result: ${JSON.stringify(result)}`);
                return result;
            } catch (error) {
                PanelView._log(`[BotHeaderView] ERROR executing workspace command: ${error.message}`);
                throw error;
            }
        }
        throw new Error(`Unknown event type: ${eventType}`);
    }
}

module.exports = BotHeaderView;

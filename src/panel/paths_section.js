/**
 * PathsSection - Renders workspace path and bot directory paths.
 * 
 * Epic: Invoke Bot Through Panel
 * Sub-Epic: Manage Panel Session
 * Story: Change Workspace Path
 */

const PanelView = require('./panel_view');

class PathsSection extends PanelView {
    /**
     * Paths section view.
     * 
     * @param {string|PanelView} botPathOrCli - Bot path or CLI instance
     */
    constructor(botPathOrCli) {
        super(botPathOrCli);
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
     * Truncate path with ellipsis if too long.
     * 
     * @param {string} path - Path to truncate
     * @param {number} maxLength - Maximum length
     * @returns {string} Truncated path
     */
    truncatePath(path, maxLength) {
        if (!path || path.length <= maxLength) {
            return path;
        }
        const ellipsis = '...';
        const prefixLength = Math.floor((maxLength - ellipsis.length) / 2);
        const suffixLength = maxLength - ellipsis.length - prefixLength;
        return path.substring(0, prefixLength) + ellipsis + path.substring(path.length - suffixLength);
    }
    
    /**
     * Render paths section HTML.
     * 
     * @returns {string} HTML string
     */
    async render() {
        console.log('[PathsSection] Starting render');
        console.log('[PathsSection] Executing status command...');
        const botData = await this.execute('status');
        console.log('[PathsSection] Status response:', JSON.stringify(botData).substring(0, 300));
        
        // NO FALLBACKS - let it fail if data is missing
        if (!botData) throw new Error('[PathsSection] botData is null/undefined');
        if (!botData.workspace_directory) throw new Error('[PathsSection] No workspace_directory in response');
        if (!botData.bot_directory) throw new Error('[PathsSection] No bot_directory in response');
        
        const maxPathLength = 80;
        const safeWorkspaceDir = this.escapeHtml(botData.workspace_directory);
        const safeBotDir = this.escapeHtml(botData.bot_directory);
        const displayWorkspaceDir = this.truncatePath(safeWorkspaceDir, maxPathLength);
        const displayBotDir = this.truncatePath(safeBotDir, maxPathLength);
        
        return `
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
        if (eventType === 'updateWorkspace') {
            // Update workspace logic would go here
            // For now, just return success
            return { success: true, workspace: eventData.workspacePath };
        }
        throw new Error(`Unknown event type: ${eventType}`);
    }
}

module.exports = PathsSection;

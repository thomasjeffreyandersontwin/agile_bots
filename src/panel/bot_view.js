/**
 * BotView - Main panel orchestrator that wraps bot JSON and displays all domain views.
 * 
 * Epic: Invoke Bot Through Panel
 * Sub-Epic: Manage Panel Session
 * Story: Open Panel, Display Session Status
 */

const PanelView = require('./panel_view');
const BotHeaderView = require('./bot_header_view');
const BehaviorsView = require('./behaviors_view');
const StoryMapView = require('./story_map_view');
const InstructionsSection = require('./instructions_view');

class BotView extends PanelView {
    /**
     * Main panel orchestrator.
     * 
     * @param {string|PanelView} botPathOrCli - Bot path or CLI instance
     * @param {string} panelVersion - Panel extension version (optional)
     * @param {Object} webview - VS Code webview instance (optional)
     * @param {Object} extensionUri - Extension URI (optional)
     */
    constructor(botPathOrCli, panelVersion, webview, extensionUri) {
        super(botPathOrCli);
        this.panelVersion = panelVersion || null;
        this.webview = webview || null;
        this.extensionUri = extensionUri || null;
        
        // Initialize domain views - pass CLI to all child views
        this.headerView = new BotHeaderView(botPathOrCli, this.panelVersion, webview, extensionUri);
        this.behaviorsView = new BehaviorsView(botPathOrCli, webview, extensionUri);
        this.storyMapView = new StoryMapView(botPathOrCli, webview, extensionUri);
        this.instructionsSection = new InstructionsSection(botPathOrCli, webview, extensionUri);
    }
    
    /**
     * Render complete bot view HTML.
     * 
     * @returns {Promise<string>} Complete HTML string
     */
    async render() {
        console.log('[BotView] Starting render');
        console.log('[BotView] Rendering header...');
        const header = await this.headerView.render();
        console.log('[BotView] Header rendered, length:', header.length);
        
        console.log('[BotView] Rendering behaviors...');
        const behaviors = await this.behaviorsView.render();
        console.log('[BotView] Behaviors rendered, length:', behaviors.length);
        
        console.log('[BotView] Rendering story map...');
        const storyMap = await this.storyMapView.render();
        console.log('[BotView] Story map rendered, length:', storyMap.length);
        
        console.log('[BotView] Rendering instructions...');
        const instructions = await this.instructionsSection.render();
        console.log('[BotView] Instructions rendered, length:', instructions.length);
        
        const finalHtml = `
            <div class="bot-view">
                ${header}
                ${behaviors}
                ${storyMap}
                ${instructions}
            </div>
        `;
        
        console.log('[BotView] Render complete, total HTML length:', finalHtml.length);
        return finalHtml;
    }
    
    /**
     * Execute command and return appropriate data.
     * Overrides PanelView.execute() to extract data from unified JSON response.
     * 
     * @param {string} command - Command to execute
     * @returns {Promise<Object>} Extracted data (bot JSON for status, unified response for actions)
     */
    async execute(command) {
        const response = await super.execute(command);
        
        // Check if response indicates an error from CLI
        if (response.status === 'error' && response.error) {
            const error = new Error(response.error);
            error.errorType = response.error_type;
            error.command = response.command;
            error.isCliError = true;
            throw error;
        }
        
        // In JSON mode, CLI returns unified structure: { execution?, instructions?, bot, scope? }
        // For "status" command, return bot data (response is already { bot: ... })
        if (command === 'status' && response.bot) {
            return response.bot;
        }
        
        // For "scope" command, return scope data with bot
        if (command === 'scope' && response.scope) {
            return response;
        }
        
        // For action commands, return unified response (contains execution, instructions, bot)
        return response;
    }
    
    /**
     * Refresh data from CLI.
     * 
     * @returns {Promise<Object>} Updated bot JSON
     */
    async refresh() {
        // "status" command returns the Bot object itself
        const botJSON = await this.execute('status');
        return botJSON;
    }
    
    /**
     * Handle user events.
     * 
     * @param {string} eventType - Type of event
     * @param {Object} eventData - Event data
     * @returns {Promise<Object>} Updated data or result
     */
    async handleEvent(eventType, eventData) {
        switch (eventType) {
            case 'refresh':
                return await this.refresh();
            case 'executeBehavior':
                return await this.behaviorsView.handleEvent('execute', eventData);
            case 'updateScope':
                return await this.scopeSection.handleEvent('updateFilter', eventData);
            case 'updateWorkspace':
                return await this.headerView.handleEvent('updateWorkspace', eventData);
            case 'switchBot':
                return await this.headerView.handleEvent('switchBot', eventData);
            default:
                throw new Error(`Unknown event type: ${eventType}`);
        }
    }
}

module.exports = BotView;

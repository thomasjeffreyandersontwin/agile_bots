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
        this.botData = null; // Cached bot data - populated during render
        
        // Initialize domain views - pass 'this' so they can access this.botData
        this.headerView = new BotHeaderView(botPathOrCli, this.panelVersion, webview, extensionUri, this);
        this.behaviorsView = new BehaviorsView(botPathOrCli, webview, extensionUri, this);
        this.storyMapView = new StoryMapView(botPathOrCli, webview, extensionUri, this);
        this.instructionsSection = new InstructionsSection(botPathOrCli, webview, extensionUri, this);
    }
    
    /**
     * Render complete bot view HTML.
     * 
     * @returns {Promise<string>} Complete HTML string
     */
    async render() {
        // ===== PERFORMANCE: BotView render =====
        const perfRenderStart = performance.now();
        log('[BotView] Starting render');
        
        // Fetch bot data ONCE and cache it for all child views
        const perfFetchStart = performance.now();
        this.botData = await this.execute('status');
        const perfFetchEnd = performance.now();
        log(`[BotView] [PERF] Fetch bot data (status): ${(perfFetchEnd - perfFetchStart).toFixed(2)}ms`);
        
        // Header
        const perfHeaderStart = performance.now();
        const header = await this.headerView.render();
        const perfHeaderEnd = performance.now();
        log(`[BotView] [PERF] Header render: ${(perfHeaderEnd - perfHeaderStart).toFixed(2)}ms`);
        
        // Behaviors
        const perfBehaviorsStart = performance.now();
        const behaviors = await this.behaviorsView.render();
        const perfBehaviorsEnd = performance.now();
        log(`[BotView] [PERF] Behaviors render: ${(perfBehaviorsEnd - perfBehaviorsStart).toFixed(2)}ms`);
        
        // Story map
        const perfStoryMapStart = performance.now();
        const storyMap = await this.storyMapView.render();
        const perfStoryMapEnd = performance.now();
        log(`[BotView] [PERF] Story map render: ${(perfStoryMapEnd - perfStoryMapStart).toFixed(2)}ms`);
        
        // Instructions
        const perfInstructionsStart = performance.now();
        const instructions = await this.instructionsSection.render();
        const perfInstructionsEnd = performance.now();
        log(`[BotView] [PERF] Instructions render: ${(perfInstructionsEnd - perfInstructionsStart).toFixed(2)}ms`);
        
        // Final assembly
        const perfAssemblyStart = performance.now();
        const finalHtml = `
            <div class="bot-view">
                ${header}
                ${behaviors}
                ${storyMap}
                ${instructions}
            </div>
        `;
        const perfAssemblyEnd = performance.now();
        log(`[BotView] [PERF] Final HTML assembly: ${(perfAssemblyEnd - perfAssemblyStart).toFixed(2)}ms`);
        
        const perfRenderEnd = performance.now();
        const totalRenderTime = (perfRenderEnd - perfRenderStart).toFixed(2);
        log(`[BotView] [PERF] TOTAL render() duration: ${totalRenderTime}ms`);
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
        // ===== PERFORMANCE: BotView refresh =====
        const perfRefreshStart = performance.now();
        
        // "status" command returns the Bot object itself
        const botJSON = await this.execute('status');
        
        const perfRefreshEnd = performance.now();
        const refreshDuration = (perfRefreshEnd - perfRefreshStart).toFixed(2);
        log(`[BotView] [PERF] refresh() (execute status) duration: ${refreshDuration}ms`);
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

/**
 * PanelView Test Helper
 * Provides factory methods for testing PanelView
 * This helper is ALLOWED to import production code (it wraps it)
 * Follows rule: object_oriented_test_helpers
 */

const path = require('path');

class PanelViewTestHelper {
    constructor(workspaceDir, botName = 'story_bot') {
        this.workspaceDir = workspaceDir;
        this.botName = botName;
        this.botPath = path.join(workspaceDir, 'bots', botName);
        
        // This helper is ALLOWED to import production code - it wraps it for tests
        const PanelView = require('../../src/panel/panel_view');
        this._cli = new PanelView(this.botPath);
    }
    
    /**
     * Cleanup CLI process - call in after() hook
     */
    cleanup() {
        if (this._cli) {
            this._cli.cleanup();
            this._cli = null;
        }
    }
    
    /**
     * Get the CLI instance for executing commands
     * @returns {PanelView} - The PanelView instance
     */
    getCLI() {
        return this._cli;
    }
    
    /**
     * Create a new PanelView instance
     * @param {string} [botPath] - Optional bot path, defaults to helper's botPath
     * @returns {PanelView} - New PanelView instance
     */
    createPanelView(botPath = null) {
        const PanelView = require('../../src/panel/panel_view');
        return new PanelView(botPath || this.botPath);
    }
    
    /**
     * Execute a command on the CLI
     * @param {string} command - Command to execute
     * @returns {Promise<*>} - Command result
     */
    async execute(command) {
        return await this._cli.execute(command);
    }
}

module.exports = PanelViewTestHelper;

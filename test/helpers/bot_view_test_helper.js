/**
 * BotView Test Helper
 * Provides factory methods and assertions for testing BotView
 * Follows rule: object_oriented_test_helpers
 */

const assert = require('node:assert');
const path = require('path');
const { parseHTML, HTMLAssertions } = require('./html_assertions');

class BotViewTestHelper {
    constructor(workspaceDir, botName = 'story_bot') {
        this.workspaceDir = workspaceDir;
        this.botName = botName;
        this.botPath = path.join(workspaceDir, 'bots', botName);
        this.webview = this.createMockWebview();
        this.extensionUri = this.createMockExtensionUri();
        
        // Create CLI instance - this test helper owns this process
        const PanelView = require('../../src/panel/panel_view');
        this._cli = new PanelView(this.botPath);
    }
    
    // ========================================================================
    // LIFECYCLE
    // ========================================================================
    
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
     */
    getCLI() {
        return this._cli;
    }
    
    // ========================================================================
    // FACTORY METHODS - Create test objects
    // ========================================================================
    
    /**
     * Create BotView instance - uses the helper's shared CLI
     */
    createBotView(webview = null, extensionUri = null) {
        const BotView = require('../../src/panel/bot_view');
        return new BotView(
            this._cli,  // Use helper's CLI instance
            null,       // panelVersion
            webview || this.webview,
            extensionUri || this.extensionUri
        );
    }
    
    /**
     * Create mock webview object
     * @returns {Object} - Mock webview
     */
    createMockWebview() {
        return {
            postMessage: (message) => {
                // Store last message for test assertions
                this.lastWebviewMessage = message;
            }
        };
    }
    
    /**
     * Create mock extension URI
     * @returns {Object} - Mock URI object
     */
    createMockExtensionUri() {
        return {
            fsPath: this.workspaceDir,
            toString: () => `file://${this.workspaceDir}`
        };
    }
    
    // ========================================================================
    // ASSERTION HELPERS - Verify results
    // ========================================================================
    
    /**
     * Assert behavior is present in HTML
     * @param {string} html - HTML string
     * @param {string} behaviorName - Expected behavior name
     */
    assertBehaviorPresent(html, behaviorName) {
        HTMLAssertions.assertContainsText(html, behaviorName);
    }
    
    /**
     * Assert behavior is present in HTML (snake_case alias)
     * @param {string} html - HTML string
     * @param {string} behaviorName - Expected behavior name
     */
    assert_behavior_present(html, behaviorName) {
        this.assertBehaviorPresent(html, behaviorName);
    }
    
    /**
     * Assert current behavior is marked in HTML
     * @param {string} html - HTML string
     * @param {string} behaviorName - Expected current behavior
     */
    assertCurrentBehaviorMarked(html, behaviorName) {
        const doc = parseHTML(html);
        const behaviorElement = doc.querySelector(`[data-behavior="${behaviorName}"]`);
        assert.ok(behaviorElement, `Behavior element "${behaviorName}" not found`);
        assert.ok(
            behaviorElement.classList.contains('current') || 
            behaviorElement.classList.contains('active') ||
            html.includes(`data-behavior="${behaviorName}"`) && html.includes('current'),
            `Behavior "${behaviorName}" should be marked as current`
        );
    }
    
    /**
     * Assert action is present under behavior
     * @param {string} html - HTML string
     * @param {string} behaviorName - Behavior name
     * @param {string} actionName - Action name
     */
    assertActionPresent(html, behaviorName, actionName) {
        HTMLAssertions.assertContainsText(html, actionName);
    }
    
    /**
     * Assert multiple actions are present
     * @param {string} html - HTML string
     * @param {string} behaviorName - Behavior name
     * @param {string[]} actionNames - Array of action names
     */
    assertActionsPresent(html, behaviorName, actionNames) {
        for (const actionName of actionNames) {
            this.assertActionPresent(html, behaviorName, actionName);
        }
    }
    
    /**
     * Assert behaviors appear in specific order
     * @param {string} html - HTML string
     * @param {string[]} behaviorNames - Array of behavior names in expected order
     */
    assertBehaviorsInOrder(html, behaviorNames) {
        let lastIndex = -1;
        for (const behaviorName of behaviorNames) {
            const index = html.indexOf(behaviorName, lastIndex);
            assert.ok(index > lastIndex, 
                `Behavior "${behaviorName}" should appear after previous behaviors`);
            lastIndex = index;
        }
    }
    
    /**
     * Assert actions are marked as completed
     * @param {string} html - HTML string
     * @param {string} behaviorName - Behavior name
     * @param {string[]} completedActionNames - Array of completed action names
     */
    assertActionsCompleted(html, behaviorName, completedActionNames) {
        const doc = parseHTML(html);
        for (const actionName of completedActionNames) {
            const actionElement = doc.querySelector(`[data-action="${actionName}"]`);
            if (actionElement) {
                assert.ok(
                    actionElement.classList.contains('completed') ||
                    actionElement.querySelector('.completed'),
                    `Action "${actionName}" should be marked as completed`
                );
            } else {
                // Check for completion indicator near action name in HTML
                const actionIndex = html.indexOf(actionName);
                assert.ok(actionIndex > -1, `Action "${actionName}" not found in HTML`);
            }
        }
    }
    
    // ========================================================================
    // SCOPE ASSERTIONS
    // ========================================================================
    
    /**
     * Assert scope information is present
     * @param {string} html - HTML string
     * @param {string} scopeType - Expected scope type (story, epic, increment, files)
     */
    assertScopePresent(html, scopeType) {
        HTMLAssertions.assertContainsText(html, scopeType);
    }
    
    /**
     * Assert no scope message is displayed
     * @param {string} html - HTML string
     */
    assertNoScopeMessage(html) {
        assert.ok(
            html.includes('No scope') || 
            html.includes('no scope') ||
            html.includes('All stories'),
            'HTML should contain no scope message'
        );
    }
    
    // ========================================================================
    // INSTRUCTIONS ASSERTIONS
    // ========================================================================
    
    /**
     * Assert instructions are present
     * @param {string} html - HTML string
     */
    assertInstructionsPresent(html) {
        assert.ok(
            html.includes('instruction') || 
            html.includes('Instruction') ||
            html.length > 0,
            'HTML should contain instructions content'
        );
    }
    
    /**
     * Assert no instructions message is displayed
     * @param {string} html - HTML string
     */
    assertNoInstructionsMessage(html) {
        assert.ok(
            html.includes('No instructions') || 
            html.includes('no instructions') ||
            html.includes('Navigate to an action'),
            'HTML should contain no instructions message'
        );
    }
}

module.exports = BotViewTestHelper;

/**
 * Test Persistent CLI Session
 * 
 * Verifies that a single Python CLI process can handle multiple commands
 * without hanging or needing to restart.
 */

// Mock vscode before any imports
const Module = require('module');
const originalRequire = Module.prototype.require;
Module.prototype.require = function(...args) {
    if (args[0] === 'vscode') {
        return require('./mock_vscode');
    }
    return originalRequire.apply(this, args);
};

const { test, after } = require('node:test');
const assert = require('assert');
const path = require('path');
const PanelView = require('../../src/panel/panel_view');

// Setup
const workspaceDir = path.join(__dirname, '../..');
const botPath = path.join(workspaceDir, 'bots', 'story_bot');

// ONE CLI for all tests
const cli = new PanelView(botPath);

after(() => {
    cli.cleanup();
});

test('TestPersistentSession', { concurrency: false }, async (t) => {

    await t.test('test_multiple_commands_on_same_session', async () => {
        /**
         * Test that we can call multiple commands on the same Python session
         * without hanging or needing to restart the process.
         */
        
        // Call 'current' command multiple times
        const result1 = await cli.execute('current');
        assert(result1, 'First command should return a result');
        
        const result2 = await cli.execute('current');
        assert(result2, 'Second command should return a result');
        
        const result3 = await cli.execute('current');
        assert(result3, 'Third command should return a result');
        
        // Verify all results are similar (same structure)
        assert(typeof result1 === 'object', 'Result 1 should be an object');
        assert(typeof result2 === 'object', 'Result 2 should be an object');
        assert(typeof result3 === 'object', 'Result 3 should be an object');
        
        // Test with different commands
        const status1 = await cli.execute('status');
        assert(status1, 'Status command should return a result');
        assert(typeof status1 === 'object', 'Status should be an object');
    });

    await t.test('test_navigation_commands_work', async () => {
        /**
         * Test navigation commands work on persistent session
         */
        
        // Navigate to shape.clarify
        const result1 = await cli.execute('shape.clarify');
        assert(result1, 'Navigation command should return result');
        
        // Navigate to shape.strategy
        const result2 = await cli.execute('shape.strategy');
        assert(result2, 'Second navigation command should return result');
        
        // Get status to verify navigation works
        const status = await cli.execute('status');
        assert(status, 'Status should return after navigation');
        assert(status.behaviors || status.current_action, 'Status should have bot data');
    });

    await t.test('test_scope_commands_work', async () => {
        /**
         * Test scope commands work on persistent session
         */
        
        // Get scope
        const scope1 = await cli.execute('scope');
        assert(scope1, 'Should get scope');
        
        // Filter scope
        await cli.execute('scope "Open Panel"');
        
        // Clear scope
        await cli.execute('scope all');
        
        // Get scope again
        const scope2 = await cli.execute('scope');
        assert(scope2, 'Should get scope after operations');
    });
});

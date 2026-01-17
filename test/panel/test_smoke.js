/**
 * Smoke Test: Panel Views with Real CLI Integration
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
const assert = require('node:assert');
const path = require('path');
const PanelView = require('../../src/panel/panel_view');
const BotView = require('../../src/panel/bot_view');
const BehaviorsView = require('../../src/panel/behaviors_view');

// Setup
const workspaceDir = path.join(__dirname, '../..');
const botPath = path.join(workspaceDir, 'bots', 'story_bot');

// ONE CLI for all tests
const cli = new PanelView(botPath);

after(() => {
    cli.cleanup();
});

test('TestPanelSmokeTest', { concurrency: false }, async (t) => {
    
    await t.test('testCLISpawnsAndResponds', async () => {
        /**
         * GIVEN: Workspace with story_bot
         * WHEN: CLI is instantiated and command executed
         * THEN: CLI returns valid response
         */
        const response = await cli.execute('status');
        
        assert.ok(response, 'Should receive response');
        assert.ok(response.behaviors || response.name, 'Should contain bot data');
    });
    
    await t.test('testBotViewRendersHTML', async () => {
        /**
         * GIVEN: Active CLI
         * WHEN: BotView renders
         * THEN: HTML is generated
         */
        const botView = new BotView(cli);
        const html = await botView.render();
        
        assert.ok(html.length > 0, 'Should render HTML');
        assert.ok(html.includes('Behavior Action Status'), 'Should have behaviors section');
        assert.ok(html.includes('Scope'), 'Should have scope section');
    });
    
    await t.test('testBehaviorsViewRendersHTML', async () => {
        /**
         * GIVEN: Active CLI
         * WHEN: BehaviorsView renders
         * THEN: HTML is generated with behaviors
         */
        const behaviorsView = new BehaviorsView(cli);
        const html = await behaviorsView.render();
        
        assert.ok(typeof html === 'string', 'Should return HTML string');
        assert.ok(html.length > 0, 'HTML should not be empty');
        assert.ok(html.includes('shape'), 'Should include shape behavior');
    });
    
    await t.test('testStatusResponseStructure', async () => {
        /**
         * GIVEN: Active CLI
         * WHEN: Status command is executed
         * THEN: Response has expected structure
         */
        const response = await cli.execute('status');
        
        assert.ok(response.behaviors, 'Should have behaviors in response');
        assert.ok(response.behaviors.all_behaviors, 'Should have all_behaviors array');
        assert.ok(response.behaviors.current, 'Should have current behavior');
        assert.ok(Array.isArray(response.behaviors.all_behaviors), 
            'all_behaviors should be array');
    });
    
    await t.test('testNavigationWorks', async () => {
        /**
         * GIVEN: Active CLI
         * WHEN: Navigation command is executed
         * THEN: Bot navigates to new position
         */
        await cli.execute('shape.clarify');
        const status = await cli.execute('status');
        
        assert.ok(status.current_action === 'clarify' || status.behaviors?.current === 'shape',
            'Should navigate to shape.clarify');
    });
});

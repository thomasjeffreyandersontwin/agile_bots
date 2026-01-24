/**
 * Get Help Through Panel Tests
 */

const Module = require('module');
const originalRequire = Module.prototype.require;
Module.prototype.require = function(...args) {
    if (args[0] === 'vscode') {
        return require('../../helpers/mock_vscode');
    }
    return originalRequire.apply(this, args);
};

const { test, after } = require('node:test');
const assert = require('node:assert');
const path = require('path');
const PanelView = require('../../../src/panel/panel_view');
const InstructionsSection = require('../../../src/panel/instructions_view');

// Setup
const workspaceDir = path.join(__dirname, '../../..');
const botPath = path.join(workspaceDir, 'bots', 'story_bot');

// ONE CLI for all tests
const cli = new PanelView(botPath);

after(() => {
    cli.cleanup();
});

test('TestGetHelpThroughPanel', { concurrency: false }, async (t) => {
    
    await t.test('testInstructionsDisplayWhenNavigatingToAction', async () => {
        await cli.execute('shape.clarify');
        
        const view = new InstructionsSection(cli);
        const html = await view.render();
        
        assert.ok(typeof html === 'string', 'Should return HTML string');
        assert.ok(html.length > 0, 'Should render content');
    });
    
    await t.test('testHelpCommandReturnsInstructions', async () => {
        const response = await cli.execute('shape.clarify.instructions');
        
        assert.ok(response.instructions, 'Should have instructions');
    });
    
    await t.test('testCurrentCommandShowsState', async () => {
        await cli.execute('shape.strategy');
        const status = await cli.execute('status');
        
        assert.ok(status.current_action, 'Should have current action');
        assert.strictEqual(status.current_action, 'strategy');
    });
});

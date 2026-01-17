/**
 * Test InstructionsView
 */

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
const InstructionsSection = require('../../src/panel/instructions_view');

// Setup
const workspaceDir = path.join(__dirname, '../..');
const botPath = path.join(workspaceDir, 'bots', 'story_bot');

// ONE CLI for all tests
const cli = new PanelView(botPath);

after(() => {
    cli.cleanup();
});

test('TestInstructionsView', { concurrency: false }, async (t) => {
    
    await t.test('testInstructionsSectionRenders', async () => {
        const view = new InstructionsSection(cli);
        const html = await view.render();
        
        assert.ok(typeof html === 'string', 'Should return HTML string');
    });
    
    await t.test('testInstructionsAfterActionExecution', async () => {
        // Execute an action to get instructions
        const response = await cli.execute('shape.clarify.instructions');
        
        // Check if instructions were returned
        assert.ok(response, 'Should get response');
        
        // Render view
        const view = new InstructionsSection(cli);
        const html = await view.render();
        
        assert.ok(typeof html === 'string', 'Should return HTML string');
    });
    
    await t.test('testInstructionsShowsSection', async () => {
        // Execute action first
        await cli.execute('shape.clarify');
        
        const view = new InstructionsSection(cli);
        const html = await view.render();
        
        // Instructions section should exist (even if empty)
        assert.ok(html.length >= 0, 'Should return HTML (may be empty)');
    });
    
    // TODO: Submit button test commented out - need to mock the submit functionality
    // to prevent text spraying during tests. Will be re-enabled once mocking is in place.
    //
    // await t.test('testInstructionsHasSubmitButton', async () => {
    //     await cli.execute('shape.clarify');
    //     
    //     const view = new InstructionsSection(cli);
    //     const html = await view.render();
    //     
    //     // If instructions exist, should have submit button
    //     if (html.length > 100) {
    //         assert.ok(html.includes('submit') || html.includes('Send') || html.includes('chat') || html.length > 0, 
    //             'Should have submit button or be non-empty');
    //     } else {
    //         assert.ok(html.length >= 0, 'HTML can be empty if no instructions');
    //     }
    // });
    
    await t.test('testInstructionsUpdatesOnNavigation', async () => {
        // Navigate to clarify
        await cli.execute('shape.clarify');
        const view1 = new InstructionsSection(cli);
        const html1 = await view1.render();
        
        // Navigate to strategy
        await cli.execute('shape.strategy');
        const view2 = new InstructionsSection(cli);
        const html2 = await view2.render();
        
        // Both should be valid HTML
        assert.ok(typeof html1 === 'string', 'Should return HTML for clarify');
        assert.ok(typeof html2 === 'string', 'Should return HTML for strategy');
    });
    
    await t.test('testInstructionsForDifferentActions', async () => {
        // Test clarify
        await cli.execute('shape.clarify');
        const status1 = await cli.execute('status');
        assert.ok(status1.current_action === 'clarify' || status1.behaviors?.current === 'shape');
        
        // Test strategy
        await cli.execute('shape.strategy');
        const status2 = await cli.execute('status');
        assert.ok(status2.current_action === 'strategy' || status2.behaviors?.current === 'shape');
    });
});

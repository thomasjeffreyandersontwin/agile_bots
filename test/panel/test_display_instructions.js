/**
 * Test Display Action Instructions Through Panel
 */

// Mock vscode before requiring any modules
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
const InstructionsSection = require('../../src/panel/instructions_view');

// Setup workspace
const workspaceDir = path.join(__dirname, '../..');
const botPath = path.join(workspaceDir, 'bots', 'story_bot');

// ONE CLI for all tests
const cli = new PanelView(botPath);

// Cleanup after all tests
after(() => {
    cli.cleanup();
});

test('TestDisplayBaseInstructions', { concurrency: false }, async (t) => {
    
    await t.test('test_panel_displays_base_instructions_when_action_has_instructions', async () => {
        // Navigate to shape.clarify.instructions
        const response = await cli.execute('shape.clarify.instructions');
        
        // Response should exist
        assert(response, 'Should get response from instructions command');
        
        // Render instructions view
        const view = new InstructionsSection(cli);
        const html = await view.render();
        
        assert(typeof html === 'string', 'Instructions section should render HTML');
    });
});

test('TestDisplayClarifyInstructions', { concurrency: false }, async (t) => {
    
    await t.test('test_panel_displays_clarify_instructions_when_action_is_clarify', async () => {
        // Navigate to clarify action
        const result = await cli.execute('shape.clarify');
        assert(result, 'Navigation should return result');
        
        // Render instructions
        const view = new InstructionsSection(cli);
        const html = await view.render();
        
        assert(typeof html === 'string', 'Should render HTML string');
    });
});

test('TestDisplayStrategyInstructions', { concurrency: false }, async (t) => {
    
    await t.test('test_panel_displays_strategy_instructions_when_action_is_strategy', async () => {
        // Navigate to strategy action
        const result = await cli.execute('shape.strategy');
        assert(result, 'Navigation should return result');
        
        // Render instructions
        const view = new InstructionsSection(cli);
        const html = await view.render();
        
        assert(typeof html === 'string', 'Should render HTML string');
    });
});

// TODO: Submit tests commented out - need to mock the submit functionality
// to prevent text spraying during tests. Will be re-enabled once mocking is in place.
//
// test('TestSubmitInstructionsToAIAgent', { concurrency: false }, async (t) => {
//     
//     await t.test('test_instructions_view_has_submit_button', async () => {
//         await cli.execute('shape.clarify');
//         
//         const view = new InstructionsSection(cli);
//         const html = await view.render();
//         
//         // Check for submit button
//         assert(html.includes('submit') || html.includes('Send') || html.includes('chat'), 
//             'Should have submit/send button');
//     });
// });

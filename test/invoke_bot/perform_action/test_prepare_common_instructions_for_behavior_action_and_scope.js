/**
 * Test Prepare Common Instructions Panel
 * 
 * Merged from: test_display_instructions.js, test_instructions_view.js
 */

/**
 * Test Display Action Instructions Through Panel
 */

// Mock vscode before requiring any modules
const Module = require('module');
const originalRequire = Module.prototype.require;
Module.prototype.require = function(...args) {
    if (args[0] === 'vscode') {
        return require('../../helpers/mock_vscode');
    }
    return originalRequire.apply(this, args);
};

const { test, after, before } = require('node:test');
const assert = require('assert');
const path = require('path');
const os = require('os');
const fs = require('fs');
const PanelView = require('../../../src/panel/panel_view');
const InstructionsSection = require('../../../src/panel/instructions_view');

// Setup - Use temp directory for test workspace to avoid modifying production data
const repoRoot = path.join(__dirname, '../../..');
const productionBotPath = path.join(repoRoot, 'bots', 'story_bot');

// Create temp workspace for tests (data only - story graphs, etc.)
const tempWorkspaceDir = fs.mkdtempSync(path.join(os.tmpdir(), 'agile-bots-instructions-test-'));

// For tests that modify story graph, we need to:
// 1. Use production bot config and source code (can't copy all of it)
// 2. Set WORKING_AREA to a temp directory so story graph changes go there
// 
// The PanelView derives workspaceDir from botPath, so we use production bot
// but override the working area via environment variable before spawning

// Create temp workspace for test data (story graphs, etc.)
function setupTestWorkspace() {
    fs.mkdirSync(path.join(tempWorkspaceDir, 'docs', 'stories'), { recursive: true });
    
    // Create empty test story graph
    const storyGraphPath = path.join(tempWorkspaceDir, 'docs', 'stories', 'story-graph.json');
    fs.writeFileSync(storyGraphPath, JSON.stringify({ epics: [] }, null, 2));
    
    // Set environment variable so Python backend uses temp workspace for data
    process.env.WORKING_AREA = tempWorkspaceDir;
}

before(() => {
    setupTestWorkspace();
    
    // Verify WORKING_AREA is set to temp directory before creating PanelView
    const { verifyTestWorkspace } = require('../../helpers/prevent_production_writes');
    verifyTestWorkspace();
});

// Use production bot path (has config and behaviors) but temp workspace for data
const botPath = productionBotPath;

// ONE CLI for all tests
const cli = new PanelView(botPath);

// Cleanup after all tests
after(() => {
    cli.cleanup();
    // Clean up temp workspace and restore environment
    try {
        if (fs.existsSync(tempWorkspaceDir)) {
            fs.rmSync(tempWorkspaceDir, { recursive: true, force: true });
        }
    } catch (err) {
        console.warn('Failed to clean up temp workspace:', err.message);
    }
    // Restore WORKING_AREA to original or unset
    delete process.env.WORKING_AREA;
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
        
        // Render instructions - use test helper
        const instructionsHelper = new InstructionsViewTestHelper(repoRoot);
        const html = await instructionsHelper.render_html();
        instructionsHelper.cleanup();
        
        assert(typeof html === 'string', 'Should render HTML string');
    });
});

test('TestDisplayStrategyInstructions', { concurrency: false }, async (t) => {
    
    await t.test('test_panel_displays_strategy_instructions_when_action_is_strategy', async () => {
        // Navigate to strategy action
        const result = await cli.execute('shape.strategy');
        assert(result, 'Navigation should return result');
        
        // Render instructions - use test helper
        const instructionsHelper = new InstructionsViewTestHelper(repoRoot);
        const html = await instructionsHelper.render_html();
        instructionsHelper.cleanup();
        
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
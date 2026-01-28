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

const { test, after, before } = require('node:test');
const assert = require('node:assert');
const path = require('path');
const os = require('os');
const fs = require('fs');
const PanelView = require('../../../src/panel/panel_view');
const InstructionsSection = require('../../../src/panel/instructions_view');

// Setup - Use temp directory for test workspace to avoid modifying production data
const repoRoot = path.join(__dirname, '../../..');
const productionBotPath = path.join(repoRoot, 'bots', 'story_bot');

// Create temp workspace for tests (data only - story graphs, etc.)
const tempWorkspaceDir = fs.mkdtempSync(path.join(os.tmpdir(), 'agile-bots-help-test-'));

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
        
        assert.ok(status.bot.current_action, 'Should have current action');
        assert.strictEqual(status.bot.current_action, 'strategy');
    });
});

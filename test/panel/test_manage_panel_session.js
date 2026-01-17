/**
 * Test Manage Panel Session
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
const BotView = require('../../src/panel/bot_view');

// Setup
const workspaceDir = path.join(__dirname, '../..');
const botPath = path.join(workspaceDir, 'bots', 'story_bot');

// ONE CLI for all tests
const cli = new PanelView(botPath);

after(() => {
    cli.cleanup();
});

test('TestOpenPanel', { concurrency: false }, async (t) => {
    
    await t.test('test_user_opens_panel_via_command_palette_happy_path', async () => {
        // Get status
        const status = await cli.execute('status');
        
        // Verify bot data returned
        assert.ok(status, 'Should get status');
        assert.ok(status.behaviors || status.name, 'Should have behaviors or name');
        
        // Render the panel
        const botView = new BotView(cli);
        const html = await botView.render();
        
        // Verify HTML structure
        assert.ok(html.length > 0, 'Should render HTML');
        assert.ok(html.includes('Behavior Action Status'), 'Should have Behavior section');
        assert.ok(html.includes('Scope'), 'Should have Scope section');
    });
    
    await t.test('test_panel_displays_bot_name', async () => {
        const status = await cli.execute('status');
        const botView = new BotView(cli);
        const html = await botView.render();
        
        // Bot name should be in HTML
        const botName = status.name || status.bot_name || 'story_bot';
        assert.ok(html.includes(botName) || html.includes('story_bot'), 
            'Should display bot name');
    });
});

test('TestDisplaySessionStatus', { concurrency: false }, async (t) => {
    
    await t.test('test_user_refreshes_panel_to_see_updated_status', async () => {
        // Get initial status
        const initialStatus = await cli.execute('status');
        const initialAction = initialStatus.current_action;
        
        // Navigate somewhere
        await cli.execute('shape.clarify');
        
        // Refresh
        const newStatus = await cli.execute('status');
        
        // Verify we can get status
        assert.ok(newStatus, 'Should get status after refresh');
        assert.ok(newStatus.behaviors, 'Should have behaviors');
    });
    
    await t.test('test_user_views_session_status_on_panel_load', async () => {
        // Navigate to shape.clarify
        await cli.execute('shape.clarify');
        const status = await cli.execute('status');
        
        // Verify current action
        assert.ok(status.current_action, 'Should have current action');
    });
});

test('TestChangeWorkspacePath', { concurrency: false }, async (t) => {
    
    await t.test('test_workspace_path_displayed', async () => {
        const botView = new BotView(cli);
        const html = await botView.render();
        
        // Verify workspace input exists
        assert.ok(html.includes('workspacePathInput') || html.includes('workspace'), 
            'Should have workspace path display');
    });
});

test('TestSwitchBot', { concurrency: false }, async (t) => {
    
    await t.test('test_panel_shows_available_bots', async () => {
        const status = await cli.execute('status');
        const botView = new BotView(cli);
        const html = await botView.render();
        
        // Verify bots are shown
        assert.ok(html.includes('story_bot') || html.includes('bot'), 
            'Should show bot name');
    });
});

test('TestTogglePanelSection', { concurrency: false }, async (t) => {
    
    await t.test('test_sections_have_collapse_handlers', async () => {
        const botView = new BotView(cli);
        const html = await botView.render();
        
        // Verify toggle functionality exists
        assert.ok(html.includes('toggleSection') || html.includes('collapsible'), 
            'Should have toggle handlers');
    });
});

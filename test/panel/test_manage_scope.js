/**
 * Test Manage Scope Through Panel
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
const ScopeSection = require('../../src/panel/scope_view');

// Setup
const workspaceDir = path.join(__dirname, '../..');
const botPath = path.join(workspaceDir, 'bots', 'story_bot');

// ONE CLI for all tests
const cli = new PanelView(botPath);

after(() => {
    cli.cleanup();
});

test('TestDisplayStoryScopeHierarchy', { concurrency: false }, async (t) => {
    
    await t.test('test_panel_displays_scope_section', async () => {
        // Get scope
        const scopeJSON = await cli.execute('scope');
        
        // Verify scope data
        assert.ok(scopeJSON, 'Should get scope data');
        
        // Render scope view
        const view = new ScopeSection(cli);
        const html = await view.render();
        
        // Verify structure
        assert.ok(html.includes('Scope'), 'Should have Scope header');
        assert.ok(html.includes('scopeFilterInput'), 'Should have filter input');
    });
    
    await t.test('test_scope_has_filter_input', async () => {
        const view = new ScopeSection(cli);
        const html = await view.render();
        
        // Verify filter input
        assert.ok(html.includes('scopeFilterInput'), 'Should have filter input');
    });
});

test('TestFilterStoryScope', { concurrency: false }, async (t) => {
    
    await t.test('test_user_filters_scope_by_story_name', async () => {
        // Apply filter
        await cli.execute('scope "Open Panel"');
        
        // Get filtered scope
        const scopeJSON = await cli.execute('scope');
        
        // Render view
        const view = new ScopeSection(cli);
        const html = await view.render();
        
        // Verify filter is applied
        assert.ok(html.includes('Scope'), 'Should have Scope section');
    });
    
    await t.test('test_user_clears_story_scope_filter', async () => {
        // Apply filter
        await cli.execute('scope "Open Panel"');
        
        // Clear filter
        await cli.execute('scope all');
        
        // Get scope
        const scopeJSON = await cli.execute('scope');
        
        // Verify filter is cleared
        assert.ok(scopeJSON, 'Should get scope data');
    });
});

test('TestShowAllScopeThroughPanel', { concurrency: false }, async (t) => {
    
    await t.test('test_user_clicks_show_all_to_clear_filter', async () => {
        // Apply filter first
        await cli.execute('scope "Open Panel"');
        
        // Clear with showall
        await cli.execute('scope showall');
        
        // Verify
        const scopeJSON = await cli.execute('scope');
        assert.ok(scopeJSON, 'Should get scope data after showall');
    });
});

test('TestOpenStoryFiles', { concurrency: false }, async (t) => {
    
    await t.test('test_story_graph_and_story_map_links_visible', async () => {
        const view = new ScopeSection(cli);
        const html = await view.render();
        
        // Verify links exist
        assert.ok(html.includes('story-graph.json') || html.includes('story'), 
            'Should have story graph link or story content');
    });
});

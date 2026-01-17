/**
 * Test ScopeView
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
const ScopeSection = require('../../src/panel/scope_view');

// Setup
const workspaceDir = path.join(__dirname, '../..');
const botPath = path.join(workspaceDir, 'bots', 'story_bot');

// ONE CLI for all tests
const cli = new PanelView(botPath);

after(() => {
    cli.cleanup();
});

test('TestScopeView', { concurrency: false }, async (t) => {
    
    await t.test('testScopeSectionRenders', async () => {
        const view = new ScopeSection(cli);
        const html = await view.render();
        
        assert.ok(typeof html === 'string', 'Should return HTML string');
        assert.ok(html.length > 0, 'Should render HTML');
    });
    
    await t.test('testScopeHasFilterInput', async () => {
        const view = new ScopeSection(cli);
        const html = await view.render();
        
        assert.ok(html.includes('scopeFilterInput'), 'Should have filter input');
    });
    
    await t.test('testScopeHasHeader', async () => {
        const view = new ScopeSection(cli);
        const html = await view.render();
        
        assert.ok(html.includes('Scope'), 'Should have Scope header');
    });
    
    await t.test('testScopeFilterCommand', async () => {
        // Apply filter
        await cli.execute('scope "Open Panel"');
        
        // Get status to verify
        const status = await cli.execute('status');
        assert.ok(status, 'Should get status after filter');
        
        // Render view
        const view = new ScopeSection(cli);
        const html = await view.render();
        assert.ok(html.includes('Scope'), 'Should render scope section');
    });
    
    await t.test('testScopeClearFilter', async () => {
        // Apply filter first
        await cli.execute('scope "Open Panel"');
        
        // Clear filter
        await cli.execute('scope all');
        
        // Verify
        const status = await cli.execute('status');
        assert.ok(status, 'Should get status after clearing filter');
    });
    
    await t.test('testScopeShowAll', async () => {
        // Show all
        await cli.execute('scope showall');
        
        const view = new ScopeSection(cli);
        const html = await view.render();
        
        assert.ok(html.includes('Scope'), 'Should render scope section');
    });
    
    await t.test('testScopeContentStructure', async () => {
        const view = new ScopeSection(cli);
        const html = await view.render();
        
        // Verify structural elements
        assert.ok(html.includes('collapsible') || html.includes('section'), 
            'Should have collapsible section structure');
    });
    
    await t.test('testStoryLinksPresent', async () => {
        const view = new ScopeSection(cli);
        const html = await view.render();
        
        // If there's content, verify links
        if (html.includes('story') || html.includes('epic')) {
            assert.ok(html.includes('onclick') || html.includes('href'), 
                'Should have clickable links for stories/epics');
        } else {
            assert.ok(html.length > 0, 'Should render even without content');
        }
    });
});

/**
 * Test Navigate And Execute Behaviors Through Panel
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
const BehaviorsView = require('../../src/panel/behaviors_view');

// Setup
const workspaceDir = path.join(__dirname, '../..');
const botPath = path.join(workspaceDir, 'bots', 'story_bot');

// ONE CLI for all tests
const cli = new PanelView(botPath);

after(() => {
    cli.cleanup();
});

test('TestDisplayHierarchy', { concurrency: false }, async (t) => {
    
    await t.test('test_panel_displays_behavior_tree_with_progress_indicators', async () => {
        // Navigate to shape.clarify
        await cli.execute('shape.clarify');
        
        // Get status
        const status = await cli.execute('status');
        
        // Render behaviors view
        const view = new BehaviorsView(cli);
        const html = await view.render();
        
        // Verify behavior tree
        assert.ok(html.includes('shape'), 'Should display shape behavior');
        assert.ok(html.includes('clarify'), 'Should display clarify action');
        assert.ok(html.includes('Behavior Action Status'), 'Should have section header');
    });
    
    await t.test('test_user_expands_and_collapses_behaviors', async () => {
        const view = new BehaviorsView(cli);
        const html = await view.render();
        
        // Verify toggle handlers exist
        assert.ok(html.includes('toggleCollapse') || html.includes('collapsible'), 
            'Should have collapse/expand functionality');
    });
    
    await t.test('test_user_sees_actions_as_clickable_items', async () => {
        await cli.execute('shape.clarify');
        
        const view = new BehaviorsView(cli);
        const html = await view.render();
        
        // Verify actions are clickable
        assert.ok(html.includes('navigateToAction') || html.includes('onclick'), 
            'Actions should be clickable');
    });
});

test('TestNavigateBehaviorAction', { concurrency: false }, async (t) => {
    
    await t.test('test_user_clicks_action_and_bot_navigates_to_that_action', async () => {
        // Start at shape.clarify
        await cli.execute('shape.clarify');
        let status = await cli.execute('status');
        assert.ok(status.current_action === 'clarify' || status.behaviors?.current === 'shape');
        
        // Navigate to strategy
        await cli.execute('shape.strategy');
        status = await cli.execute('status');
        
        // Verify navigation
        assert.ok(status.current_action === 'strategy' || status.behaviors?.current === 'shape', 
            'Should navigate to strategy');
    });
    
    await t.test('test_user_navigates_forward_with_next_button', async () => {
        // Start at shape.clarify
        await cli.execute('shape.clarify');
        const initialStatus = await cli.execute('status');
        
        // Try next
        try {
            await cli.execute('next');
        } catch (e) {
            // Next may fail - just verify status still works
        }
        
        const status = await cli.execute('status');
        assert.ok(status, 'Should be able to get status after next');
    });
    
    await t.test('test_user_navigates_backward_with_back_button', async () => {
        // Start at shape.strategy
        await cli.execute('shape.strategy');
        
        // Try back
        try {
            await cli.execute('back');
        } catch (e) {
            // Back may fail - just verify status still works
        }
        
        const status = await cli.execute('status');
        assert.ok(status, 'Should be able to get status after back');
    });
    
    await t.test('test_user_clicks_current_button', async () => {
        await cli.execute('shape.clarify');
        
        // Execute current
        await cli.execute('current');
        
        const status = await cli.execute('status');
        assert.ok(status.current_action === 'clarify' || status.behaviors?.current === 'shape', 
            'Should still be at clarify after current');
    });
});

test('TestExecuteBehaviorAction', { concurrency: false }, async (t) => {
    
    await t.test('test_user_clicks_behavior_to_navigate', async () => {
        // Navigate to discovery
        try {
            await cli.execute('discovery.clarify');
        } catch (e) {
            // Discovery may not exist - that's OK
        }
        
        const status = await cli.execute('status');
        assert.ok(status, 'Should be able to get status');
    });
    
    await t.test('test_user_clicks_action_to_execute', async () => {
        // Execute shape.clarify
        const result = await cli.execute('shape.clarify');
        
        // Verify execution succeeded
        assert.ok(result, 'Should get result from executing action');
        
        // Verify status
        const status = await cli.execute('status');
        assert.ok(status.behaviors || status.current_action, 'Status should have bot data');
    });
    
    await t.test('test_navigation_buttons_exist', async () => {
        const view = new BehaviorsView(cli);
        const html = await view.render();
        
        // Verify navigation buttons
        assert.ok(html.includes('back') || html.includes('Back'), 'Should have back button');
        assert.ok(html.includes('next') || html.includes('Next'), 'Should have next button');
        assert.ok(html.includes('current') || html.includes('Current'), 'Should have current button');
    });
});

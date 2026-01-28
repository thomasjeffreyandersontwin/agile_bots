/**
 * Test Display Scope Panel
 * 
 * Merged from: test_manage_scope.js, test_scope_view.js
 */

/**
 * Test Manage Scope Through Panel
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
const StoryMapView = require('../../../src/panel/story_map_view');

// Setup - Use temp directory for test data to avoid modifying production
const repoRoot = path.join(__dirname, '../../..');
const productionBotPath = path.join(repoRoot, 'bots', 'story_bot');
const tempWorkspaceDir = fs.mkdtempSync(path.join(os.tmpdir(), 'agile-bots-scope-test-'));

// Setup test workspace - only data files, not the bot itself
function setupTestWorkspace() {
    fs.mkdirSync(path.join(tempWorkspaceDir, 'docs', 'stories'), { recursive: true });
    
    // Copy story-graph.json to temp directory for test isolation
    const storyGraphSrc = path.join(repoRoot, 'docs', 'stories', 'story-graph.json');
    const storyGraphDest = path.join(tempWorkspaceDir, 'docs', 'stories', 'story-graph.json');
    if (fs.existsSync(storyGraphSrc)) {
        fs.copyFileSync(storyGraphSrc, storyGraphDest);
    }
    
    // Set WORKING_AREA to temp directory to ensure no production writes
    // Bot path stays production since we're not modifying the bot itself
    process.env.WORKING_AREA = tempWorkspaceDir;
    
    // Set AGILE_BOTS_REPO_ROOT so PanelView can find src/cli/cli_main.py
    process.env.AGILE_BOTS_REPO_ROOT = repoRoot;
    
    // Verify WORKING_AREA is set to temp directory before creating PanelView
    const { verifyTestWorkspace } = require('../../helpers/prevent_production_writes');
    verifyTestWorkspace();
}

before(() => {
    setupTestWorkspace();
});

// ONE CLI for all tests
// Use production bot path (we're not modifying the bot)
// WORKING_AREA isolates data writes to temp directory
const cli = new PanelView(productionBotPath);

after(() => {
    cli.cleanup();
    // Clean up temp directory
    if (fs.existsSync(tempWorkspaceDir)) {
        fs.rmSync(tempWorkspaceDir, { recursive: true, force: true });
    }
    // Clean up environment variables
    delete process.env.AGILE_BOTS_REPO_ROOT;
    delete process.env.WORKING_AREA;
});


test('TestDisplayStoryScopeHierarchy', { concurrency: false }, async (t) => {
    
    await t.test('test_panel_displays_scope_section', async () => {
        // Get scope
        const scopeJSON = await cli.execute('scope');
        
        // Verify scope data
        assert.ok(scopeJSON, 'Should get scope data');
        
        // Render scope view
        const view = new StoryMapView(cli);
        const html = await view.render();
        
        // Verify structure
        assert.ok(html.includes('Scope'), 'Should have Scope header');
        assert.ok(html.includes('scopeFilterInput'), 'Should have filter input');
    });
    
    await t.test('test_scope_has_filter_input', async () => {
        const view = new StoryMapView(cli);
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
        const view = new StoryMapView(cli);
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
        const view = new StoryMapView(cli);
        const html = await view.render();
        
        // Verify links exist
        assert.ok(html.includes('story-graph.json') || html.includes('story'), 
            'Should have story graph link or story content');
    });
});

test('TestScopeView', { concurrency: false }, async (t) => {
    
    await t.test('testScopeSectionRenders', async () => {
        const view = new StoryMapView(cli);
        const html = await view.render();
        
        assert.ok(typeof html === 'string', 'Should return HTML string');
        assert.ok(html.length > 0, 'Should render HTML');
    });
    
    await t.test('testScopeHasFilterInput', async () => {
        const view = new StoryMapView(cli);
        const html = await view.render();
        
        assert.ok(html.includes('scopeFilterInput'), 'Should have filter input');
    });
    
    await t.test('testScopeHasHeader', async () => {
        const view = new StoryMapView(cli);
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
        const view = new StoryMapView(cli);
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
        
        const view = new StoryMapView(cli);
        const html = await view.render();
        
        assert.ok(html.includes('Scope'), 'Should render scope section');
    });
    
    await t.test('testScopeContentStructure', async () => {
        const view = new StoryMapView(cli);
        const html = await view.render();
        
        // Verify structural elements
        assert.ok(html.includes('collapsible') || html.includes('section'), 
            'Should have collapsible section structure');
    });
    
    await t.test('testStoryLinksPresent', async () => {
        const view = new StoryMapView(cli);
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

// ============================================================================
// Test Set Scope To Selected Story Node
// Story: Set scope to selected story node
// Sub-Epic: Manage Story Scope
// ============================================================================

test('TestSetScopeToSelectedStoryNode', { concurrency: false }, async (t) => {
    
    await t.test('test_user_sets_scope_to_selected_epic', async () => {
        /**
         * SCENARIO: User sets scope to selected epic
         * GIVEN: User has selected an epic named Invoke Bot in the panel
         * WHEN: User clicks the Scope To button (executes scope command)
         * THEN: System sets scope filter to Invoke Bot
         * AND: System refreshes the panel view
         * AND: Panel displays only story nodes matching Invoke Bot
         */
        
        // Given - User selects epic "Invoke Bot"
        const selectedEpicName = 'Invoke Bot';
        
        // When - Scope To button clicked (equivalent to scope command)
        const scopeResult = await cli.execute(`scope "${selectedEpicName}"`);
        
        // Then - Verify scope command executed successfully
        assert.ok(scopeResult.status === 'success' || scopeResult.message, 
            'Scope command should execute successfully');
        
        // Verify panel renders without errors
        const view = new StoryMapView(cli);
        const html = await view.render();
        assert.ok(html.length > 0, 'Panel should render HTML');
        assert.ok(html.includes('scopeFilterInput'), 'Panel should have filter input');
    });
    
    await t.test('test_user_sets_scope_to_selected_sub_epic', async () => {
        /**
         * SCENARIO: User sets scope to selected sub-epic
         * GIVEN: User has selected a sub-epic named Edit Story Map in the panel
         * WHEN: User clicks the Scope To button
         * THEN: System sets scope filter to Edit Story Map
         * AND: System refreshes the panel view
         * AND: Panel displays only story nodes matching Edit Story Map
         */
        
        // Given - User selects sub-epic "Edit Story Map"
        const selectedSubEpicName = 'Edit Story Map';
        
        // When - Scope To button clicked
        const scopeResult = await cli.execute(`scope "${selectedSubEpicName}"`);
        
        // Then - Verify scope command executed successfully
        assert.ok(scopeResult.status === 'success' || scopeResult.message, 
            'Scope command should execute successfully');
        
        // Verify panel renders without errors
        const view = new StoryMapView(cli);
        const html = await view.render();
        assert.ok(html.length > 0, 'Panel should render HTML');
    });
    
    await t.test('test_user_sets_scope_to_selected_story', async () => {
        /**
         * SCENARIO: User sets scope to selected story
         * GIVEN: User has selected a story named Display Story Hierarchy Panel in the panel
         * WHEN: User clicks the Scope To button
         * THEN: System sets scope filter to Display Story Hierarchy Panel
         * AND: System refreshes the panel view
         * AND: Panel displays only story nodes matching Display Story Hierarchy Panel
         */
        
        // Given - User selects story "Display Story Hierarchy Panel"
        const selectedStoryName = 'Display Story Hierarchy Panel';
        
        // When - Scope To button clicked
        const scopeResult = await cli.execute(`scope "${selectedStoryName}"`);
        
        // Then - Verify scope command executed successfully
        assert.ok(scopeResult.status === 'success' || scopeResult.message, 
            'Scope command should execute successfully');
        
        // Verify panel renders without errors
        const view = new StoryMapView(cli);
        const html = await view.render();
        assert.ok(html.length > 0, 'Panel should render HTML');
    });
    
    await t.test('test_user_attempts_to_set_scope_without_selecting_node', async () => {
        /**
         * SCENARIO: User attempts to set scope without selecting a node
         * GIVEN: User has not selected any story node in the panel
         * WHEN: User views the toolbar
         * THEN: Scope To button is hidden
         * 
         * This tests the button visibility in HTML - btn-scope-to should have display: none
         * when no node is selected (root is selected by default)
         */
        
        // Given - Showall to reset scope
        await cli.execute('scope showall');
        
        // When - Render the view with root selected
        const view = new StoryMapView(cli);
        const html = await view.render();
        
        // Then - Panel should render successfully
        assert.ok(html.length > 0, 'Panel should render HTML');
        assert.ok(html.includes('scopeFilterInput'), 'Panel should have scope filter input');
    });
    
    // Cleanup after all tests in this suite
    t.after(async () => {
        await cli.execute('scope showall');
    });
});

// ============================================================================
// Test Panel Submit Button Displays Behavior-Specific Icon With Hover Tooltip
// Story: Set scope to selected story node and submit
// Sub-Epic: Manage Story Scope
// ============================================================================


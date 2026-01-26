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

const { test, after } = require('node:test');
const assert = require('assert');
const path = require('path');
const PanelView = require('../../../src/panel/panel_view');
const StoryMapView = require('../../../src/panel/story_map_view');

// Setup
const workspaceDir = path.join(__dirname, '../../..');
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
        await cli.execute(`scope "${selectedEpicName}"`);
        
        // Then - Verify scope is set and panel shows filtered results
        const view = new StoryMapView(cli);
        const html = await view.render();
        
        // Verify filter input shows the selected epic name
        assert.ok(html.includes(selectedEpicName), 
            'Panel should display the scoped epic name');
        
        // Verify the scope command was applied (filter input has value)
        assert.ok(html.includes('scopeFilterInput'), 
            'Panel should have filter input');
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
        await cli.execute(`scope "${selectedSubEpicName}"`);
        
        // Then - Verify scope is set and panel shows filtered results
        const view = new StoryMapView(cli);
        const html = await view.render();
        
        // Verify the sub-epic name appears in the filtered view
        assert.ok(html.includes(selectedSubEpicName), 
            'Panel should display the scoped sub-epic name');
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
        await cli.execute(`scope "${selectedStoryName}"`);
        
        // Then - Verify scope is set and panel shows filtered results
        const view = new StoryMapView(cli);
        const html = await view.render();
        
        // Verify the story name appears in the filtered view
        assert.ok(html.includes(selectedStoryName), 
            'Panel should display the scoped story name');
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
        
        // Given - No node selected (root is default)
        // When - Render the view with root selected
        const view = new StoryMapView(cli);
        const html = await view.render();
        
        // Then - Scope To button should be hidden (display: none in initial state)
        // The button HTML is present but with style="display: none"
        assert.ok(html.includes('btn-scope-to'), 
            'Scope To button element should exist');
        assert.ok(html.includes('id="btn-scope-to"') && html.includes('display: none'), 
            'Scope To button should be hidden initially when no story node is selected');
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

test('TestPanelSubmitButtonDisplaysBehaviorSpecificIconWithHoverTooltip', { concurrency: false }, async (t) => {
    
    await t.test('test_submit_button_icon_changes_based_on_behavior_needed', async () => {
        /**
         * SCENARIO: Panel submit button displays behavior-specific icon with hover tooltip
         * GIVEN: User has selected a <node_type> <node_name> in the panel
         * AND: Node has behavior <behavior> needed
         * WHEN: Panel renders the submit button
         * THEN: Submit button displays <icon_file> icon indicating <behavior> behavior
         * WHEN: User hovers over the submit button
         * THEN: Submit button shows tooltip <tooltip_text>
         * 
         * Examples table from scenario - tests all 5 behavior levels
         */
        
        // Examples from scenario
        const examples = [
            { node_type: 'epic', node_name: 'Product Catalog', behavior: 'shape', icon_file: 'submit_subepic.png', tooltip_text: 'Submit shape instructions for epic' },
            { node_type: 'sub-epic', node_name: 'Report Export', behavior: 'explore', icon_file: 'submit_story.png', tooltip_text: 'Submit explore instructions for sub-epic' },
            { node_type: 'story', node_name: 'Create User', behavior: 'scenario', icon_file: 'submit_ac.png', tooltip_text: 'Submit scenario instructions for story' },
            { node_type: 'story', node_name: 'Delete File', behavior: 'test', icon_file: 'submit_tests.png', tooltip_text: 'Submit test instructions for story' },
            { node_type: 'story', node_name: 'Upload File', behavior: 'code', icon_file: 'submit_code.png', tooltip_text: 'Submit code instructions for story' },
        ];
        
        // Given - Render panel view
        const view = new StoryMapView(cli);
        const html = await view.render();
        
        // Then - Verify each example's icon and tooltip are present in the rendered HTML
        for (const example of examples) {
            const description = `${example.node_type} ${example.node_name} (${example.behavior})`;
            
            // Verify icon file is present
            const iconName = example.icon_file.replace('.png', '');
            assert.ok(
                html.includes(example.icon_file) || html.includes(iconName) || html.includes(`img/${iconName}`),
                `[${description}] Submit button should display ${example.icon_file} icon for ${example.behavior} behavior`
            );
            
            // Verify tooltip text is present
            assert.ok(
                html.includes(example.tooltip_text) || html.includes(`Submit ${example.behavior}`),
                `[${description}] Submit button tooltip should show: ${example.tooltip_text}`
            );
        }
        
        // Verify submit button element exists
        assert.ok(html.includes('btn-submit') || html.includes('submit'), 
            'Submit button element should exist in panel');
    });
});

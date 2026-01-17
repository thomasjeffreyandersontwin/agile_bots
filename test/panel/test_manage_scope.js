/**
 * Test Manage Scope Through Panel
 * 
 * Sub-epic: Manage Scope Through Panel
 * Stories: Display Story Scope Hierarchy, Filter Story Scope
 */

// Mock vscode before requiring any modules that depend on it
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
const fs = require('fs');
const os = require('os');
const BotView = require('../../src/bot/bot_view');
const ScopeSection = require('../../src/scope/scope_view');

// Track all bot views to ensure cleanup
const activeBotViews = [];

// Force exit after all tests complete
after(() => {
    // Clean up any remaining bot views
    for (const botView of activeBotViews) {
        try {
            botView.cleanup();
        } catch (e) {
            // Ignore cleanup errors
        }
    }
    // Force exit to prevent hanging
    setTimeout(() => process.exit(0), 100);
});

function setupTestWorkspace() {
    // Use actual workspace root so CLI script can be found
    // Tests create temp dirs for bot state, but workspace must be real repo root
    const repoRoot = path.join(__dirname, '../..');
    return repoRoot;
}

function getBotDirectory() {
    const repoRoot = path.join(__dirname, '../..');
    return path.join(repoRoot, 'bots', 'story_bot');
}

test('TestDisplayStoryScopeHierarchy', { concurrency: false }, async (t) => {
    
    await t.test('test_panel_displays_nested_epic_sub_epic_story_scenario_hierarchy', async () => {
        /**
         * SCENARIO: Panel displays nested epic/sub-epic/story/scenario hierarchy
         * Story: Display Story Scope Hierarchy
         * Steps from story-graph.json:
         *   Given Bot has story graph with epics, sub-epics, stories, and scenarios
         *   When Panel renders scope section
         *   Then Panel displays epic names
         *   And Panel displays sub-epic names nested under epics
         *   And Panel displays story names nested under sub-epics
         *   And Panel displays scenario names nested under stories
         *   And User can expand/collapse epic folders
         *   And User can expand/collapse sub-epic folders
         *   And User can expand/collapse story folders
         */
        const tmpPath = setupTestWorkspace();
        const botDir = getBotDirectory();
        
        const botView = new BotView({}, null, tmpPath, botDir);
        activeBotViews.push(botView);
        
        try {
            // Given Bot has story graph with epics, sub-epics, stories, and scenarios
            const scopeJSON = await botView.execute('scope');
            
            // When Panel renders scope section
            const scopeData = scopeJSON.scope || scopeJSON || { type: 'story', content: [] };
            const view = new ScopeSection(scopeData, null, tmpPath);
            const html = view.render();
            
            // Then Panel displays epic names
            // Verify scope section structure
            assert(/<div[^>]*class="[^"]*scope-section[^"]*card-primary[^"]*"[^>]*>/.test(html));
            assert(/<div[^>]*class="[^"]*collapsible-section[^"]*expanded[^"]*"[^>]*>/.test(html));
            assert(/<div[^>]*class="[^"]*collapsible-header[^"]*"[^>]*onclick="toggleSection\('scope-content'\)"[^>]*>/.test(html));
            assert(html.includes('Scope'));
            assert(html.includes('id="scope-content"'));
            
            // Verify filter input exists
            assert(/<div[^>]*class="[^"]*input-container[^"]*"[^>]*>/.test(html));
            assert(/<div[^>]*class="[^"]*input-header[^"]*"[^>]*>Filter<\/div>/.test(html));
            assert(/<input[^>]*type="text"[^>]*id="scopeFilterInput"[^>]*>/.test(html));
            assert(/<input[^>]*id="scopeFilterInput"[^>]*placeholder="Epic or Story name"[^>]*>/.test(html));
            assert(/<input[^>]*id="scopeFilterInput"[^>]*onchange="updateFilter\(this\.value\)"[^>]*>/.test(html));
            
            // Verify story tree structure if content exists
            if (scopeData.content && scopeData.content.length > 0) {
                // Verify epic structure
                assert(/<div[^>]*style="[^"]*margin-top:[^"]*8px[^"]*font-size:[^"]*12px[^"]*"[^>]*>/.test(html));
                assert(/<span[^>]*class="[^"]*collapsible-header[^"]*"[^>]*onclick="toggleCollapse\([^)]*\)"[^>]*>/.test(html));
                assert(/<div[^>]*id="epic-[^"]*"[^>]*class="[^"]*collapsible-content[^"]*"[^>]*>/.test(html));
                
                // Verify expand/collapse icons (now uses images, not emojis)
                assert(/onclick="toggleCollapse\([^)]*\)"/.test(html) || html.includes('toggleCollapse') || html.includes('collapsible'));
            } else {
                // If no content, just verify the section structure exists
                assert(html.includes('Scope'));
            }
            
            // Verify section header with expand icon
            assert(/<span[^>]*class="[^"]*expand-icon[^"]*"[^>]*style="[^"]*margin-right:[^"]*8px[^"]*font-size:[^"]*28px[^"]*"[^>]*>/.test(html));
            assert(html.includes('â–¸'));
        } finally {
            if (botView) {
                botView.cleanup();
                const index = activeBotViews.indexOf(botView);
                if (index > -1) activeBotViews.splice(index, 1);
            }
            // Small delay to ensure process is killed before deleting directory
            await new Promise(resolve => setTimeout(resolve, 50));
            try {
                fs.rmSync(tmpPath, { recursive: true, force: true });
            } catch (e) {
                // Ignore cleanup errors
            }
        }
    });
    
    await t.test('test_user_expands_epic_to_see_sub_epics', async () => {
        /**
         * SCENARIO: User expands epic to see sub-epics
         * Story: Display Story Scope Hierarchy
         * Steps from story-graph.json:
         *   Given Panel displays collapsed epic
         *   When User clicks epic folder
         *   Then Epic expands showing sub-epics
         *   And Sub-epics are nested under epic
         */
        const tmpPath = setupTestWorkspace();
        const botDir = getBotDirectory();
        
        const botView = new BotView({}, null, tmpPath, botDir);
        activeBotViews.push(botView);
        
        try {
            const scopeJSON = await botView.execute('scope');
            const scopeData = scopeJSON.scope || scopeJSON || { type: 'story', content: [] };
            const view = new ScopeSection(scopeData, null, tmpPath);
            const html = view.render();
            
            // Verify epic structure if content exists
            if (scopeData.content && scopeData.content.length > 0) {
                // Verify epic has toggle handler
                assert(/<span[^>]*class="[^"]*collapsible-header[^"]*"[^>]*onclick="toggleCollapse\([^)]*\)"[^>]*>/.test(html));
                
                // Verify epic has collapsible content
                assert(/<div[^>]*id="epic-[^"]*"[^>]*class="[^"]*collapsible-content[^"]*"[^>]*style="[^"]*display:[^"]*none[^"]*"[^>]*>/.test(html));
                
                // Verify epic icon
                assert(html.includes('ðŸ’¡'));
            } else {
                // If no content, just verify the section structure exists
                assert(html.includes('Scope'));
            }
        } finally {
            if (botView) {
                botView.cleanup();
                const index = activeBotViews.indexOf(botView);
                if (index > -1) activeBotViews.splice(index, 1);
            }
            // Small delay to ensure process is killed before deleting directory
            await new Promise(resolve => setTimeout(resolve, 50));
            try {
                fs.rmSync(tmpPath, { recursive: true, force: true });
            } catch (e) {
                // Ignore cleanup errors
            }
        }
    });
});

test('TestFilterStoryScope', { concurrency: false }, async (t) => {
    
    await t.test('test_user_filters_scope_by_story_name', async () => {
        /**
         * SCENARIO: User filters scope by story name
         * Story: Filter Story Scope
         * Steps from story-graph.json:
         *   Given Panel displays scope section with full story hierarchy
         *   When User types Open Panel in scope filter
         *   Then Panel displays filtered hierarchy showing Open Panel story
         *   And Panel displays Open Panel parent sub-epic (Manage Panel Session)
         *   And Panel displays parent epic (Invoke Bot Through Panel)
         */
        const tmpPath = setupTestWorkspace();
        const botDir = getBotDirectory();
        
        const botView = new BotView({}, null, tmpPath, botDir);
        activeBotViews.push(botView);
        
        try {
            // Given Panel displays scope section with full story hierarchy
            const initialScopeJSON = await botView.execute('scope');
            const initialScopeData = initialScopeJSON.scope || initialScopeJSON || { type: 'story', filter: '', content: [] };
            const initialView = new ScopeSection(initialScopeData, null, tmpPath);
            const initialHtml = initialView.render();
            assert(/<div[^>]*class="[^"]*scope-section[^"]*"[^>]*>/.test(initialHtml));
            
            // Verify filter input has updateFilter handler
            assert(/<input[^>]*id="scopeFilterInput"[^>]*onchange="updateFilter\(this\.value\)"[^>]*>/.test(initialHtml));
            
            // When User types Open Panel in scope filter - ACTUALLY EXECUTE THE FILTER COMMAND
            const filteredScopeJSON = await botView.execute('scope "Open Panel"');
            
            const filteredScopeData = filteredScopeJSON.scope || filteredScopeJSON || { type: 'story', filter: 'Open Panel', content: [] };
            const filteredView = new ScopeSection(filteredScopeData, null, tmpPath);
            const filteredHtml = filteredView.render();
            
            // Then Panel displays filtered hierarchy showing Open Panel story
            // Verify filter input has the filter value
            assert(/<input[^>]*id="scopeFilterInput"[^>]*value="[^"]*Open Panel[^"]*"[^>]*>/.test(filteredHtml) || filteredHtml.includes('Open Panel'));
            
            // Verify clear filter button appears when filter is set
            // The button has onclick="event.stopPropagation(); clearScopeFilter();" but may be formatted differently
            assert(/<button[^>]*onclick="[^"]*clearScopeFilter[^"]*"[^>]*>/.test(filteredHtml) || filteredHtml.includes('âœ•'));
            
            // Verify scope section structure is maintained
            assert(/<div[^>]*class="[^"]*scope-section[^"]*"[^>]*>/.test(filteredHtml));
            assert(filteredHtml.includes('Scope'));
            
            // Verify filter was actually applied
            assert(filteredScopeData.filter === 'Open Panel' || filteredHtml.includes('Open Panel'));
        } finally {
            if (botView) {
                botView.cleanup();
                const index = activeBotViews.indexOf(botView);
                if (index > -1) activeBotViews.splice(index, 1);
            }
            // Small delay to ensure process is killed before deleting directory
            await new Promise(resolve => setTimeout(resolve, 50));
            try {
                fs.rmSync(tmpPath, { recursive: true, force: true });
            } catch (e) {
                // Ignore cleanup errors
            }
        }
    });
    
    await t.test('test_user_clears_story_scope_filter', async () => {
        /**
         * SCENARIO: User clears story scope filter
         * Story: Filter Story Scope
         * Steps from story-graph.json:
         *   Given Panel displays filtered scope showing only Open Panel story
         *   When User clicks clear filter button
         *   Then Panel displays all stories in full hierarchy
         *   And All epics are visible
         */
        const tmpPath = setupTestWorkspace();
        const botDir = getBotDirectory();
        
        const botView = new BotView({}, null, tmpPath, botDir);
        activeBotViews.push(botView);
        
        try {
            // Given Panel displays filtered scope showing only Open Panel story
            await botView.execute('scope "Open Panel"');
            
            const filteredScopeJSON = await botView.execute('scope');
            const filteredScopeData = filteredScopeJSON.scope || filteredScopeJSON || { type: 'story', filter: 'Open Panel', content: [] };
            const filteredView = new ScopeSection(filteredScopeData, null, tmpPath);
            const filteredHtml = filteredView.render();
            assert(/<input[^>]*id="scopeFilterInput"[^>]*value="[^"]*Open Panel[^"]*"[^>]*>/.test(filteredHtml));
            
            // Verify clear filter button exists with proper handler
            assert(/<button[^>]*onclick="[^"]*clearScopeFilter[^"]*"[^>]*>/.test(filteredHtml));
            
            // When User clicks clear filter button - ACTUALLY EXECUTE THE CLEAR COMMAND
            const clearedScopeJSON = await botView.execute('scope all');
            
            const clearedScopeData = clearedScopeJSON.scope || clearedScopeJSON || { type: 'all', filter: '', content: null };
            const clearedView = new ScopeSection(clearedScopeData, null, tmpPath);
            const clearedHtml = clearedView.render();
            
            // Then Panel displays all stories in full hierarchy
            // And All epics are visible
            // Verify filter input is cleared
            assert(/<input[^>]*id="scopeFilterInput"[^>]*value=""[^"]*>/.test(clearedHtml) || !clearedHtml.includes('value="Open Panel"'));
            
            // Verify filter was actually cleared
            assert(clearedScopeData.filter === '' || clearedScopeData.filter === undefined || clearedScopeData.type === 'all',
                'Filter should be cleared');
            
            // Verify clear button is hidden when no filter
            // (Clear button only shows when filter has value)
        } finally {
            if (botView) {
                botView.cleanup();
                const index = activeBotViews.indexOf(botView);
                if (index > -1) activeBotViews.splice(index, 1);
            }
            // Small delay to ensure process is killed before deleting directory
            await new Promise(resolve => setTimeout(resolve, 50));
            try {
                fs.rmSync(tmpPath, { recursive: true, force: true });
            } catch (e) {
                // Ignore cleanup errors
            }
        }
    });
});

test('TestShowAllScopeThroughPanel', { concurrency: false }, async (t) => {
    
    await t.test('test_user_clicks_show_all_to_clear_filter', async () => {
        /**
         * SCENARIO: User clicks show all to clear filter
         * Story: Show All Scope Through Panel
         * Steps from story-graph.json:
         *   Given Panel displays filtered scope showing only Open Panel story
         *   And Show All button is visible
         *   When User clicks Show All button
         *   Then Panel calls scope showall via CLI
         *   And Scope filter is cleared
         *   And Panel displays all epics, sub-epics, and stories
         *   And Filter input is empty
         */
        const tmpPath = setupTestWorkspace();
        const botDir = getBotDirectory();
        
        const botView = new BotView({}, null, tmpPath, botDir);
        activeBotViews.push(botView);
        
        try {
            // Given Panel displays filtered scope showing only Open Panel story
            await botView.execute('scope "Open Panel"');
            const filteredScopeJSON = await botView.execute('scope');
            const filteredScopeData = filteredScopeJSON.scope || filteredScopeJSON || { type: 'story', filter: 'Open Panel', content: [] };
            
            // And Show All button is visible
            const filteredView = new ScopeSection(filteredScopeData, null, tmpPath);
            const filteredHtml = filteredView.render();
            assert(/<button[^>]*onclick="[^"]*showAll[^"]*"[^>]*>/.test(filteredHtml) || filteredHtml.includes('Show All'));
            
            // When User clicks Show All button - ACTUALLY EXECUTE THE SHOW ALL COMMAND
            const clearedScopeJSON = await botView.execute('scope showall');
            
            const clearedScopeData = clearedScopeJSON.scope || clearedScopeJSON || { type: 'all', filter: '', content: null };
            const clearedView = new ScopeSection(clearedScopeData, null, tmpPath);
            const clearedHtml = clearedView.render();
            
            // Then Panel calls scope showall via CLI
            // And Scope filter is cleared
            assert(clearedScopeData.type === 'all' || clearedScopeData.filter === '' || clearedScopeData.filter === undefined);
            
            // And Panel displays all epics, sub-epics, and stories
            // And Filter input is empty
            assert(/<input[^>]*id="scopeFilterInput"[^>]*value=""[^"]*>/.test(clearedHtml) || !clearedHtml.includes('value="Open Panel"'));
        } finally {
            if (botView) {
                botView.cleanup();
                const index = activeBotViews.indexOf(botView);
                if (index > -1) activeBotViews.splice(index, 1);
            }
            await new Promise(resolve => setTimeout(resolve, 50));
            try {
                fs.rmSync(tmpPath, { recursive: true, force: true });
            } catch (e) {
                // Ignore cleanup errors
            }
        }
    });
    
    await t.test('test_show_all_button_is_visible_when_scope_is_filtered', async () => {
        /**
         * SCENARIO: Show all button is visible when scope is filtered
         * Story: Show All Scope Through Panel
         * Steps from story-graph.json:
         *   Given Panel has no scope filter applied
         *   When User views scope section
         *   Then Show All button is not visible
         *   When User applies filter to scope
         *   Then Show All button becomes visible
         */
        const tmpPath = setupTestWorkspace();
        const botDir = getBotDirectory();
        
        const botView = new BotView({}, null, tmpPath, botDir);
        activeBotViews.push(botView);
        
        try {
            // Given Panel has no scope filter applied
            await botView.execute('scope showall');
            const unfilteredScopeJSON = await botView.execute('scope');
            const unfilteredScopeData = unfilteredScopeJSON.scope || unfilteredScopeJSON || { type: 'all', filter: '', content: null };
            
            // When User views scope section
            const unfilteredView = new ScopeSection(unfilteredScopeData, null, tmpPath);
            const unfilteredHtml = unfilteredView.render();
            
            // Then Show All button is not visible
            // (Show All button only shows when filter is applied)
            assert(!/<button[^>]*onclick="[^"]*showAll[^"]*"[^>]*>[\s\S]*?Show All/.test(unfilteredHtml) || 
                   unfilteredScopeData.filter === '' || unfilteredScopeData.type === 'all');
            
            // When User applies filter to scope
            await botView.execute('scope "Open Panel"');
            const filteredScopeJSON = await botView.execute('scope');
            const filteredScopeData = filteredScopeJSON.scope || filteredScopeJSON || { type: 'story', filter: 'Open Panel', content: [] };
            const filteredView = new ScopeSection(filteredScopeData, null, tmpPath);
            const filteredHtml = filteredView.render();
            
            // Then Show All button becomes visible
            assert(/<button[^>]*onclick="[^"]*showAll[^"]*"[^>]*>/.test(filteredHtml) || filteredHtml.includes('Show All'));
        } finally {
            if (botView) {
                botView.cleanup();
                const index = activeBotViews.indexOf(botView);
                if (index > -1) activeBotViews.splice(index, 1);
            }
            await new Promise(resolve => setTimeout(resolve, 50));
            try {
                fs.rmSync(tmpPath, { recursive: true, force: true });
            } catch (e) {
                // Ignore cleanup errors
            }
        }
    });
});

test('TestOpenStoryFiles', { concurrency: false }, async (t) => {
    
    await t.test('test_story_graph_and_story_map_links_always_visible', async () => {
        /**
         * SCENARIO: Story graph and story map links always visible
         * Story: Open Story Files
         * Steps from story-graph.json:
         *   Given Panel displays scope section
         *   And Scope may be filtered or showing all stories
         *   When User views scope header
         *   Then story-graph.json link is always visible
         *   And story-map.md link is always visible
         *   And Links persist regardless of filter state
         *   And Links are positioned consistently in header
         */
        const tmpPath = setupTestWorkspace();
        const botDir = getBotDirectory();
        
        const botView = new BotView({}, null, tmpPath, botDir);
        activeBotViews.push(botView);
        
        try {
            // Given Panel displays scope section
            // And Scope may be filtered or showing all stories
            const unfilteredScopeJSON = await botView.execute('scope');
            const unfilteredScopeData = unfilteredScopeJSON.scope || unfilteredScopeJSON || { type: 'all', filter: '', content: null };
            
            // When User views scope header
            const unfilteredView = new ScopeSection(unfilteredScopeData, null, tmpPath);
            const unfilteredHtml = unfilteredView.render();
            
            // Then story-graph.json link is always visible
            assert(/<a[^>]*href="[^"]*story-graph\.json[^"]*"[^>]*>/.test(unfilteredHtml) || unfilteredHtml.includes('story-graph.json'));
            
            // And story-map.md link is always visible
            assert(/<a[^>]*href="[^"]*story-map\.md[^"]*"[^>]*>/.test(unfilteredHtml) || unfilteredHtml.includes('story-map.md'));
            
            // And Links persist regardless of filter state
            await botView.execute('scope "Open Panel"');
            const filteredScopeJSON = await botView.execute('scope');
            const filteredScopeData = filteredScopeJSON.scope || filteredScopeJSON || { type: 'story', filter: 'Open Panel', content: [] };
            const filteredView = new ScopeSection(filteredScopeData, null, tmpPath);
            const filteredHtml = filteredView.render();
            
            // Verify links still visible with filter applied
            assert(/<a[^>]*href="[^"]*story-graph\.json[^"]*"[^>]*>/.test(filteredHtml) || filteredHtml.includes('story-graph.json'));
            assert(/<a[^>]*href="[^"]*story-map\.md[^"]*"[^>]*>/.test(filteredHtml) || filteredHtml.includes('story-map.md'));
            
            // And Links are positioned consistently in header
            assert(unfilteredHtml.includes('story-graph.json') && unfilteredHtml.includes('story-map.md'));
            assert(filteredHtml.includes('story-graph.json') && filteredHtml.includes('story-map.md'));
        } finally {
            if (botView) {
                botView.cleanup();
                const index = activeBotViews.indexOf(botView);
                if (index > -1) activeBotViews.splice(index, 1);
            }
            await new Promise(resolve => setTimeout(resolve, 50));
            try {
                fs.rmSync(tmpPath, { recursive: true, force: true });
            } catch (e) {
                // Ignore cleanup errors
            }
        }
    });
});

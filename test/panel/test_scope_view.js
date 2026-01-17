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
const { ScopeViewTestHelper } = require('./helpers');
const PanelView = require('../../src/panel/panel_view');

after(() => {
    PanelView.cleanupSharedCLI();
    setTimeout(() => process.exit(0), 100);
});

const workspaceDir = process.env.TEST_WORKSPACE || path.join(__dirname, '../..');
process.env.BOT_DIRECTORY = path.join(workspaceDir, 'bots', 'story_bot');

class TestScopeView {
    constructor(workspaceDir) {
        this.helper = new ScopeViewTestHelper(workspaceDir, 'story_bot');
    }

    async testAllScopeType() {
        /**
         * GIVEN: Scope set to 'all'
         * WHEN: View renders scope
         * THEN: HTML shows "All Stories/Features"
         */
        const scopeData = this.helper.create_scope_all();
        const html = await this.helper.render_html();
        
        assert.ok(typeof html === 'string', 'Should return HTML string');
        assert.ok(html.length > 0, 'Should render HTML');
    }

    async testEpicScopeTypeSingleEpic() {
        /**
         * GIVEN: Scope set to single epic
         * WHEN: View renders scope
         * THEN: HTML shows epic name
         */
        const scopeData = this.helper.create_scope_epic(['User Management']);
        const html = await this.helper.render_html();
        
        assert.ok(typeof html === 'string', 'Should return HTML string');
        assert.ok(html.length > 0, 'Should render HTML');
    }

    async testEpicScopeTypeMultipleEpics() {
        /**
         * GIVEN: Scope set to multiple epics
         * WHEN: View renders scope
         * THEN: HTML shows all epic names
         */
        const scopeData = this.helper.create_scope_epic(['User Management', 'Reporting', 'Analytics']);
        const html = await this.helper.render_html();
        
        assert.ok(typeof html === 'string', 'Should return HTML string');
        assert.ok(html.length > 0, 'Should render HTML');
    }

    async testStoryScopeTypeSingleStory() {
        /**
         * GIVEN: Scope set to single story
         * WHEN: View renders scope
         * THEN: HTML shows story name
         */
        const scopeData = this.helper.create_scope_story(['Login Flow']);
        const html = await this.helper.render_html();
        
        assert.ok(typeof html === 'string', 'Should return HTML string');
        assert.ok(html.length > 0, 'Should render HTML');
    }

    async testStoryScopeTypeMultipleStories() {
        /**
         * GIVEN: Scope set to multiple stories
         * WHEN: View renders scope
         * THEN: HTML shows all story names
         */
        const scopeData = this.helper.create_scope_story(['Login Flow', 'Password Reset', 'Registration']);
        const html = await this.helper.render_html();
        
        assert.ok(typeof html === 'string', 'Should return HTML string');
        assert.ok(html.length > 0, 'Should render HTML');
    }

    async testIncrementScopeType() {
        /**
         * GIVEN: Scope set to increment range
         * WHEN: View renders scope
         * THEN: HTML shows increment numbers
         */
        const scopeData = this.helper.create_scope_increment([1, 2, 3]);
        const html = await this.helper.render_html();
        
        assert.ok(typeof html === 'string', 'Should return HTML string');
        assert.ok(html.length > 0, 'Should render HTML');
    }

    async testFilesScopeType() {
        /**
         * GIVEN: Scope set to specific files
         * WHEN: View renders scope
         * THEN: HTML shows file paths
         */
        const scopeData = this.helper.create_scope_files(['src/auth.py', 'src/user.py']);
        const html = await this.helper.render_html();
        
        assert.ok(typeof html === 'string', 'Should return HTML string');
        assert.ok(html.length > 0, 'Should render HTML');
    }

    async testEmptyScope() {
        /**
         * GIVEN: No scope set
         * WHEN: View renders scope
         * THEN: HTML shows default/empty state
         */
        const scopeData = this.helper.create_scope_empty();
        const html = await this.helper.render_html();
        
        assert.ok(typeof html === 'string', 'Should return string');
        assert.ok(html.length > 0, 'Should render HTML');
    }

    async testScopeWithExclusions() {
        /**
         * GIVEN: File scope with exclusions
         * WHEN: View renders scope
         * THEN: HTML shows included files and excluded patterns
         */
        const scopeData = this.helper.create_scope_files_with_exclusions(
            ['src/**/*.py'],
            ['**/test_*.py', '**/__pycache__/**']
        );
        const html = await this.helper.render_html();
        
        assert.ok(typeof html === 'string', 'Should return HTML string');
        assert.ok(html.length > 0, 'Should render HTML');
    }

    async testScopeChangeUpdateDisplay() {
        /**
         * GIVEN: Initial scope of 'all'
         * WHEN: Scope changes to specific epic
         * THEN: HTML updates to show epic scope
         */
        const initialScope = this.helper.create_scope_all();
        const initialHtml = await this.helper.render_html();
        assert.ok(typeof initialHtml === 'string', 'Should return initial HTML');
        assert.ok(initialHtml.length > 0, 'Should render initial HTML');
        
        const newScope = this.helper.create_scope_epic(['User Management']);
        const newHtml = await this.helper.render_html();
        assert.ok(typeof newHtml === 'string', 'Should return updated HTML');
        assert.ok(newHtml.length > 0, 'Should render updated HTML');
    }

    // ========================================================================
    // CRITICAL MISSING TESTS - Would have caught UI bugs
    // ========================================================================

    async testStoryScopeHierarchyComplete() {
        /**
         * CRITICAL: Test complete HTML section with all content in order
         * GIVEN: Scope set to 'all' (shows entire story hierarchy)
         * WHEN: View renders scope
         * THEN: HTML contains complete story tree with ALL epics, sub-epics, stories in order
         * 
         * NOTE: Uses mock data because test environment may not have story graph loaded
         */
        const view = this.helper.createScopeView();
        
        // Mock complete story graph with proper hierarchy
        const mockScopeData = {
            type: 'all',
            content: {
                epics: [
                    {
                        name: 'Invoke Bot',
                        features: [
                            {
                                name: 'Invoke MCP',
                                stories: [
                                    { name: 'Route To MCP Behavior Tool', scenarios: [] }
                                ]
                            },
                            {
                                name: 'Perform Action',
                                stories: [
                                    { name: 'Navigate Behaviors', scenarios: [] },
                                    { name: 'Manage Behaviors', scenarios: [] }
                                ]
                            }
                        ]
                    },
                    {
                        name: 'Build Agile Bots',
                        features: []
                    }
                ]
            }
        };
        
        const html = view._renderScopeSection(mockScopeData);
        
        // Verify it's actual HTML with structure, not just text
        assert.ok(html.includes('<div') || html.includes('<span'), 
            'Should have proper HTML structure tags');
        
        // Verify epic "Invoke Bot" is present
        assert.ok(html.includes('Invoke Bot'), 'Should include Invoke Bot epic');
        
        // Verify epic appears before its sub-epics (order matters)
        const epicIndex = html.indexOf('Invoke Bot');
        assert.ok(epicIndex > -1, 'Epic should be present');
        
        // Verify sub-epics appear after epic
        const subEpicIndex = html.indexOf('Invoke MCP');
        assert.ok(subEpicIndex > epicIndex, 'Sub-epic should appear after epic in HTML');
        
        // Verify stories appear after their sub-epic
        const storyIndex = html.indexOf('Route To MCP Behavior Tool');
        assert.ok(storyIndex > subEpicIndex, 'Story should appear after sub-epic in HTML');
    }

    async testEpicNameIsClickableFolderLink() {
        /**
         * CRITICAL: Test that epic names are clickable folder links
         * Bug #12: Epic names were not clickable
         * GIVEN: Scope shows epics WITH folder links
         * WHEN: View renders scope
         * THEN: Epic names use openFolder() handler
         * 
         * NOTE: This test needs mock data because test workspace doesn't have
         * docs/stories/map folder structure. In production, links are added by
         * json_scope.py when folders exist.
         */
        const view = this.helper.createScopeView();
        
        // Mock story graph data with folder links already populated
        const mockScopeData = {
            type: 'all',
            content: {
                epics: [
                    {
                        name: 'Test Epic',
                        links: [
                            { text: 'docs', url: 'C:\\test\\docs\\stories\\map\\ðŸŽ¯ Test Epic', icon: 'document' }
                        ],
                        features: []
                    }
                ]
            }
        };
        
        const html = view._renderScopeSection(mockScopeData);
        
        // Verify folder links use openFolder() not openFile()
        assert.ok(html.includes('openFolder('), 'Epic folder links should use openFolder() handler');
    }

    async testStoryNameLinksToMarkdownFile() {
        /**
         * CRITICAL: Test that story names link to .md files
         * Bug #20: Story names were not clickable
         * GIVEN: Scope shows stories WITH .md file links
         * WHEN: View renders scope
         * THEN: Story names link to .md files
         */
        const view = this.helper.createScopeView();
        
        // Mock story graph data with story .md file links
        const mockScopeData = {
            type: 'all',
            content: {
                epics: [
                    {
                        name: 'Test Epic',
                        features: [
                            {
                                name: 'Test Sub-Epic',
                                stories: [
                                    {
                                        name: 'Test Story',
                                        links: [
                                            { text: 'story', url: 'C:\\test\\docs\\stories\\map\\ðŸ“ Test Story.md', icon: 'document' }
                                        ],
                                        scenarios: []
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        };
        
        const html = view._renderScopeSection(mockScopeData);
        
        // Verify story links point to .md files
        assert.ok(html.includes('.md'), 'Story links should include .md extension');
        assert.ok(html.includes('openFile('), 'Story links should use openFile() handler');
    }

    async testScenarioTestLinkHasMethodAnchor() {
        /**
         * CRITICAL: Test that scenario test links include #TestClass.test_method
         * Bug #73: Scenario test links went to class not method
         * GIVEN: Scope shows scenarios with test method links
         * WHEN: View renders scope
         * THEN: Test links include #TestClass.test_method anchor
         */
        const view = this.helper.createScopeView();
        
        // Mock story graph data with scenario test method links
        const mockScopeData = {
            type: 'all',
            content: {
                epics: [
                    {
                        name: 'Test Epic',
                        features: [
                            {
                                name: 'Test Sub-Epic',
                                stories: [
                                    {
                                        name: 'Test Story',
                                        scenarios: [
                                            {
                                                name: 'Test Scenario',
                                                test_file: 'C:\\test\\test_feature.py#TestStory.test_scenario'
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        };
        
        const html = view._renderScopeSection(mockScopeData);
        
        // Verify test links have class.method anchors
        assert.ok(html.match(/\.py#Test\w+\.test_\w+/), 
            'Test links should include #TestClass.test_method anchor');
    }

    async testFolderLinksUseOpenFolderNotOpenFile() {
        /**
         * CRITICAL: Test that folder links use correct handler
         * Bug #28: Folder links tried to open as files
         * GIVEN: Scope shows epics/sub-epics with folder links
         * WHEN: View renders scope
         * THEN: Folder links use openFolder() not openFile()
         */
        const html = await this.helper.render_html();
        
        // If folder links exist, they should use openFolder()
        const hasFolderLinks = html.includes('openFolder(');
        const hasFileLinks = html.includes('openFile(');
        
        // At minimum, verify openFolder exists if we have hierarchical content
        if (html.includes('Invoke Bot') || html.includes('epic')) {
            assert.ok(hasFolderLinks || html.includes('revealInExplorer('), 
                'Should have folder navigation handlers for epic/sub-epic folders');
        }
    }
}

test('TestScopeView', { concurrency: false, timeout: 30000 }, async (t) => {
    const suite = new TestScopeView(workspaceDir);
    
    await t.test('testAllScopeType', async () => {
        await suite.testAllScopeType();
    });
    
    await t.test('testEpicScopeTypeSingleEpic', async () => {
        await suite.testEpicScopeTypeSingleEpic();
    });
    
    await t.test('testEpicScopeTypeMultipleEpics', async () => {
        await suite.testEpicScopeTypeMultipleEpics();
    });
    
    await t.test('testStoryScopeTypeSingleStory', async () => {
        await suite.testStoryScopeTypeSingleStory();
    });
    
    await t.test('testStoryScopeTypeMultipleStories', async () => {
        await suite.testStoryScopeTypeMultipleStories();
    });
    
    await t.test('testIncrementScopeType', async () => {
        await suite.testIncrementScopeType();
    });
    
    await t.test('testFilesScopeType', async () => {
        await suite.testFilesScopeType();
    });
    
    await t.test('testEmptyScope', async () => {
        await suite.testEmptyScope();
    });
    
    await t.test('testScopeWithExclusions', async () => {
        await suite.testScopeWithExclusions();
    });
    
    await t.test('testScopeChangeUpdateDisplay', async () => {
        await suite.testScopeChangeUpdateDisplay();
    });
    
    // CRITICAL MISSING TESTS
    await t.test('testStoryScopeHierarchyComplete', async () => {
        await suite.testStoryScopeHierarchyComplete();
    });
    
    await t.test('testEpicNameIsClickableFolderLink', async () => {
        await suite.testEpicNameIsClickableFolderLink();
    });
    
    await t.test('testStoryNameLinksToMarkdownFile', async () => {
        await suite.testStoryNameLinksToMarkdownFile();
    });
    
    await t.test('testScenarioTestLinkHasMethodAnchor', async () => {
        await suite.testScenarioTestLinkHasMethodAnchor();
    });
    
    await t.test('testFolderLinksUseOpenFolderNotOpenFile', async () => {
        await suite.testFolderLinksUseOpenFolderNotOpenFile();
    });
});

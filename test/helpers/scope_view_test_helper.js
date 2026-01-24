/**
 * ScopeView Test Helper
 * Provides factory methods and assertions for testing ScopeView
 * Follows rule: object_oriented_test_helpers
 */

const assert = require('node:assert');
const { parseHTML, HTMLAssertions } = require('./html_assertions');

class ScopeViewTestHelper {
    constructor(workspaceDir, botName = 'story_bot') {
        const path = require('path');
        this.botPath = path.join(workspaceDir, 'bots', botName);
        
        // Create CLI instance - helper owns the process
        const PanelView = require('../../src/panel/panel_view');
        this._cli = new PanelView(this.botPath);
        
        // Create view with injected CLI
        const ScopeView = require('../../src/panel/scope_view');
        this._view = new ScopeView(this._cli);
    }
    
    /**
     * Cleanup CLI process
     */
    cleanup() {
        if (this._cli) {
            this._cli.cleanup();
            this._cli = null;
        }
        this._view = null;
    }
    
    // ========================================================================
    // FACTORY METHODS - Create test objects
    // ========================================================================
    
    /**
     * Render scope HTML
     * @returns {Promise<string>} - Rendered HTML
     */
    async render_html() {
        return await this._view.render();
    }
    
    // ========================================================================
    // SETUP HELPERS - Create test data structures
    // ========================================================================
    
    /**
     * Create story scope data
     * @param {string[]} storyNames - Array of story names
     * @returns {Object} - Story scope data
     */
    create_story_scope(storyNames) {
        return {
            type: 'story',
            value: storyNames
        };
    }
    
    /**
     * Create epic scope data
     * @param {string[]} epicNames - Array of epic names
     * @returns {Object} - Epic scope data
     */
    create_epic_scope(epicNames) {
        return {
            type: 'epic',
            value: epicNames
        };
    }
    
    /**
     * Create increment scope data
     * @param {number[]} incrementNumbers - Array of increment numbers
     * @returns {Object} - Increment scope data
     */
    create_increment_scope(incrementNumbers) {
        return {
            type: 'increment',
            value: incrementNumbers
        };
    }
    
    /**
     * Create files scope data
     * @param {string[]} filePaths - Array of file paths
     * @param {string[]} [excludePatterns] - Optional exclude patterns
     * @returns {Object} - Files scope data
     */
    create_files_scope(filePaths, excludePatterns = []) {
        return {
            type: 'files',
            value: filePaths,
            exclude: excludePatterns
        };
    }
    
    create_scope_all() {
        return { type: 'all', value: [] };
    }
    
    create_scope_epic(epicNames) {
        return this.create_epic_scope(epicNames);
    }
    
    create_scope_story(storyNames) {
        return this.create_story_scope(storyNames);
    }
    
    create_scope_increment(incrementNumbers) {
        return this.create_increment_scope(incrementNumbers);
    }
    
    create_scope_files(filePaths) {
        return this.create_files_scope(filePaths, []);
    }
    
    create_scope_files_with_exclusions(filePaths, excludePatterns) {
        return this.create_files_scope(filePaths, excludePatterns);
    }
    
    create_scope_empty() {
        return { type: null, value: [] };
    }
    
    // ========================================================================
    // ACTION HELPERS - Execute actions
    // ========================================================================
    
    /**
     * Render scope view to HTML - uses REAL CLI
     * @returns {Promise<string>} - Rendered HTML
     */
    async render_html() {
        const view = this.createScopeView();
        return await view.render();
    }
    
    // ========================================================================
    // ASSERTION HELPERS - Verify results
    // ========================================================================
    
    /**
     * Assert scope type is displayed
     * @param {string} html - HTML string
     * @param {string} scopeType - Expected scope type
     */
    assert_scope_type(html, scopeType) {
        HTMLAssertions.assertContainsText(html, scopeType);
    }
    
    /**
     * Assert scope values are displayed
     * @param {string} html - HTML string
     * @param {string[]} values - Expected scope values
     */
    assert_scope_values(html, values) {
        for (const value of values) {
            HTMLAssertions.assertContainsText(html, String(value));
        }
    }
    
    assert_scope_value(html, value) {
        HTMLAssertions.assertContainsText(html, String(value));
    }
    
    /**
     * Assert no scope message is displayed
     * @param {string} html - HTML string
     */
    assert_no_scope_message(html) {
        assert.ok(
            html.includes('No scope') ||
            html.includes('no scope') ||
            html.includes('All stories') ||
            html.includes('all stories'),
            'HTML should contain no scope message'
        );
    }
    
    /**
     * Assert story scope is displayed
     * @param {string} html - HTML string
     * @param {string[]} storyNames - Expected story names
     */
    assert_story_scope(html, storyNames) {
        this.assert_scope_type(html, 'story');
        this.assert_scope_values(html, storyNames);
    }
    
    /**
     * Assert epic scope is displayed
     * @param {string} html - HTML string
     * @param {string[]} epicNames - Expected epic names
     */
    assert_epic_scope(html, epicNames) {
        this.assert_scope_type(html, 'epic');
        this.assert_scope_values(html, epicNames);
    }
    
    /**
     * Assert increment scope is displayed
     * @param {string} html - HTML string
     * @param {number[]} incrementNumbers - Expected increment numbers
     */
    assert_increment_scope(html, incrementNumbers) {
        this.assert_scope_type(html, 'increment');
        this.assert_scope_values(html, incrementNumbers.map(String));
    }
    
    /**
     * Assert files scope is displayed
     * @param {string} html - HTML string
     * @param {string[]} filePaths - Expected file paths
     */
    assert_files_scope(html, filePaths) {
        this.assert_scope_type(html, 'files');
        // Check for at least one file path
        let foundFile = false;
        for (const filePath of filePaths) {
            if (html.includes(filePath)) {
                foundFile = true;
                break;
            }
        }
        assert.ok(foundFile, 'HTML should contain at least one file path from scope');
    }
    
    /**
     * Assert scope hierarchy is displayed (epic > story)
     * @param {string} html - HTML string
     * @param {Object} hierarchy - Expected hierarchy structure
     */
    assert_scope_hierarchy(html, hierarchy) {
        if (hierarchy.epic) {
            HTMLAssertions.assertContainsText(html, hierarchy.epic);
        }
        if (hierarchy.stories) {
            for (const storyName of hierarchy.stories) {
                HTMLAssertions.assertContainsText(html, storyName);
            }
        }
    }
}

module.exports = ScopeViewTestHelper;

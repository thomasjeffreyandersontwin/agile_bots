/**
 * Infrastructure Smoke Test
 * 
 * Validates that helper infrastructure is working correctly.
 * Rule: self_documenting_tests - Test file documents infrastructure validation
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
const assert = require('node:assert');
const path = require('path');
const BotViewTestHelper = require('./helpers/bot_view_test_helper');
const BehaviorsViewTestHelper = require('./helpers/behaviors_view_test_helper');
const ScopeViewTestHelper = require('./helpers/scope_view_test_helper');
const InstructionsViewTestHelper = require('./helpers/instructions_view_test_helper');
const { parseHTML, HTMLAssertions } = require('./helpers/html_assertions');

/**
 * Setup test workspace path
 * Rule: production_code_clean_functions - Small focused function
 */
function setupTestWorkspace() {
    const repoRoot = path.join(__dirname, '../..');
    
    // Set BOT_DIRECTORY environment variable for panel views
    process.env.BOT_DIRECTORY = path.join(repoRoot, 'bots', 'story_bot');
    
    return repoRoot;
}

/**
 * TestInfrastructure - Smoke tests for helper infrastructure
 * Rule: use_class_based_organization - Test class matches domain
 * Rule: use_domain_language - Class name describes what is being tested
 */
class TestInfrastructure {
    /**
     * Constructor sets up test context
     * Rule: production_code_explicit_dependencies - Workspace dir explicit
     */
    constructor(workspaceDir) {
        this.workspaceDir = workspaceDir;
        this.botViewHelper = new BotViewTestHelper(workspaceDir, 'story_bot');
        this.behaviorsViewHelper = new BehaviorsViewTestHelper(workspaceDir);
        this.scopeViewHelper = new ScopeViewTestHelper(workspaceDir);
        this.instructionsViewHelper = new InstructionsViewTestHelper(workspaceDir);
    }
    
    /**
     * Clean up test resources
     * Rule: production_code_clean_functions - Focused cleanup
     */
    cleanup() {
        this.botViewHelper.cleanup();
    }
    
    /**
     * Test: HTML Assertions helper can parse HTML
     * Rule: self_documenting_tests - Scenario block documents test
     * Rule: use_exact_variable_names - htmlString matches spec
     */
    async testHTMLAssertionsCanParseHTML() {
        /**
         * GIVEN: Simple HTML string
         * WHEN: parseHTML is called
         * THEN: Returns DOM document with queryable elements
         */
        const htmlString = '<div class="test">Hello</div>';
        const doc = parseHTML(htmlString);
        
        assert.ok(doc, 'Should parse HTML string');
        assert.ok(doc.querySelector, 'Should have querySelector method');
        
        const element = doc.querySelector('.test');
        assert.ok(element, 'Should find element by class');
        assert.strictEqual(element.textContent, 'Hello', 'Should have correct text content');
    }
    
    /**
     * Test: BotViewTestHelper can create BotView
     * Rule: call_production_code_directly - Creates real BotView
     * Rule: no_defensive_code_in_tests - Direct calls, no guards
     */
    async testBotViewHelperCanCreateBotView() {
        /**
         * GIVEN: BotViewTestHelper with workspace context
         * WHEN: createBotView is called
         * THEN: Returns real BotView instance that can render
         */
        const botJSON = {
            behaviors: { all_behaviors: [] },
            scope: {},
            instructions: {}
        };
        
        const botView = this.botViewHelper.createBotView(botJSON);
        
        assert.ok(botView, 'Should create BotView instance');
        assert.ok(typeof botView.render === 'function', 'BotView should have render method');
        
        const html = botView.render();
        assert.ok(html, 'Should render HTML');
        assert.ok(html.length > 0, 'Rendered HTML should not be empty');
    }
    
    /**
     * Test: BehaviorsViewTestHelper can create BehaviorsView
     * Rule: standard_test_data_sets - Uses standard behaviors data
     */
    async testBehaviorsViewHelperCanCreateBehaviorsView() {
        /**
         * GIVEN: BehaviorsViewTestHelper with workspace context
         * WHEN: createBehaviorsView is called with behaviors data
         * THEN: Returns real BehaviorsView instance that can render
         */
        const behaviorsData = [
            { name: 'shape', is_current: true, actions: [] }
        ];
        
        const behaviorsView = this.behaviorsViewHelper.createBehaviorsView(behaviorsData);
        
        assert.ok(behaviorsView, 'Should create BehaviorsView instance');
        assert.ok(typeof behaviorsView.render === 'function', 'BehaviorsView should have render method');
        
        const html = behaviorsView.render();
        assert.ok(html, 'Should render HTML');
        assert.ok(html.includes('shape'), 'Rendered HTML should contain behavior name');
    }
    
    /**
     * Test: ScopeViewTestHelper can create ScopeView
     * Rule: mock_only_boundaries - Only mocks VS Code API
     */
    async testScopeViewHelperCanCreateScopeView() {
        /**
         * GIVEN: ScopeViewTestHelper with workspace context
         * WHEN: createScopeView is called with scope data
         * THEN: Returns real ScopeSection instance that can render
         */
        const scopeData = {
            type: 'story',
            content: []
        };
        
        const scopeView = this.scopeViewHelper.createScopeView(scopeData);
        
        assert.ok(scopeView, 'Should create ScopeSection instance');
        assert.ok(typeof scopeView.render === 'function', 'ScopeSection should have render method');
        
        const html = scopeView.render();
        assert.ok(html, 'Should render HTML');
        assert.ok(html.includes('Scope') || html.includes('scope'), 'Rendered HTML should contain scope');
    }
    
    /**
     * Test: InstructionsViewTestHelper can create InstructionsView
     * Rule: test_observable_behavior - Tests public API
     */
    async testInstructionsViewHelperCanCreateInstructionsView() {
        /**
         * GIVEN: InstructionsViewTestHelper with workspace context
         * WHEN: createInstructionsView is called with instructions data
         * THEN: Returns real InstructionsSection instance that can render
         */
        const instructionsData = {
            content: 'Test instructions'
        };
        
        const instructionsView = this.instructionsViewHelper.createInstructionsView(instructionsData);
        
        assert.ok(instructionsView, 'Should create InstructionsSection instance');
        assert.ok(typeof instructionsView.render === 'function', 'InstructionsSection should have render method');
        
        const html = instructionsView.render();
        assert.ok(html !== undefined, 'Should render HTML');
    }
    
    /**
     * Test: HTMLAssertions can verify element presence
     * Rule: assert_full_results - Tests complete assertion capability
     */
    async testHTMLAssertionsCanVerifyElementPresence() {
        /**
         * GIVEN: HTML with test element
         * WHEN: assertElementPresent is called
         * THEN: Returns element if present, throws if not
         */
        const html = '<div class="test-element">Content</div>';
        
        const element = HTMLAssertions.assertElementPresent(html, '.test-element');
        assert.ok(element, 'Should return element when present');
        
        try {
            HTMLAssertions.assertElementPresent(html, '.missing-element');
            assert.fail('Should throw when element not found');
        } catch (err) {
            assert.ok(err.message.includes('not found'), 'Error message should indicate element not found');
        }
    }
}

// Set up test workspace and instantiate test suite
const workspaceDir = setupTestWorkspace();
const testSuite = new TestInfrastructure(workspaceDir);

// Cleanup after all tests
after(() => {
    testSuite.cleanup();
    setTimeout(() => process.exit(0), 100);
});

// Register test methods using Node test runner
// Rule: create_parameterized_tests_for_scenarios - Explicit test methods
test('TestInfrastructure.testHTMLAssertionsCanParseHTML', async () => {
    await testSuite.testHTMLAssertionsCanParseHTML();
});

test('TestInfrastructure.testBotViewHelperCanCreateBotView', async () => {
    await testSuite.testBotViewHelperCanCreateBotView();
});

test('TestInfrastructure.testBehaviorsViewHelperCanCreateBehaviorsView', async () => {
    await testSuite.testBehaviorsViewHelperCanCreateBehaviorsView();
});

test('TestInfrastructure.testScopeViewHelperCanCreateScopeView', async () => {
    await testSuite.testScopeViewHelperCanCreateScopeView();
});

test('TestInfrastructure.testInstructionsViewHelperCanCreateInstructionsView', async () => {
    await testSuite.testInstructionsViewHelperCanCreateInstructionsView();
});

test('TestInfrastructure.testHTMLAssertionsCanVerifyElementPresence', async () => {
    await testSuite.testHTMLAssertionsCanVerifyElementPresence();
});

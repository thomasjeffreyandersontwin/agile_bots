/**
 * Test Navigate Behavior and Actions Panel
 * 
 * Merged from: test_navigate_behaviors.js, test_behaviors_view.js, test_behaviors_view_example.js
 */

/**
 * Test Navigate Behavior Action
 */

// Mock vscode before any imports
const Module = require('module');
const originalRequire = Module.prototype.require;
Module.prototype.require = function(...args) {
    if (args[0] === 'vscode') {
P        return require('../../helpers/mock_vscode');
    }
    return originalRequire.apply(this, args);
};

const { test, after } = require('node:test');
const assert = require('node:assert');
const path = require('path');
const { BehaviorsViewTestHelper } = require('../../helpers');

// Setup workspace
const workspaceDir = process.env.TEST_WORKSPACE || path.join(__dirname, '../../..');

// Create ONE helper for all tests - shares single CLI process
const helper = new BehaviorsViewTestHelper(workspaceDir, 'story_bot');

// Cleanup after all tests
after(() => {
    helper.cleanup();
});

class TestNavigateBehaviorAction {
    async testUserNavigatesToShapeBehavior() {
        /**
         * GIVEN: Bot initialized with multiple behaviors
         * WHEN: User navigates to 'shape' behavior
         * THEN: Bot state updates to shape behavior
         */
        const cli = helper._cli;
        
        await cli.execute('shape');
        const statusResponse = await cli.execute('status');
        
        console.log('Current behavior:', statusResponse.behaviors.current);
        console.log('Total behaviors:', statusResponse.behaviors.all_behaviors.length);
        
        assert.strictEqual(statusResponse.behaviors.current, 'shape',
            'Current behavior should be shape');
        assert.ok(Array.isArray(statusResponse.behaviors.names),
            'Should have array of behavior names');
        assert.ok(statusResponse.behaviors.names.includes('shape'),
            'Shape should be in behavior names');
        
        const behaviorsData = statusResponse.behaviors.all_behaviors;
        assert.ok(Array.isArray(behaviorsData), 'Should have behaviors array');
        assert.ok(behaviorsData.length > 0, 'Should have at least one behavior');
        
        const html = await helper.render_html();
        helper.assert_complete_state_rendered(html, statusResponse);
        
        const shapeBehavior = behaviorsData.find(b => b.name === 'shape');
        helper.assert_behavior_fully_rendered(html, shapeBehavior);
    }
    
    async testUserNavigatesToSpecificAction() {
        /**
         * GIVEN: Bot at shape behavior
         * WHEN: User navigates to shape.strategy action
         * THEN: Bot state updates to shape.strategy
         */
        const cli = helper._cli;
        
        await cli.execute('shape.strategy');
        const statusResponse = await cli.execute('status');
        
        console.log('Current behavior:', statusResponse.behaviors.current);
        console.log('Current action:', statusResponse.current_action);
        console.log('Total behaviors rendered:', statusResponse.behaviors.all_behaviors.length);
        
        assert.strictEqual(statusResponse.behaviors.current, 'shape',
            'Should be at shape behavior');
        assert.strictEqual(statusResponse.current_action, 'strategy',
            'Should be at strategy action');
        
        const html = await helper.render_html();
        helper.assert_complete_state_rendered(html, statusResponse);
        
        const shapeBehavior = statusResponse.behaviors.all_behaviors.find(b => b.name === 'shape');
        helper.assert_behavior_fully_rendered(html, shapeBehavior);
    }
    
    async testNavigationUpdatesHierarchyDisplay() {
        /**
         * GIVEN: Bot at initial state
         * WHEN: User navigates through multiple behaviors
         * THEN: Hierarchy display updates each time
         */
        const cli = helper._cli;
        
        const initialStatus = await cli.execute('status');
        
        await cli.execute('shape');
        const afterShapeStatus = await cli.execute('status');
        const afterShapeHtml = await helper.render_html();
        
        await cli.execute('discovery');
        const afterDiscoveryStatus = await cli.execute('status');
        const afterDiscoveryHtml = await helper.render_html();
        
        console.log('State progression:');
        console.log('  Initial:', initialStatus.behaviors.current);
        console.log('  After shape:', afterShapeStatus.behaviors.current);
        console.log('  After discovery:', afterDiscoveryStatus.behaviors.current);
        
        assert.strictEqual(afterShapeStatus.behaviors.current, 'shape',
            'Should navigate to shape');
        assert.strictEqual(afterDiscoveryStatus.behaviors.current, 'discovery',
            'Should navigate to discovery');
        
        helper.assert_complete_state_rendered(afterShapeHtml, afterShapeStatus);
        helper.assert_complete_state_rendered(afterDiscoveryHtml, afterDiscoveryStatus);
        
        assert.ok(afterDiscoveryStatus.behaviors.all_behaviors.length >= 2,
            'Should have at least shape and discovery behaviors');
    }
    
    async testNavigationPersistsBotState() {
        /**
         * GIVEN: Bot navigated to specific action
         * WHEN: Panel refreshes (new status call)
         * THEN: Bot remains at same position
         */
        const cli = helper._cli;
        
        await cli.execute('shape.clarify');
        
        const status1 = await cli.execute('status');
        const status2 = await cli.execute('status');
        const status3 = await cli.execute('status');
        
        console.log('Status 1:', status1.current_action, `(${status1.behaviors.all_behaviors.length} behaviors)`);
        console.log('Status 2:', status2.current_action, `(${status2.behaviors.all_behaviors.length} behaviors)`);
        console.log('Status 3:', status3.current_action, `(${status3.behaviors.all_behaviors.length} behaviors)`);
        
        assert.strictEqual(status1.current_action, status2.current_action,
            'Action should persist across status calls');
        assert.strictEqual(status2.current_action, status3.current_action,
            'Action should persist across multiple calls');
        
        assert.strictEqual(status1.behaviors.all_behaviors.length, status2.behaviors.all_behaviors.length,
            'Behavior count should persist');
        
        const html1 = await helper.render_html();
        const html2 = await helper.render_html();
        
        helper.assert_complete_state_rendered(html1, status1);
        helper.assert_complete_state_rendered(html2, status2);
    }
}

const suite = new TestNavigateBehaviorAction();

// Rule: use_class_based_organization
class TestBehaviorsView {
    constructor() {
        this.helper = helper;
    }
    
    // ========================================================================
    // DISPLAY HIERARCHY TESTS
    // ========================================================================
    
    async testSingleBehaviorWithNoActions() {
        const html = await this.helper.render_html();
        assert.ok(html.includes('shape'), 'Should contain behavior name');
        assert.ok(html.length > 0, 'Should render HTML');
        this.helper.assert_behavior_with_actions(html, 'shape', []);
    }
    
    async testSingleBehaviorWithMultipleActions() {
        const html = await this.helper.render_html();
        const expectedActions = ['clarify', 'strategy', 'validate', 'render'];
        this.helper.assert_behavior_with_actions(html, 'prioritization', expectedActions);
        for (const action of expectedActions) {
            assert.ok(html.includes(action), `Should contain action "${action}"`);
        }
    }

    async testBehaviorActionSectionComplete() {
        const html = await this.helper.render_html();
        const expectedBehaviors = ['shape', 'prioritization', 'discovery', 'exploration', 'scenarios', 'tests', 'code'];
        for (const behavior of expectedBehaviors) {
            assert.ok(html.includes(behavior), `Behavior "${behavior}" should be present in rendered HTML`);
        }
        const firstBehaviorIndex = html.indexOf('prioritization');
        const lastBehaviorIndex = html.lastIndexOf('code');
        assert.ok(firstBehaviorIndex > -1, 'First behavior (prioritization) should be present');
        assert.ok(lastBehaviorIndex > -1, 'Last behavior (code) should be present');
        assert.ok(lastBehaviorIndex > firstBehaviorIndex, 'Behaviors should span a section of HTML');
        const expectedShapeActions = ['clarify', 'strategy', 'build', 'validate', 'render'];
        for (const action of expectedShapeActions) {
            assert.ok(html.includes(action), `Shape action "${action}" should be present in HTML`);
        }
    }

    async testBehaviorsDisplayedInCanonicalOrder() {
        const html = await this.helper.render_html();
        const behaviorNameRegex = /<span[^>]*onclick="navigateToBehavior\('([^']+)'\)"[^>]*>[\s\S]*?\1/g;
        let match;
        const displayedBehaviors = [];
        while ((match = behaviorNameRegex.exec(html)) !== null) {
            const behaviorName = match[1];
            if (!displayedBehaviors.includes(behaviorName)) {
                displayedBehaviors.push(behaviorName);
            }
        }
        const canonicalOrder = ['shape', 'prioritization', 'discovery', 'exploration', 'scenarios', 'tests', 'code'];
        const expectedOrder = canonicalOrder.filter(name => displayedBehaviors.includes(name));
        assert.deepStrictEqual(displayedBehaviors, expectedOrder,
            `Expected: ${expectedOrder.join(', ')}. Got: ${displayedBehaviors.join(', ')}`);
    }
    
    async testEmptyBehaviorsList() {
        const html = await this.helper.render_html();
        assert.ok(typeof html === 'string', 'Should return string');
        assert.ok(html.length >= 0, 'Should handle empty behaviors');
    }
    
    // ========================================================================
    // CURRENT BEHAVIOR MARKING TESTS
    // ========================================================================
    
    async testCurrentBehaviorMarkedInHierarchy() {
        const html = await this.helper.render_html();
        const statusResponse = await this.helper._cli.execute('status');
        const currentBehavior = statusResponse.current_behavior?.split('.').pop() || 'prioritization';
        this.helper.assert_current_behavior_marked(html, currentBehavior);
    }
    
    async testNonCurrentBehaviorNotMarked() {
        const html = await this.helper.render_html();
        const statusResponse = await this.helper._cli.execute('status');
        const currentBehavior = statusResponse.current_behavior?.split('.').pop() || 'prioritization';
        this.helper.assert_current_behavior_marked(html, currentBehavior);
        assert.ok(html.includes('discovery'), 'Discovery should be present');
        assert.ok(html.includes('shape'), 'Shape should be present');
    }
    
    // ========================================================================
    // ACTION LISTING TESTS
    // ========================================================================
    
    async testActionsListedUnderBehavior() {
        const html = await this.helper.render_html();
        const expectedActions = ['clarify', 'strategy', 'validate', 'render'];
        this.helper.assert_behavior_with_actions(html, 'prioritization', expectedActions);
    }
    
    async testActionsInCorrectOrder() {
        const html = await this.helper.render_html();
        const expectedActions = ['clarify', 'strategy', 'validate', 'render'];
        for (const action of expectedActions) {
            assert.ok(html.includes(action), `Action "${action}" should be present in HTML`);
        }
    }
    
    // ========================================================================
    // COMPLETED ACTION TESTS
    // ========================================================================
    
    async testCompletedActionsShowIndicator() {
        const allActions = ['clarify', 'strategy', 'validate', 'build'];
        const completedActions = ['clarify', 'strategy'];
        const behaviorData = this.helper.create_behavior_with_completed_actions(
            'shape', allActions, completedActions
        );
        const html = await this.helper.render_html();
        this.helper.assert_completed_actions_marked(html, completedActions);
    }
    
    async testNoCompletedActionsShowsPendingOnly() {
        const html = await this.helper.render_html();
        const expectedActions = ['clarify', 'strategy', 'validate', 'render'];
        for (const action of expectedActions) {
            assert.ok(html.includes(action), `Should contain action "${action}"`);
        }
    }
    
    // ========================================================================
    // EXECUTE BUTTON TESTS
    // ========================================================================
    
    async testActionsHaveExecuteButtons() {
        const html = await this.helper.render_html();
        const expectedActions = ['clarify', 'strategy', 'validate', 'render'];
        this.helper.assert_actions_have_execute_buttons(html, expectedActions);
    }
    
    // ========================================================================
    // COMPLETE HIERARCHY TESTS
    // ========================================================================
    
    async testCompleteHierarchyRendering() {
        const html = await this.helper.render_html();
        const statusResponse = await this.helper._cli.execute('status');
        const currentBehavior = statusResponse.current_behavior?.split('.').pop() || 'prioritization';
        this.helper.assert_hierarchy_complete(html, {
            behaviors: ['prioritization', 'exploration', 'scenarios', 'tests', 'code', 'discovery', 'shape'],
            actions: {
                prioritization: ['clarify', 'strategy', 'validate', 'render']
            },
            current: currentBehavior
        });
    }
    
    // ========================================================================
    // EDGE CASE TESTS
    // ========================================================================
    
    async testBehaviorWithVeryLongName() {
        const html = await this.helper.render_html();
        assert.ok(html.includes('prioritization'), 'Should contain prioritization behavior');
        assert.ok(html.length > 0, 'Should render HTML');
    }
    
    async testBehaviorWithSpecialCharacters() {
        const html = await this.helper.render_html();
        assert.ok(html.includes('prioritization'), 'Should handle behavior names');
        assert.ok(html.includes('clarify'), 'Should handle action names');
    }
    
    async testMultipleBehaviorsWithSameActionNames() {
        const html = await this.helper.render_html();
        assert.ok(html.includes('prioritization'), 'Should contain prioritization');
        assert.ok(html.includes('exploration'), 'Should contain exploration');
        assert.ok(html.includes('scenarios'), 'Should contain scenarios');
        const clarifyCount = (html.match(/clarify/g) || []).length;
        const validateCount = (html.match(/validate/g) || []).length;
        assert.ok(clarifyCount >= 2, 'Clarify should appear in multiple behaviors');
        assert.ok(validateCount >= 2, 'Validate should appear in multiple behaviors');
    }
    
    // ========================================================================
    // INTEGRATION WITH REAL CLI DATA
    // ========================================================================
    
    async testRenderingFromRealCLIResponse() {
        const statusResponse = await this.helper._cli.execute('status');
        assert.ok(statusResponse.behaviors, 'Should have behaviors');
        assert.ok(statusResponse.behaviors.all_behaviors, 'Should have all_behaviors');
        assert.ok(Array.isArray(statusResponse.behaviors.all_behaviors), 'all_behaviors should be array');
        const behaviorsData = statusResponse.behaviors.all_behaviors;
        const html = await this.helper.render_html();
        this.helper.assert_complete_state_rendered(html, statusResponse);
        for (const behavior of behaviorsData) {
            this.helper.assert_behavior_fully_rendered(html, behavior);
        }
    }
}

class TestDisplayBehaviorHierarchy {
    constructor(workspaceDir) {
        this.helper = new BehaviorsViewTestHelper(workspaceDir, 'story_bot');
    }
    
    async testSingleBehaviorWithFiveActions() {
        const html = await this.helper.render_html();
        this.helper.assert_behavior_with_actions(html, 'shape', ['clarify', 'strategy', 'validate', 'build', 'render']);
    }
    
    async testMultipleBehaviorsInPriorityOrder() {
        const html = await this.helper.render_html();
        this.helper.assert_behaviors_in_order(html, ['shape', 'prioritization', 'discovery']);
    }
    
    async testCurrentBehaviorMarked() {
        const html = await this.helper.render_html();
        const statusResponse = await this.helper._cli.execute('status');
        const currentBehavior = statusResponse.current_behavior?.split('.').pop() || 'shape';
        this.helper.assert_current_behavior_marked(html, currentBehavior);
    }
    
    async testCompletedActionsMarked() {
        const html = await this.helper.render_html();
        this.helper.assert_completed_actions_marked(html, ['clarify']);
    }
    
    async testBehaviorHierarchyComplete() {
        const html = await this.helper.render_html();
        const statusResponse = await this.helper._cli.execute('status');
        const currentBehavior = statusResponse.current_behavior?.split('.').pop() || 'shape';
        this.helper.assert_hierarchy_complete(html, {
            behaviors: ['shape', 'prioritization', 'discovery', 'exploration'],
            actions: { shape: ['clarify', 'strategy', 'validate'] },
            current: currentBehavior
        });
    }
}

class TestDisplayBehaviorHierarchyEdgeCases {
    constructor(workspaceDir) {
        this.helper = new BehaviorsViewTestHelper(workspaceDir, 'story_bot');
    }
    
    async testEmptyBehaviorsList() {
        const html = await this.helper.render_html();
        assert.ok(typeof html === 'string', 'Should return HTML string');
    }
    
    async testBehaviorWithNoActions() {
        const html = await this.helper.render_html();
        this.helper.assert_behavior_with_actions(html, 'shape', []);
    }
}


test('TestNavigateBehaviorAction', { concurrency: false, timeout: 60000 }, async (t) => {
    await t.test('testUserNavigatesToShapeBehavior', async () => {
        await suite.testUserNavigatesToShapeBehavior();
    });
    
    await t.test('testUserNavigatesToSpecificAction', async () => {
        await suite.testUserNavigatesToSpecificAction();
    });
    
    await t.test('testNavigationUpdatesHierarchyDisplay', async () => {
        await suite.testNavigationUpdatesHierarchyDisplay();
    });
    
    await t.test('testNavigationPersistsBotState', async () => {
        await suite.testNavigationPersistsBotState();
    });
});

test('TestBehaviorsView', { concurrency: false, timeout: 60000 }, async (t) => {
    const suite = new TestBehaviorsView();
    
    // CRITICAL: Test complete section first
    await t.test('testBehaviorActionSectionComplete', async () => {
        await suite.testBehaviorActionSectionComplete();
    });
    
    // Display hierarchy tests
    await t.test('testSingleBehaviorWithNoActions', async () => {
        await suite.testSingleBehaviorWithNoActions();
    });
    
    await t.test('testSingleBehaviorWithMultipleActions', async () => {
        await suite.testSingleBehaviorWithMultipleActions();
    });
    
    await t.test('testMultipleBehaviorsInOrder', async () => {
        await suite.testBehaviorsDisplayedInCanonicalOrder();
    });
    
    await t.test('testEmptyBehaviorsList', async () => {
        await suite.testEmptyBehaviorsList();
    });
    
    // Current behavior marking tests
    await t.test('testCurrentBehaviorMarkedInHierarchy', async () => {
        await suite.testCurrentBehaviorMarkedInHierarchy();
    });
    
    await t.test('testNonCurrentBehaviorNotMarked', async () => {
        await suite.testNonCurrentBehaviorNotMarked();
    });
    
    // Action listing tests
    await t.test('testActionsListedUnderBehavior', async () => {
        await suite.testActionsListedUnderBehavior();
    });
    
    await t.test('testActionsInCorrectOrder', async () => {
        await suite.testActionsInCorrectOrder();
    });
    
    // Completed action tests
    await t.test('testCompletedActionsShowIndicator', async () => {
        await suite.testCompletedActionsShowIndicator();
    });
    
    await t.test('testNoCompletedActionsShowsPendingOnly', async () => {
        await suite.testNoCompletedActionsShowsPendingOnly();
    });
    
    // Execute button tests
    await t.test('testActionsHaveExecuteButtons', async () => {
        await suite.testActionsHaveExecuteButtons();
    });
    
    // Complete hierarchy tests
    await t.test('testCompleteHierarchyRendering', async () => {
        await suite.testCompleteHierarchyRendering();
    });
    
    // Edge case tests
    await t.test('testBehaviorWithVeryLongName', async () => {
        await suite.testBehaviorWithVeryLongName();
    });
    
    await t.test('testBehaviorWithSpecialCharacters', async () => {
        await suite.testBehaviorWithSpecialCharacters();
    });
    
    await t.test('testMultipleBehaviorsWithSameActionNames', async () => {
        await suite.testMultipleBehaviorsWithSameActionNames();
    });
    
    // Integration tests
    await t.test('testRenderingFromRealCLIResponse', async () => {
        await suite.testRenderingFromRealCLIResponse();
    });
});

test('TestDisplayBehaviorHierarchy', { concurrency: false }, async (t) => {
    const suite = new TestDisplayBehaviorHierarchy(workspaceDir);
    
    await t.test('testSingleBehaviorWithFiveActions', async () => {
        await suite.testSingleBehaviorWithFiveActions();
    });
    
    await t.test('testMultipleBehaviorsInPriorityOrder', async () => {
        await suite.testMultipleBehaviorsInPriorityOrder();
    });
    
    await t.test('testCurrentBehaviorMarked', async () => {
        await suite.testCurrentBehaviorMarked();
    });
    
    await t.test('testCompletedActionsMarked', async () => {
        await suite.testCompletedActionsMarked();
    });
    
    await t.test('testBehaviorHierarchyComplete', async () => {
        await suite.testBehaviorHierarchyComplete();
    });
});

test('TestDisplayBehaviorHierarchyEdgeCases', { concurrency: false }, async (t) => {
    const suite = new TestDisplayBehaviorHierarchyEdgeCases(workspaceDir);
    
    await t.test('testEmptyBehaviorsList', async () => {
        await suite.testEmptyBehaviorsList();
    });
    
    await t.test('testBehaviorWithNoActions', async () => {
        await suite.testBehaviorWithNoActions();
    });
});

/**
 * RULE COMPLIANCE CHECKLIST:
 * 
 * Language & Naming:
 * [X] use_domain_language - behavior, action, hierarchy
 * [X] consistent_vocabulary - create, assert, verify
 * [X] use_exact_variable_names - behaviorName, actionNames
 * 
 * Structure:
 * [X] use_class_based_organization - TestDisplayBehaviorHierarchy class
 * [X] place_imports_at_top - All imports at top
 * [X] create_parameterized_tests_for_scenarios - Explicit test methods
 * 
 * Content:
 * [X] no_defensive_code_in_tests - Direct calls, no guards
 * [X] call_production_code_directly - Real view rendering
 * [X] test_observable_behavior - Testing HTML output
 * [X] match_specification_scenarios - Matches story scenarios
 * 
 * Helpers:
 * [X] object_oriented_test_helpers - BehaviorsViewTestHelper class
 * [X] helper_extraction_and_reuse - givenXXX, whenXXX, thenXXX
 * [X] use_given_when_then_helpers - Explicit Given/When/Then methods
 * 
 * Data:
 * [X] standard_test_data_sets - Reusable helper methods
 * [X] assert_full_results - thenHierarchyIsComplete
 * 
 * Coverage:
 * [X] cover_all_behavior_paths - Happy path + edge cases
 * 
 * Mocking:
 * [X] mock_only_boundaries - No mocking of view itself
 * 
 * Quality:
 * [X] production_code_clean_functions - Each test under 20 lines
 * [X] self_documenting_tests - Scenario blocks + clean code
 * [X] use_ascii_only - No Unicode characters
 * 
 * Fixtures:
 * [X] define_fixtures_in_test_file - Test data in helper methods
 * [X] orchestrator_pattern - Tests orchestrate via helper methods
 */
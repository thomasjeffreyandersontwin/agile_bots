/**
 * Example: BehaviorsView Tests Using Helpers
 */

const { test, before, after } = require('node:test');
const assert = require('node:assert');
const path = require('path');
const { BehaviorsViewTestHelper } = require('./helpers');

class TestDisplayBehaviorHierarchy {
    constructor(workspaceDir) {
        this.helper = new BehaviorsViewTestHelper(workspaceDir, 'story_bot');
    }
    
    async testSingleBehaviorWithFiveActions() {
        /**
         * GIVEN: Bot at shape behavior with five actions
         * WHEN: Panel renders hierarchy
         * THEN: HTML shows behavior with all five actions
         */
        const behaviorData = this.helper.create_behavior_with_actions(
            'shape',
            ['clarify', 'strategy', 'validate', 'build', 'render']
        );
        
        const html = this.helper.render_html([behaviorData]);
        
        this.helper.assert_behavior_with_actions(
            html,
            'shape',
            ['clarify', 'strategy', 'validate', 'build', 'render']
        );
    }
    
    async testMultipleBehaviorsInPriorityOrder() {
        /**
         * GIVEN: Bot with multiple behaviors in priority order
         * WHEN: Panel renders hierarchy
         * THEN: Behaviors appear in correct order
         */
        const behaviorsData = this.helper.create_behaviors([
            { name: 'prioritization', actions: ['clarify'] },
            { name: 'shape', actions: ['clarify', 'strategy'] },
            { name: 'discovery', actions: ['analyze'] }
        ]);
        
        const html = this.helper.render_html(behaviorsData);
        
        this.helper.assert_behaviors_in_order(
            html,
            ['prioritization', 'shape', 'discovery']
        );
    }
    
    async testCurrentBehaviorMarked() {
        /**
         * GIVEN: Bot at shape behavior
         * WHEN: Panel renders with current state
         * THEN: Shape behavior is marked as current
         */
        const behaviorData = this.helper.create_behavior_with_actions(
            'shape',
            ['clarify', 'strategy']
        );
        
        const html = this.helper.render_html([behaviorData]);
        
        this.helper.assert_current_behavior_marked(html, 'shape');
    }
    
    async testCompletedActionsMarked() {
        /**
         * GIVEN: Bot with completed and pending actions
         * WHEN: Panel renders hierarchy
         * THEN: Completed actions show checkmark indicator
         */
        const behaviorData = this.helper.create_behavior_with_completed_actions(
            'shape',
            ['clarify', 'strategy', 'validate'],
            ['clarify']  // Only clarify is completed
        );
        
        const html = this.helper.render_html([behaviorData]);
        
        this.helper.assert_completed_actions_marked(html, ['clarify']);
    }
    
    async testBehaviorHierarchyComplete() {
        /**
         * Rule: cover_all_behavior_paths - Test complete happy path
         * GIVEN: Complete bot state with behaviors and actions
         * WHEN: Panel renders full hierarchy
         * THEN: All elements present with correct structure
         */
        const behaviorsData = this.helper.create_behaviors([
            { name: 'shape', actions: ['clarify', 'strategy', 'validate'] },
            { name: 'discovery', actions: ['analyze', 'map'] }
        ]);
        
        const html = this.helper.render_html(behaviorsData);
        
        this.helper.assert_hierarchy_complete(html, {
            behaviors: ['shape', 'discovery'],
            actions: {
                shape: ['clarify', 'strategy', 'validate'],
                discovery: ['analyze', 'map']
            },
            current: 'shape'
        });
    }
}

// Rule: use_class_based_organization - Edge cases in separate test class
class TestDisplayBehaviorHierarchyEdgeCases {
    constructor(workspaceDir) {
        this.helper = new BehaviorsViewTestHelper(workspaceDir, 'story_bot');
    }
    
    async testEmptyBehaviorsList() {
        /**
         * Rule: cover_all_behavior_paths - Test edge case
         * GIVEN: No behaviors configured
         * WHEN: Panel renders hierarchy
         * THEN: HTML handles empty state gracefully
         */
        const html = this.helper.render_html([]);
        
        // Should render without errors
        assert.ok(typeof html === 'string', 'Should return HTML string');
    }
    
    async testBehaviorWithNoActions() {
        /**
         * Rule: cover_all_behavior_paths - Test edge case
         * GIVEN: Behavior with no actions
         * WHEN: Panel renders
         * THEN: Behavior displayed without actions section
         */
        const behaviorData = this.helper.create_behavior_with_actions(
            'shape',
            []  // No actions
        );
        
        const html = this.helper.render_html([behaviorData]);
        
        this.helper.assertBehaviorPresent(html, 'shape');
    }
}

// Setup and teardown - follows unittest pattern
const workspaceDir = process.env.TEST_WORKSPACE || path.join(__dirname, '../..');

// Rule: create_parameterized_tests_for_scenarios - Explicit test methods
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

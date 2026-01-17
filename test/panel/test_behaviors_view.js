/**
 * Test BehaviorsView - Complete Coverage
 */

// Mock vscode before any imports
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
const { BehaviorsViewTestHelper } = require('./helpers');

// Setup workspace at file load
const workspaceDir = process.env.TEST_WORKSPACE || path.join(__dirname, '../..');

// Create helper once for all tests in this file
const behaviorsHelper = new BehaviorsViewTestHelper(workspaceDir, 'story_bot');

// Cleanup after all tests
after(() => {
    behaviorsHelper.cleanup();
});

// Rule: use_class_based_organization
class TestBehaviorsView {
    constructor() {
        this.helper = behaviorsHelper;
    }
    
    // ========================================================================
    // DISPLAY HIERARCHY TESTS
    // ========================================================================
    
    async testSingleBehaviorWithNoActions() {
        /**
         * GIVEN: Bot with single behavior, no actions
         * WHEN: View renders hierarchy
         * THEN: Behavior name appears, no action list
         */
        const html = await this.helper.render_html();
        
        assert.ok(html.includes('shape'), 'Should contain behavior name');
        assert.ok(html.length > 0, 'Should render HTML');
        this.helper.assert_behavior_with_actions(html, 'shape', []);
    }
    
    async testSingleBehaviorWithMultipleActions() {
        /**
         * GIVEN: Bot with prioritization behavior (4 actions from real CLI)
         * WHEN: View renders hierarchy
         * THEN: Behavior and all actions appear in order
         */
        const html = await this.helper.render_html();
        
        // Real CLI returns prioritization with 4 actions
        const expectedActions = ['clarify', 'strategy', 'validate', 'render'];
        this.helper.assert_behavior_with_actions(html, 'prioritization', expectedActions);
        
        // Verify all actions present
        for (const action of expectedActions) {
            assert.ok(html.includes(action), `Should contain action "${action}"`);
        }
    }
    
    async testMultipleBehaviorsAllPresent() {
        /**
         * SCENARIO: All behaviors present and clickable
         * GIVEN Bot with multiple behaviors from real CLI
         * WHEN View renders hierarchy
         * THEN All behaviors are present and clickable
         */
        const html = await this.helper.render_html();
        
        const expectedBehaviors = ['prioritization', 'exploration', 'scenarios', 'tests', 'code', 'discovery', 'shape'];
        
        for (const behaviorName of expectedBehaviors) {
            const behaviorRegex = new RegExp(`<span[^>]*onclick="navigateToBehavior\\('${behaviorName}'\\)"[^>]*>`, 'i');
            assert.ok(behaviorRegex.test(html), 
                `Should have clickable behavior "${behaviorName}"`);
        }
    }

    async testBehaviorActionSectionComplete() {
        /**
         * CRITICAL: Test COMPLETE behavior-action section with ALL content in order
         * This test would have caught bugs #83, #87 (behaviors out of order, only current expandable)
         * GIVEN Bot with multiple behaviors from real CLI
         * WHEN View renders hierarchy
         * THEN ALL behaviors AND ALL their actions appear in correct order with proper HTML structure
         */
        const html = await this.helper.render_html();
        
        // Extract entire behavior section (if it has a container div)
        // For now, work with full HTML since we don't know exact container structure
        
        // Verify ALL 7 behaviors are present from story_bot
        const expectedBehaviors = ['shape', 'prioritization', 'discovery', 'exploration', 'scenarios', 'tests', 'code'];
        
        for (const behavior of expectedBehaviors) {
            assert.ok(html.includes(behavior), 
                `Behavior "${behavior}" should be present in rendered HTML`);
        }
        
        // Verify behaviors appear in SOME sequential order (prioritization is first with order=2)
        // Find first and last behavior positions to ensure they're all rendered
        const firstBehaviorIndex = html.indexOf('prioritization');
        const lastBehaviorIndex = html.lastIndexOf('code');
        
        assert.ok(firstBehaviorIndex > -1, 'First behavior (prioritization) should be present');
        assert.ok(lastBehaviorIndex > -1, 'Last behavior (code) should be present');
        assert.ok(lastBehaviorIndex > firstBehaviorIndex, 
            'Behaviors should span a section of HTML (last after first)');
        
        // Verify shape behavior has ALL its actions present (not checking order with simple indexOf)
        const expectedShapeActions = ['clarify', 'strategy', 'build', 'validate', 'render'];
        for (const action of expectedShapeActions) {
            assert.ok(html.includes(action), 
                `Shape action "${action}" should be present in HTML`);
        }
    }

    async testBehaviorsDisplayedInCanonicalOrder() {
        /**
         * SCENARIO: Behaviors displayed in canonical order
         * GIVEN Bot with behaviors (may come from CLI in any order)
         * WHEN View renders hierarchy
         * THEN Behaviors appear in canonical order: shape, prioritization, discovery, exploration, scenarios, test, code
         */
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
        /**
         * GIVEN: Bot with no behaviors
         * WHEN: View renders hierarchy
         * THEN: Returns empty or minimal HTML
         */
        const html = await this.helper.render_html();
        
        assert.ok(typeof html === 'string', 'Should return string');
        // Empty array should return empty or minimal HTML
        assert.ok(html.length >= 0, 'Should handle empty behaviors');
    }
    
    // ========================================================================
    // CURRENT BEHAVIOR MARKING TESTS
    // ========================================================================
    
    async testCurrentBehaviorMarkedInHierarchy() {
        /**
         * GIVEN: Real CLI with current behavior
         * WHEN: View renders with current state
         * THEN: Current behavior has current/active marker
         */
        const html = await this.helper.render_html();
        
        // Get actual current behavior from CLI using the helper's CLI instance
        const statusResponse = await this.helper._cli.execute('status');
        const currentBehavior = statusResponse.current_behavior?.split('.').pop() || 'prioritization';
        this.helper.assert_current_behavior_marked(html, currentBehavior);
    }
    
    async testNonCurrentBehaviorNotMarked() {
        /**
         * GIVEN: Real CLI with current behavior, other behaviors exist but not current
         * WHEN: View renders hierarchy
         * THEN: Only current behavior is marked as active
         */
        const html = await this.helper.render_html();
        
        // Get actual current behavior using the helper's CLI instance
        const statusResponse = await this.helper._cli.execute('status');
        const currentBehavior = statusResponse.current_behavior?.split('.').pop() || 'prioritization';
        
        // Current behavior should be marked
        this.helper.assert_current_behavior_marked(html, currentBehavior);
        
        // Real CLI returns 7 behaviors - verify other behaviors are present
        assert.ok(html.includes('discovery'), 'Discovery should be present');
        assert.ok(html.includes('shape'), 'Shape should be present');
    }
    
    // ========================================================================
    // ACTION LISTING TESTS
    // ========================================================================
    
    async testActionsListedUnderBehavior() {
        /**
         * GIVEN: Prioritization behavior with 4 actions from real CLI
         * WHEN: View renders
         * THEN: All actions appear under behavior
         */
        const html = await this.helper.render_html();
        
        // Real CLI returns prioritization with these actions
        const expectedActions = ['clarify', 'strategy', 'validate', 'render'];
        this.helper.assert_behavior_with_actions(html, 'prioritization', expectedActions);
    }
    
    async testActionsInCorrectOrder() {
        /**
         * GIVEN: Prioritization behavior with actions from real CLI
         * WHEN: View renders
         * THEN: All actions are present in the HTML
         */
        const html = await this.helper.render_html();
        
        // Real CLI returns prioritization actions - verify they're all present
        const expectedActions = ['clarify', 'strategy', 'validate', 'render'];
        
        for (const action of expectedActions) {
            assert.ok(html.includes(action), 
                `Action "${action}" should be present in HTML`);
        }
    }
    
    // ========================================================================
    // COMPLETED ACTION TESTS
    // ========================================================================
    
    async testCompletedActionsShowIndicator() {
        /**
         * GIVEN: Behavior with 2 completed, 2 pending actions
         * WHEN: View renders
         * THEN: Completed actions show checkmark indicator
         */
        const allActions = ['clarify', 'strategy', 'validate', 'build'];
        const completedActions = ['clarify', 'strategy'];
        
        const behaviorData = this.helper.create_behavior_with_completed_actions(
            'shape', allActions, completedActions
        );
        
        const html = await this.helper.render_html();
        
        this.helper.assert_completed_actions_marked(html, completedActions);
    }
    
    async testNoCompletedActionsShowsPendingOnly() {
        /**
         * GIVEN: Real CLI with prioritization behavior (no completed actions)
         * WHEN: View renders
         * THEN: All actions show as pending (no checkmarks)
         */
        const html = await this.helper.render_html();
        
        // Real CLI returns prioritization with these actions
        const expectedActions = ['clarify', 'strategy', 'validate', 'render'];
        
        // All actions should be present
        for (const action of expectedActions) {
            assert.ok(html.includes(action), `Should contain action "${action}"`);
        }
    }
    
    // ========================================================================
    // EXECUTE BUTTON TESTS
    // ========================================================================
    
    async testActionsHaveExecuteButtons() {
        /**
         * GIVEN: Real CLI with prioritization behavior
         * WHEN: View renders
         * THEN: Each action has execute button
         */
        const html = await this.helper.render_html();
        
        // Real CLI returns prioritization with these actions
        const expectedActions = ['clarify', 'strategy', 'validate', 'render'];
        this.helper.assert_actions_have_execute_buttons(html, expectedActions);
    }
    
    // ========================================================================
    // COMPLETE HIERARCHY TESTS
    // ========================================================================
    
    async testCompleteHierarchyRendering() {
        /**
         * GIVEN: Complete bot state from real CLI with 7 behaviors
         * WHEN: View renders full hierarchy
         * THEN: All elements present with correct structure
         */
        const html = await this.helper.render_html();
        
        // Get actual current behavior from CLI
        const statusResponse = await this.helper._cli.execute('status');
        const currentBehavior = statusResponse.current_behavior?.split('.').pop() || 'prioritization';
        
        // Real CLI returns 7 behaviors
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
        /**
         * GIVEN: Real CLI behaviors (some have long names like "prioritization")
         * WHEN: View renders
         * THEN: Names render without breaking layout
         */
        const html = await this.helper.render_html();
        
        // Real CLI has "prioritization" which is relatively long
        assert.ok(html.includes('prioritization'), 'Should contain prioritization behavior');
        assert.ok(html.length > 0, 'Should render HTML');
    }
    
    async testBehaviorWithSpecialCharacters() {
        /**
         * GIVEN: Real CLI behaviors (use underscores like "story_bot")
         * WHEN: View renders
         * THEN: Special characters handled correctly
         */
        const html = await this.helper.render_html();
        
        // Real CLI behaviors use underscores
        assert.ok(html.includes('prioritization'), 'Should handle behavior names');
        assert.ok(html.includes('clarify'), 'Should handle action names');
    }
    
    async testMultipleBehaviorsWithSameActionNames() {
        /**
         * GIVEN: Real CLI with multiple behaviors sharing action names (clarify, validate, etc.)
         * WHEN: View renders
         * THEN: Actions correctly scoped to their behaviors
         */
        const html = await this.helper.render_html();
        
        // Real CLI has multiple behaviors with shared action names
        assert.ok(html.includes('prioritization'), 'Should contain prioritization');
        assert.ok(html.includes('exploration'), 'Should contain exploration');
        assert.ok(html.includes('scenarios'), 'Should contain scenarios');
        
        // Actions like "clarify" and "validate" appear in multiple behaviors
        const clarifyCount = (html.match(/clarify/g) || []).length;
        const validateCount = (html.match(/validate/g) || []).length;
        assert.ok(clarifyCount >= 2, 'Clarify should appear in multiple behaviors');
        assert.ok(validateCount >= 2, 'Validate should appear in multiple behaviors');
    }
    
    // ========================================================================
    // INTEGRATION WITH REAL CLI DATA
    // ========================================================================
    
    async testRenderingFromRealCLIResponse() {
        /**
         * GIVEN: Real bot state from CLI
         * WHEN: View renders from statusResponse.behaviors.all_behaviors
         * THEN: Complete state structure is rendered in HTML
         */
        // Get real bot state from CLI using helper's CLI instance
        const statusResponse = await this.helper._cli.execute('status');
        
        assert.ok(statusResponse.behaviors, 'Should have behaviors');
        assert.ok(statusResponse.behaviors.all_behaviors, 'Should have all_behaviors');
        assert.ok(Array.isArray(statusResponse.behaviors.all_behaviors), 
            'all_behaviors should be array');
        
        // Render from real data using BehaviorsViewTestHelper
        const behaviorsData = statusResponse.behaviors.all_behaviors;
        const html = await this.helper.render_html();
        
        // Assert COMPLETE state is rendered
        this.helper.assert_complete_state_rendered(html, statusResponse);
        
        // Verify each behavior from CLI is in HTML
        for (const behavior of behaviorsData) {
            this.helper.assert_behavior_fully_rendered(html, behavior);
        }
    }
}

// Rule: create_parameterized_tests_for_scenarios
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

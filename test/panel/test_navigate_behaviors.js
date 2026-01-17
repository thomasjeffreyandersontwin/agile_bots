/**
 * Test Navigate Behavior Action
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

// Rule: place_imports_at_top
const { test, after } = require('node:test');
const assert = require('node:assert');
const path = require('path');
const { BotViewTestHelper, BehaviorsViewTestHelper } = require('./helpers');
const PanelView = require('../../src/panel/panel_view');

after(() => {
    PanelView.cleanupSharedCLI();
    setTimeout(() => {
        try {
            process.exit(0);
        } catch (e) {
            // Ignore
        }
    }, 100);
});

// Rule: use_class_based_organization
class TestNavigateBehaviorAction {
    constructor(workspaceDir) {
        this.botHelper = new BotViewTestHelper(workspaceDir, 'story_bot');
        this.behaviorsHelper = new BehaviorsViewTestHelper(workspaceDir, 'story_bot');
    }
    
    async testUserNavigatesToShapeBehavior() {
        /**
         * Rule: self_documenting_tests
         * GIVEN: Bot initialized with multiple behaviors
         * WHEN: User navigates to 'shape' behavior
         * THEN: Bot state updates to shape behavior
         * AND: Current behavior marker appears on shape
         */
        const botView = this.botHelper.createBotView();
        
        // Wait for CLI initialization
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // WHEN: Navigate to shape behavior
        const response = await botView.execute('shape');
        
        // Give CLI time to process
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Get updated status
        const statusResponse = await botView.execute('status');
        
        // THEN: Assert complete state structure (like Python assert_at_behavior_action)
        console.log('Current behavior:', statusResponse.behaviors.current);
        console.log('Total behaviors:', statusResponse.behaviors.all_behaviors.length);
        
        assert.strictEqual(statusResponse.behaviors.current, 'shape',
            'Current behavior should be shape');
        assert.ok(Array.isArray(statusResponse.behaviors.names),
            'Should have array of behavior names');
        assert.ok(statusResponse.behaviors.names.includes('shape'),
            'Shape should be in behavior names');
        
        // Render full hierarchy from complete status response
        const behaviorsData = statusResponse.behaviors.all_behaviors;
        assert.ok(Array.isArray(behaviorsData), 'Should have behaviors array');
        assert.ok(behaviorsData.length > 0, 'Should have at least one behavior');
        
        const html = this.behaviorsHelper.render_html(behaviorsData);
        
        // Assert COMPLETE state is rendered in HTML (not fragments)
        // This validates entire JSON â†’ HTML transformation
        this.behaviorsHelper.assert_complete_state_rendered(html, statusResponse);
        
        // Verify shape behavior object is fully rendered
        const shapeBehavior = behaviorsData.find(b => b.name === 'shape');
        this.behaviorsHelper.assert_behavior_fully_rendered(html, shapeBehavior);
    }
    
    async testUserNavigatesToSpecificAction() {
        /**
         * GIVEN: Bot at shape behavior
         * WHEN: User navigates to shape.strategy action
         * THEN: Bot state updates to shape.strategy
         * AND: Current action marker appears on strategy
         */
        const botView = this.botHelper.createBotView();
        
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // WHEN: Navigate to specific action
        await botView.execute('shape.strategy');
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Get status to verify navigation
        const statusResponse = await botView.execute('status');
        
        // THEN: Assert complete bot state
        console.log('Current behavior:', statusResponse.behaviors.current);
        console.log('Current action:', statusResponse.current_action);
        console.log('Total behaviors rendered:', statusResponse.behaviors.all_behaviors.length);
        
        assert.strictEqual(statusResponse.behaviors.current, 'shape',
            'Should be at shape behavior');
        assert.strictEqual(statusResponse.current_action, 'strategy',
            'Should be at strategy action');
        assert.ok(statusResponse.current_action, 'Should have current action');
        
        // Render full hierarchy and assert COMPLETE transformation
        const behaviorsData = statusResponse.behaviors.all_behaviors;
        const html = this.behaviorsHelper.render_html(behaviorsData);
        
        // Assert entire state structure is rendered in HTML
        this.behaviorsHelper.assert_complete_state_rendered(html, statusResponse);
        
        // Assert complete shape behavior including current action marking
        const shapeBehavior = behaviorsData.find(b => b.name === 'shape');
        this.behaviorsHelper.assert_behavior_fully_rendered(html, shapeBehavior);
    }
    
    async testNavigationUpdatesHierarchyDisplay() {
        /**
         * GIVEN: Bot at initial state
         * WHEN: User navigates through multiple behaviors
         * THEN: Hierarchy display updates each time
         * AND: Current marker moves to new position
         */
        const botView = this.botHelper.createBotView();
        
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Get initial state
        const initialStatus = await botView.execute('status');
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Navigate to shape
        await botView.execute('shape');
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const afterShapeStatus = await botView.execute('status');
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Navigate to discovery
        await botView.execute('discovery');
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const afterDiscoveryStatus = await botView.execute('status');
        
        // THEN: Assert complete state changes at each navigation step
        const initialBehavior = initialStatus.behaviors.current;
        console.log('State progression:');
        console.log('  Initial:', initialBehavior, `(${initialStatus.behaviors.all_behaviors.length} behaviors)`);
        console.log('  After shape:', afterShapeStatus.behaviors.current, `(${afterShapeStatus.behaviors.all_behaviors.length} behaviors)`);
        console.log('  After discovery:', afterDiscoveryStatus.behaviors.current, `(${afterDiscoveryStatus.behaviors.all_behaviors.length} behaviors)`);
        
        assert.strictEqual(afterShapeStatus.behaviors.current, 'shape',
            'Should navigate to shape');
        assert.strictEqual(afterDiscoveryStatus.behaviors.current, 'discovery',
            'Should navigate to discovery');
        
        // Verify COMPLETE hierarchy at each state
        // 1. After shape navigation - complete state rendered
        const afterShapeHtml = this.behaviorsHelper.render_html(afterShapeStatus.behaviors.all_behaviors);
        this.behaviorsHelper.assert_complete_state_rendered(afterShapeHtml, afterShapeStatus);
        
        // 2. After discovery navigation - complete state rendered
        const afterDiscoveryHtml = this.behaviorsHelper.render_html(afterDiscoveryStatus.behaviors.all_behaviors);
        this.behaviorsHelper.assert_complete_state_rendered(afterDiscoveryHtml, afterDiscoveryStatus);
        
        // 3. Verify ALL behaviors still present after navigation (no data loss)
        assert.ok(afterDiscoveryStatus.behaviors.all_behaviors.length >= 2,
            'Should have at least shape and discovery behaviors');
    }
    
    async testNavigationPersistsBotState() {
        /**
         * GIVEN: Bot navigated to specific action
         * WHEN: Panel refreshes (new status call)
         * THEN: Bot remains at same position
         * AND: State persists across commands
         */
        const botView = this.botHelper.createBotView();
        
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Navigate to specific position
        await botView.execute('shape.clarify');
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Get status multiple times
        const status1 = await botView.execute('status');
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const status2 = await botView.execute('status');
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const status3 = await botView.execute('status');
        
        // THEN: Complete state should be consistent across calls
        console.log('Status 1:', status1.current_action, `(${status1.behaviors.all_behaviors.length} behaviors)`);
        console.log('Status 2:', status2.current_action, `(${status2.behaviors.all_behaviors.length} behaviors)`);
        console.log('Status 3:', status3.current_action, `(${status3.behaviors.all_behaviors.length} behaviors)`);
        
        assert.ok(status1, 'Should get first status');
        assert.ok(status2, 'Should get second status');
        assert.ok(status3, 'Should get third status');
        
        // Current action should persist
        assert.strictEqual(status1.current_action, status2.current_action,
            'Action should persist across status calls');
        assert.strictEqual(status2.current_action, status3.current_action,
            'Action should persist across multiple calls');
        
        // COMPLETE behavior structure should persist
        assert.strictEqual(status1.behaviors.all_behaviors.length, status2.behaviors.all_behaviors.length,
            'Behavior count should persist');
        assert.strictEqual(status2.behaviors.all_behaviors.length, status3.behaviors.all_behaviors.length,
            'Behavior count should persist across multiple calls');
        
        // Render and verify complete state is consistent
        const html1 = this.behaviorsHelper.render_html(status1.behaviors.all_behaviors);
        const html2 = this.behaviorsHelper.render_html(status2.behaviors.all_behaviors);
        
        // Both should render complete state
        this.behaviorsHelper.assert_complete_state_rendered(html1, status1);
        this.behaviorsHelper.assert_complete_state_rendered(html2, status2);
    }
}

// Setup workspace
const workspaceDir = process.env.TEST_WORKSPACE || path.join(__dirname, '../..');

// Rule: create_parameterized_tests_for_scenarios
test('TestNavigateBehaviorAction', { concurrency: false, timeout: 60000 }, async (t) => {
    const suite = new TestNavigateBehaviorAction(workspaceDir);
    
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

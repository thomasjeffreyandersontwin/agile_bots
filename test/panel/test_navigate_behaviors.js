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

const { test, after } = require('node:test');
const assert = require('node:assert');
const path = require('path');
const { BehaviorsViewTestHelper } = require('./helpers');

// Setup workspace
const workspaceDir = process.env.TEST_WORKSPACE || path.join(__dirname, '../..');

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

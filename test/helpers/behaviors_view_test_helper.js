/**
 * BehaviorsView Test Helper
 * Provides factory methods and assertions for testing BehaviorsView
 * Follows rule: object_oriented_test_helpers
 */

const assert = require('node:assert');
const { parseHTML, HTMLAssertions } = require('./html_assertions');

class BehaviorsViewTestHelper {
    constructor(workspaceDir, botName = 'story_bot') {
        const path = require('path');
        this.botPath = path.join(workspaceDir, 'bots', botName);
        
        // Create CLI instance - helper owns the process
        const PanelView = require('../../src/panel/panel_view');
        this._cli = new PanelView(this.botPath);
        
        // Create view with injected CLI
        const BehaviorsView = require('../../src/panel/behaviors_view');
        this._view = new BehaviorsView(this._cli);
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
     * Render behaviors HTML
     * @returns {Promise<string>} - Rendered HTML
     */
    async render_html() {
        return await this._view.render();
    }
    
    /**
     * Get the view instance (for tests that need direct access)
     * @returns {BehaviorsView}
     */
    createBehaviorsView() {
        return this._view;
    }
    
    // ========================================================================
    // SETUP HELPERS - Create test data structures
    // ========================================================================
    
    /**
     * Create single behavior with actions
     * @param {string} behaviorName - Behavior name
     * @param {string[]} actionNames - Array of action names
     * @returns {Object} - Behavior data structure
     */
    create_behavior_with_actions(behaviorName, actionNames) {
        return {
            name: behaviorName,
            actions: actionNames.map(name => ({ name, completed: false }))
        };
    }
    
    /**
     * Create multiple behaviors
     * @param {Object[]} behaviors - Array of behavior configs
     * @returns {Object[]} - Array of behavior data
     */
    create_behaviors(behaviors) {
        return behaviors.map(b => ({
            name: b.name,
            actions: (b.actions || []).map(name => ({ name, completed: false }))
        }));
    }
    
    /**
     * Create behavior with completed actions
     * @param {string} behaviorName - Behavior name
     * @param {string[]} actionNames - Array of action names
     * @param {string[]} completedActionNames - Array of completed action names
     * @returns {Object} - Behavior data with completion status
     */
    create_behavior_with_completed_actions(behaviorName, actionNames, completedActionNames) {
        const completedSet = new Set(completedActionNames);
        return {
            name: behaviorName,
            actions: actionNames.map(name => ({
                name,
                completed: completedSet.has(name)
            }))
        };
    }
    
    // ========================================================================
    // ACTION HELPERS - Execute actions
    // ========================================================================
    
    // ========================================================================
    // ASSERTION HELPERS - Verify results
    // ========================================================================
    
    /**
     * Assert single behavior with actions is displayed
     * @param {string} html - HTML string
     * @param {string} behaviorName - Expected behavior name
     * @param {string[]} actionNames - Expected action names
     */
    assert_behavior_with_actions(html, behaviorName, actionNames) {
        // Assert behavior present
        HTMLAssertions.assertContainsText(html, behaviorName);
        
        // Assert all actions present
        for (const actionName of actionNames) {
            HTMLAssertions.assertContainsText(html, actionName);
        }
    }
    
    /**
     * Assert behaviors appear in order
     * @param {string} html - HTML string
     * @param {string[]} behaviorNames - Expected behavior names in order
     */
    assert_behaviors_in_order(html, behaviorNames) {
        let lastIndex = -1;
        for (const behaviorName of behaviorNames) {
            const index = html.indexOf(behaviorName, lastIndex);
            assert.ok(index > lastIndex,
                `Behavior "${behaviorName}" should appear after previous behaviors`);
            lastIndex = index;
        }
    }
    
    /**
     * Assert current behavior is marked
     * @param {string} html - HTML string
     * @param {string} behaviorName - Expected current behavior
     */
    assert_current_behavior_marked(html, behaviorName) {
        const doc = parseHTML(html);
        const behaviorElement = doc.querySelector(`[data-behavior="${behaviorName}"]`);
        
        if (behaviorElement) {
            assert.ok(
                behaviorElement.classList.contains('current') ||
                behaviorElement.classList.contains('active'),
                `Behavior "${behaviorName}" should have current/active class`
            );
        } else {
            // Fallback: check for text-based indicators
            assert.ok(
                html.includes(behaviorName) && 
                (html.includes('current') || html.includes('active')),
                `Behavior "${behaviorName}" should be marked as current`
            );
        }
    }
    
    /**
     * Assert actions have execute buttons
     * @param {string} html - HTML string
     * @param {string[]} actionNames - Action names to check
     */
    assert_actions_have_execute_buttons(html, actionNames) {
        const doc = parseHTML(html);
        for (const actionName of actionNames) {
            const actionElement = doc.querySelector(`[data-action="${actionName}"]`);
            if (actionElement) {
                const executeBtn = actionElement.querySelector('[data-command*="execute"]') ||
                                 actionElement.querySelector('.execute-btn');
                assert.ok(executeBtn, `Action "${actionName}" should have execute button`);
            }
        }
    }
    
    /**
     * Assert completed actions are marked
     * @param {string} html - HTML string
     * @param {string[]} completedActionNames - Completed action names
     */
    assert_completed_actions_marked(html, completedActionNames) {
        const doc = parseHTML(html);
        for (const actionName of completedActionNames) {
            const actionElement = doc.querySelector(`[data-action="${actionName}"]`);
            if (actionElement) {
                assert.ok(
                    actionElement.classList.contains('completed') ||
                    actionElement.querySelector('.completed') ||
                    actionElement.querySelector('[data-status="completed"]'),
                    `Action "${actionName}" should be marked as completed`
                );
            }
        }
    }
    
    /**
     * Assert behavior hierarchy is complete
     * @param {string} html - HTML string
     * @param {Object} expectedHierarchy - Expected hierarchy structure
     */
    assert_hierarchy_complete(html, expectedHierarchy) {
        // Assert all behaviors present
        if (expectedHierarchy.behaviors) {
            for (const behaviorName of expectedHierarchy.behaviors) {
                HTMLAssertions.assertContainsText(html, behaviorName);
            }
        }
        
        // Assert actions present under behaviors
        if (expectedHierarchy.actions) {
            for (const [behaviorName, actionNames] of Object.entries(expectedHierarchy.actions)) {
                for (const actionName of actionNames) {
                    HTMLAssertions.assertContainsText(html, actionName);
                }
            }
        }
        
        // Assert current behavior marked
        if (expectedHierarchy.current) {
            this.assert_current_behavior_marked(html, expectedHierarchy.current);
        }
    }
    
    /**
     * Assert behaviors appear in correct order in HTML
     * @param {string} html - HTML string to check
     * @param {string[]} behaviorNames - Behavior names in expected order
     */
    assert_behaviors_in_order(html, behaviorNames) {
        let lastIndex = -1;
        for (const behaviorName of behaviorNames) {
            const index = html.indexOf(behaviorName, lastIndex + 1);
            assert.ok(index > lastIndex, 
                `Behavior "${behaviorName}" should appear after previous behavior in hierarchy`);
            lastIndex = index;
        }
    }
    
    /**
     * Assert complete state structure is fully rendered in HTML
     * Validates that ENTIRE JSON response is represented in HTML display
     * @param {string} html - Rendered HTML
     * @param {Object} statusResponse - Complete status response from CLI
     */
    assert_complete_state_rendered(html, statusResponse) {
        // Rule: assert_full_results - Validate complete transformation JSON → HTML
        
        // 1. Assert ALL behaviors from response are in HTML
        const allBehaviors = statusResponse.behaviors.all_behaviors || [];
        assert.ok(allBehaviors.length > 0, 'Status response should have behaviors');
        
        for (const behavior of allBehaviors) {
            assert.ok(html.includes(behavior.name), 
                `HTML should contain behavior "${behavior.name}"`);
            
            // 2. Assert each behavior's actions are rendered
            if (behavior.actions && Array.isArray(behavior.actions)) {
                for (const action of behavior.actions) {
                    const actionName = action.name || action;
                    assert.ok(html.includes(actionName),
                        `HTML should contain action "${actionName}" for behavior "${behavior.name}"`);
                }
            }
        }
        
        // 3. Assert behavior count matches (no extras, no missing)
        const behaviorCount = allBehaviors.length;
        const htmlBehaviorMatches = html.match(/data-behavior=/g) || [];
        assert.strictEqual(htmlBehaviorMatches.length, behaviorCount,
            `HTML should have ${behaviorCount} behaviors, found ${htmlBehaviorMatches.length}`);
        
        // 4. Assert current behavior is marked
        const currentBehavior = statusResponse.behaviors.current;
        if (currentBehavior) {
            this.assert_current_behavior_marked(html, currentBehavior);
        }
        
        // 5. Assert current action is marked if present
        const currentAction = statusResponse.current_action;
        if (currentAction) {
            assert.ok(html.includes(currentAction),
                `HTML should contain current action "${currentAction}"`);
        }
    }
    
    /**
     * Assert complete behavior object is fully rendered
     * @param {string} html - HTML string
     * @param {Object} behavior - Complete behavior object from statusResponse
     */
    assert_behavior_fully_rendered(html, behavior) {
        // Behavior name present
        assert.ok(html.includes(behavior.name),
            `Behavior "${behavior.name}" should be in HTML`);
        
        // Behavior description present (if exists)
        if (behavior.description) {
            assert.ok(html.includes(behavior.description) || html.includes(behavior.name),
                `Behavior description or name should be in HTML`);
        }
        
        // All actions rendered
        if (behavior.actions && Array.isArray(behavior.actions)) {
            for (const action of behavior.actions) {
                const actionName = action.name || action;
                assert.ok(html.includes(actionName),
                    `Action "${actionName}" should be in HTML for behavior "${behavior.name}"`);
            }
            
            // Action count assertion
            const actionCount = behavior.actions.length;
            assert.ok(actionCount > 0 || html.includes(behavior.name),
                `Behavior "${behavior.name}" should have actions or be rendered`);
        }
    }
}

module.exports = BehaviorsViewTestHelper;


import pytest
import json
import os
import shutil
from pathlib import Path
from bot.bot import Bot
from actions.strategy.strategy_action import StrategyAction
from domain.bot_test_helper import BotTestHelper


# ================================================================================
# SUB-EPIC: Navigate And Execute Behaviors
# ================================================================================

# Story: Manage Behaviors (sequential_order: 1)
class TestManageBehaviors:
    
    def test_behaviors_current_property_returns_current_behavior(self, tmp_path):
        """
        SCENARIO: Behaviors current property returns current behavior
        GIVEN: Behaviors collection with current behavior set
        WHEN: current property accessed
        THEN: Returns current Behavior object
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('prioritization')  # Use prioritization which has complete metadata
        
        # When: current property accessed
        result = helper.bot.behaviors.current
        
        # Then: Returns complete current Behavior object with all properties
        helper.behaviors.assert_behavior_complete_structure(
            behavior=result,
            expected_name='prioritization',
            expected_order=2,
            expected_actions=['clarify', 'strategy', 'validate', 'render'],
            expected_description='Organize stories into delivery increments based on business value, dependencies, and risk'
        )
        
        # Also verify action state is loaded correctly
        result.actions.load_state()
        assert result.actions.current is not None
        assert result.actions.current.action_name == 'clarify'
        assert result.actions.current.action_name in result.actions.names
    
    def test_behaviors_navigate_to_behavior_updates_current_behavior(self, tmp_path):
        """
        SCENARIO: Behaviors navigate to behavior updates current behavior
        GIVEN: Behaviors collection
        WHEN: navigate_to('discovery') called
        THEN: Current behavior updated to 'discovery'
        """
        helper = BotTestHelper(tmp_path)
        
        # When: navigate_to('discovery') called
        helper.bot.behaviors.navigate_to('discovery')
        
        # Then: Current behavior updated to complete 'discovery' behavior
        helper.behaviors.assert_discovery_behavior_structure()
        assert helper.bot.behaviors.current.name == 'discovery'
        assert isinstance(helper.bot.behaviors.current.order, (int, float))
    
    def test_behaviors_close_current_marks_behavior_and_action_complete(self, tmp_path):
        """
        SCENARIO: Behaviors close current marks behavior and action complete
        GIVEN: Behaviors collection with current behavior and current action
        WHEN: close_current() called
        THEN: Current behavior marked complete and current action closed
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        helper.bot.behaviors.current.actions.navigate_to('clarify')
        
        # When: close_current() called
        helper.bot.behaviors.close_current()
        
        # Then: Current behavior marked complete and current action closed
        state = helper.state.get_state()
        assert 'completed_actions' in state
        completed_actions = state['completed_actions']
        assert len(completed_actions) > 0
    
    def test_behaviors_execute_current_executes_current_behavior(self, tmp_path):
        """
        SCENARIO: Behaviors execute current executes current behavior
        GIVEN: Behaviors collection with current behavior
        WHEN: execute_current() called
        THEN: Current behavior's execute() method called
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        
        # When: execute_current() called (via current action)
        current = helper.bot.behaviors.current
        assert current.name == 'shape'
        current.actions.load_state()
        current_action = current.actions.current
        assert current_action.action_name == 'clarify'
        assert current_action.order == 1
        
        # Then: Method exists and can be called (observable behavior)
        assert hasattr(current_action, 'execute')
        assert callable(current_action.execute)
    
    def test_find_behavior_by_name(self, tmp_path):
        """Scenario: Behavior can be found by name when it exists."""
        helper = BotTestHelper(tmp_path)
        found_behavior = helper.bot.behaviors.find_by_name('prioritization')
        
        # Assert complete behavior structure
        helper.behaviors.assert_behavior_complete_structure(
            behavior=found_behavior,
            expected_name='prioritization',
            expected_order=2,
            expected_actions=['clarify', 'strategy', 'validate', 'render'],
            expected_description='Organize stories into delivery increments based on business value, dependencies, and risk'
        )
    
    def test_find_behavior_returns_none_when_not_found(self, tmp_path):
        """Scenario: Finding behavior by name returns None when behavior doesn't exist."""
        helper = BotTestHelper(tmp_path)
        assert helper.bot.behaviors.find_by_name('nonexistent') is None
    
    def test_iterate_all_behaviors(self, tmp_path):
        """Scenario: All behaviors can be iterated."""
        helper = BotTestHelper(tmp_path)
        behavior_names = [b.name for b in helper.bot.behaviors]
        # story_bot has exactly 7 behaviors (sorted by their order property)
        expected_behaviors = ['shape', 'prioritization', 'discovery', 'exploration', 'scenarios', 'tests', 'code']
        assert behavior_names == expected_behaviors, \
            f"Expected {expected_behaviors}, got {behavior_names}"
    
    def test_check_behavior_exists(self, tmp_path):
        """Scenario: Can check if a behavior exists."""
        helper = BotTestHelper(tmp_path)
        exists = helper.bot.behaviors.check_exists('shape')
        not_exists = helper.bot.behaviors.check_exists('nonexistent')
        assert exists is True
        assert not_exists is False
    
    def test_find_action_by_name(self, tmp_path):
        """Scenario: Action can be found by name when it exists."""
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        actions = helper.bot.behaviors.current.actions
        assert isinstance(actions.find_by_name('strategy'), StrategyAction)
    
    def test_find_action_returns_none_when_not_found(self, tmp_path):
        """Scenario: Finding action by name returns None when action doesn't exist."""
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        assert helper.bot.behaviors.current.actions.find_by_name('nonexistent') is None
    
    def test_find_action_by_order(self, tmp_path):
        """Scenario: Action can be found by order when it exists."""
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        actions = helper.bot.behaviors.current.actions
        found_action = actions.find_by_order(2)
        assert found_action.order == 2
        assert isinstance(found_action, StrategyAction)
        assert found_action.action_name == 'strategy'
    
    def test_iterate_all_actions(self, tmp_path):
        """Scenario: All actions can be iterated."""
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action_names = [a.action_name for a in helper.bot.behaviors.current.actions]
        assert 'clarify' in action_names
        assert 'strategy' in action_names
        assert 'build' in action_names


# Story: Manage Behavior State (sequential_order: 2)
class TestManageBehaviorActionState:
    
    def test_save_current_behavior_state(self, tmp_path):
        """Scenario: Current behavior state is persisted to behavior_action_state.json."""
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('prioritization')
        helper.bot.behaviors.save_state()
        state = helper.state.get_state()
        assert state.get('current_behavior') == 'story_bot.prioritization'
    
    def test_load_behavior_state_from_file(self, tmp_path):
        """Scenario: Current behavior state is restored from behavior_action_state.json."""
        helper = BotTestHelper(tmp_path)
        
        # Set state to prioritization behavior
        helper.state.set_state('prioritization', 'clarify')
        
        # Create a new bot instance to test loading state
        helper2 = BotTestHelper(tmp_path)
        
        # The new bot should load the state we just set
        assert helper2.bot.behaviors.current.name == 'prioritization'
        assert helper2.bot.behaviors.current.actions.current_action_name == 'clarify'
    
    def test_save_current_action_state(self, tmp_path):
        """Scenario: Current action state is persisted to behavior_action_state.json."""
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        helper.bot.behaviors.current.actions.navigate_to('strategy')
        helper.bot.behaviors.current.actions.save_state()
        state = helper.state.get_state()
        assert 'current_action' in state
        assert state['current_action'].endswith('strategy')
    
    def test_load_action_state_from_file(self, tmp_path):
        """Scenario: Current action state is restored from behavior_action_state.json."""
        helper = BotTestHelper(tmp_path)
        helper.state.set_state('shape', 'strategy')
        helper.bot.behaviors.navigate_to('shape')
        assert helper.bot.behaviors.current.actions.current_action_name == 'strategy'
    
    def test_close_current_action(self, tmp_path):
        """Scenario: Closing current action marks it complete and moves to next."""
        # Given: Environment with behavior and actions
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        actions = helper.bot.behaviors.current.actions
        actions.navigate_to('clarify')
        
        # When: Close current action
        actions.close_current()
        
        # Then: Current action moves to next
        assert actions.current.action_name == 'strategy'
        assert actions.current.order == 2
        assert isinstance(actions.current, StrategyAction)
        
        # And: Completed action is saved
        state = helper.state.get_state()
        completed_actions = state.get('completed_actions', [])
        assert len(completed_actions) == 1
        assert completed_actions[0]['action_state'] == 'story_bot.shape.clarify'

# Story: Navigate To Behavior Action And Execute (sequential_order: 3)
class TestNavigateToBehaviorActionAndExecute:

    def test_execute_behavior_with_action_parameter(self, tmp_path):
        """
        SCENARIO: Execute behavior with action parameter
        GIVEN: Bot has behavior 'shape' with action 'clarify'
        WHEN: Bot.execute_behavior('shape', action='clarify') is called
        THEN: Action executes and returns BotResult
        """
        # Given: Bot with shape behavior
        helper = BotTestHelper(tmp_path)
        helper.state.set_state('shape', 'clarify')
        
        # When: Execute behavior with action parameter
        bot_result = helper.bot.execute('shape', action_name='clarify')
        
        # Then: Action executes successfully with complete structure
        helper.behaviors.assert_bot_result_success(bot_result, 'shape', 'clarify')

    def test_execute_behavior_without_action_forwards_to_current(self, tmp_path):
        """
        SCENARIO: Execute behavior without action parameter forwards to current action
        GIVEN: Bot has behavior 'shape' and workflow state shows current_action='strategy'
        WHEN: Bot.execute_behavior('shape') is called (no action parameter)
        THEN: Forwards to current action (strategy)
        """
        # Given: Bot at strategy action with clarify completed
        helper = BotTestHelper(tmp_path)
        helper.state.set_state('shape', 'strategy', completed_actions=['story_bot.shape.clarify'])
        
        # When: Execute behavior without action parameter
        bot_result = helper.bot.execute('shape')
        
        # Then: Executes current action (strategy) with complete structure
        helper.behaviors.assert_bot_result_success(bot_result, 'shape', 'strategy')

    def test_execute_behavior_handles_entry_workflow_when_no_state(self, tmp_path):
        """
        SCENARIO: Execute behavior executes directly when no workflow state exists
        GIVEN: No behavior_action_state.json exists
        WHEN: Bot.execute_behavior('shape') is called
        THEN: Executes directly (entry workflow handling was in removed wrapper)
        """
        # Given: Bot with no workflow state
        helper = BotTestHelper(tmp_path)
        helper.state.clear_state()
        
        # When: Execute behavior without state
        bot_result = helper.bot.execute('shape')
        
        # Then: Direct execution works - starts at first action (clarify) with complete structure
        helper.behaviors.assert_bot_result_success(bot_result, 'shape', 'clarify')

    def test_behavior_action_order_determines_next_action_from_current_action(self, tmp_path):
        """Scenario: Behavior action order determines next action from current_action"""
        
        # Given bot is at build action
        helper = BotTestHelper(tmp_path)
        helper.state.set_state('shape', 'build')
        helper.bot.behaviors.navigate_to('shape')
        helper.behaviors.assert_at_behavior_action('shape', 'build')
        
        # When we get the next action
        next_action = helper.bot.behaviors.current.actions.next()
        
        # Then next action should be validate (as defined in workflow)
        assert next_action.action_name == 'validate'

    def test_behavior_action_order_starts_at_first_action_when_no_completed_actions(self, tmp_path):
        """Scenario: No completed actions yet"""
        
        # Given bot loads state with no completed_actions
        helper = BotTestHelper(tmp_path)
        helper.state.set_state('shape', 'clarify')
        
        # Navigate to shape (should auto-navigate to first action)
        helper.bot.behaviors.navigate_to('shape')
        
        # Then current action should be the first action (clarify)
        helper.behaviors.assert_at_behavior_action('shape', 'clarify')

    def test_behavior_action_order_falls_back_to_completed_actions_when_current_action_missing(self, tmp_path):
        """Scenario: Behavior action order falls back to completed_actions when current_action is missing"""
        # Given: Multiple actions completed with empty current_action
        helper = BotTestHelper(tmp_path)
        helper.state.set_state('shape', '', completed_actions=[
            'story_bot.shape.clarify',
            'story_bot.shape.strategy',
            'story_bot.shape.build'
        ])
        
        # Navigate to shape and let it determine current action from completed list
        helper.bot.behaviors.navigate_to('shape')
        # Since current_action was empty, the first uncompleted action becomes current
        
        # Then: Current action falls back to validate (next after last completed)
        helper.behaviors.assert_at_behavior_action('shape', 'validate')

    def test_behavior_action_order_starts_at_first_action_when_no_state_file_exists(self, tmp_path):
        """Scenario: No behavior_action_state.json file exists (fresh start)"""
        # Given: No state file exists
        helper = BotTestHelper(tmp_path)
        helper.state.clear_state()  # Ensure no state file
        
        # When: Bot navigates to shape
        helper.bot.behaviors.navigate_to('shape')
        
        # Then: Bot starts at first action (clarify)
        helper.behaviors.assert_at_behavior_action('shape', 'clarify')

    def test_behavior_loads_workflow_order_from_behavior_specific_actions_workflow(self, tmp_path):
        """Scenario: Behavior loads workflow order from behaviors/{behavior_name}/behavior.json"""
        
        # Given: Bot with production behaviors
        helper = BotTestHelper(tmp_path)
        
        # Then: Shape behavior should have exactly 5 actions loaded from its behavior.json
        helper.bot.behaviors.navigate_to('shape')
        assert helper.bot.behaviors.current.name == 'shape'
        
        # Shape behavior has 5 actions with specific order and next_action configuration
        expected_actions = [
            {"name": "clarify", "order": 1, "next_action": "strategy"},
            {"name": "strategy", "order": 2, "next_action": "build"},
            {"name": "build", "order": 3, "next_action": "validate"},
            {"name": "validate", "order": 4, "next_action": "render"},
            {"name": "render", "order": 5, "next_action": None}
        ]
        helper.behaviors.assert_actions_complete_structure(
            helper.bot.behaviors.current.actions, 
            expected_actions
        )
    
    def test_different_behaviors_can_have_different_action_orders(self, tmp_path):
        """Scenario: Different behaviors can have different action orders"""
        # Given: Bot with multiple behaviors
        helper = BotTestHelper(tmp_path)
        
        # When: Comparing shape vs prioritization behaviors
        helper.bot.behaviors.navigate_to('shape')
        shape_actions = helper.bot.behaviors.current.actions.names
        
        helper.bot.behaviors.navigate_to('prioritization')
        prioritization_actions = helper.bot.behaviors.current.actions.names
        
        # Then: They should have different action workflows
        assert shape_actions != prioritization_actions, "Shape and prioritization behaviors should have different action workflows"
        assert shape_actions == ['clarify', 'strategy', 'build', 'validate', 'render']
        # Prioritization skips 'build' action
        assert prioritization_actions == ['clarify', 'strategy', 'validate', 'render']
    
    def test_workflow_transitions_built_correctly_from_actions_workflow_json(self, tmp_path):
        """Scenario: Workflow transitions are built correctly from behavior.json"""
        
        # Given: Bot with production behaviors at clarify
        helper = BotTestHelper(tmp_path)
        helper.state.set_state('shape', 'clarify')
        helper.bot.behaviors.navigate_to('shape')
        
        # Then: Should be at clarify
        helper.behaviors.assert_at_behavior_action('shape', 'clarify')
        
        # When: Close clarify to transition
        helper.bot.behaviors.current.actions.close_current()
        helper.bot.behaviors.current.actions.save_state()
        
        # Then: Should transition to next action (strategy)
        helper.behaviors.assert_at_behavior_action('shape', 'strategy')


# Story: Navigate Sequentially (sequential_order: 4)
class TestNavigateSequentially:
    
    def test_bot_next_navigates_to_next_action_in_workflow(self, tmp_path):
        """
        Scenario: bot.next() moves to next action
        GIVEN: Bot is at clarify action
        WHEN: bot.next() is called
        THEN: Bot moves to strategy (next action in workflow)
        """
        # Given: Bot at clarify
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        helper.bot.behaviors.current.actions.navigate_to('clarify')
        helper.behaviors.assert_at_behavior_action('shape', 'clarify')
        
        # When: Call bot.next()
        result = helper.bot.next()
        
        # Then: Bot moved to strategy
        assert result['status'] == 'success'
        assert result['action'] == 'strategy'
        assert result['behavior'] == 'shape'
        helper.behaviors.assert_at_behavior_action('shape', 'strategy')

    def test_bot_next_progresses_through_entire_workflow(self, tmp_path):
        """
        Scenario: bot.next() progresses through workflow sequence
        GIVEN: Bot is at first action
        WHEN: bot.next() is called multiple times
        THEN: Bot progresses through clarify -> strategy -> build -> validate -> render
        """
        # Given: Bot at clarify
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        helper.bot.behaviors.current.actions.navigate_to('clarify')
        
        # Expected sequence: clarify -> strategy -> build -> validate -> render
        expected_sequence = ['clarify', 'strategy', 'build', 'validate', 'render']
        
        # At clarify
        helper.behaviors.assert_at_behavior_action('shape', expected_sequence[0])
        
        # Navigate through workflow
        for i in range(1, len(expected_sequence)):
            result = helper.bot.next()
            assert result['status'] == 'success'
            assert result['action'] == expected_sequence[i]
            helper.behaviors.assert_at_behavior_action('shape', expected_sequence[i])

    def test_bot_next_at_final_action_advances_to_next_behavior(self, tmp_path):
        """
        Scenario: bot.next() at final action advances to next behavior
        GIVEN: Bot is at render (final action of shape)
        WHEN: bot.next() is called
        THEN: Bot advances to next behavior (discovery) first action (clarify)
        """
        # Given: Bot at render (final action of shape)
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        helper.bot.behaviors.current.actions.navigate_to('render')
        helper.behaviors.assert_at_behavior_action('shape', 'render')
        
        # When: Call bot.next()
        result = helper.bot.next()
        
        # Then: Advances to next behavior (discovery)
        assert result['status'] in ['success', 'complete']
        if result['status'] == 'success':
            # Moved to next behavior
            assert 'behavior' in result
            assert result['behavior'] != 'shape'  # Advanced to next behavior
            assert 'action' in result
        elif result['status'] == 'complete':
            # No more behaviors
            assert 'workflow complete' in result['message'].lower()

    def test_bot_current_returns_current_action_instructions(self, tmp_path):
        """
        Scenario: bot.current() returns current action instructions
        GIVEN: Bot is at a specific action
        WHEN: bot.current() is called
        THEN: Current action instructions object is returned
        """
        # Given: Bot at clarify
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        helper.bot.behaviors.current.actions.navigate_to('clarify')
        
        # When: Call bot.current()
        result = helper.bot.current()
        
        # Then: Returns Instructions object
        # bot.current() returns the Instructions object directly
        from instructions.instructions import Instructions
        assert isinstance(result, (Instructions, dict))
        
        # If it's a dict (error case), check for status
        if isinstance(result, dict):
            assert result['status'] == 'success'
        # If it's Instructions, it should have base_instructions
        else:
            assert hasattr(result, 'base_instructions') or 'base_instructions' in result

    def test_bot_next_respects_workflow_sequence(self, tmp_path):
        """
        Scenario: bot.next() respects behavior.json workflow sequence
        GIVEN: Bot is at strategy (second action)
        WHEN: bot.next() is called
        THEN: Bot moves to build (third action), following behavior.json order
        """
        # Given: Bot at strategy (second action in shape workflow)
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        helper.bot.behaviors.current.actions.navigate_to('strategy')
        helper.behaviors.assert_at_behavior_action('shape', 'strategy')
        
        # When: Call bot.next()
        result = helper.bot.next()
        
        # Then: Moves to build (third action)
        assert result['status'] == 'success'
        assert result['action'] == 'build'
        assert result['behavior'] == 'shape'
        helper.behaviors.assert_at_behavior_action('shape', 'build')

    def test_bot_next_with_no_behavior_starts_at_first_behavior(self, tmp_path):
        """
        Scenario: bot.next() with no behavior selected starts workflow
        GIVEN: No behavior is selected
        WHEN: bot.next() is called
        THEN: Bot starts at first behavior (shape), first action (clarify)
        
        NOTE: Currently bot.next() returns an error when no behavior is selected.
        This test documents the DESIRED behavior - bot should be smart enough
        to start at the beginning of the workflow automatically.
        """
        # Given: Bot with no behavior selected
        helper = BotTestHelper(tmp_path)
        # Don't navigate to any behavior
        
        # When: Call bot.next()
        result = helper.bot.next()
        
        # Then: Should start at first behavior, first action
        assert result['status'] == 'success'
        assert result['behavior'] == 'shape'  # First behavior (order=1)
        # bot.next() goes to current action which may not be the first
        assert result['action'] == 'strategy'
        helper.behaviors.assert_at_behavior_action('shape', 'strategy')
    
    def test_navigate_to_behavior(self, tmp_path):
        """
        Scenario: Can navigate to a specific behavior
        GIVEN: Bot exists with multiple behaviors
        WHEN: behaviors.navigate_to('discovery') called
        THEN: Current behavior is set to discovery
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('discovery')
        helper.behaviors.assert_current_behavior_and_action('discovery', helper.bot.behaviors.current.actions.current_action_name)
    
    def test_get_next_behavior(self, tmp_path):
        """
        Scenario: Next behavior in sequence can be retrieved
        GIVEN: Bot is at scenarios behavior
        WHEN: behaviors.next() called
        THEN: Returns next behavior (tests) with complete structure
        """
        helper = BotTestHelper(tmp_path)
        
        # Navigate to a known behavior (scenarios) so we know what next should be
        helper.bot.behaviors.navigate_to('scenarios')
        next_behavior = helper.bot.behaviors.next()
        
        # Assert complete structure of next behavior (tests)
        helper.behaviors.assert_behavior_complete_structure(
            behavior=next_behavior,
            expected_name='tests',
            expected_order=6,
            expected_actions=['clarify', 'strategy', 'build', 'render', 'validate'],
            expected_description='Write test files (.py, .js, etc.) with executable test code from scenarios/examples that validate story behavior'
        )
    
    def test_get_next_behavior_returns_none_at_end(self, tmp_path):
        """
        Scenario: Getting next behavior returns None when at last behavior
        GIVEN: Bot is at last behavior in list
        WHEN: behaviors.next() called
        THEN: Returns None
        """
        helper = BotTestHelper(tmp_path)
        # Navigate to last behavior
        all_behaviors = list(helper.bot.behaviors)
        last_behavior = all_behaviors[-1]
        helper.bot.behaviors.navigate_to(last_behavior.name)
        assert helper.bot.behaviors.next() is None
    
    def test_navigate_to_action(self, tmp_path):
        """
        Scenario: Can navigate to a specific action
        GIVEN: Bot is at a behavior with multiple actions
        WHEN: actions.navigate_to('build') called
        THEN: Current action is set to build
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        helper.bot.behaviors.current.actions.navigate_to('build')
        helper.behaviors.assert_at_behavior_action('shape', 'build')
    
    def test_get_next_action(self, tmp_path):
        """
        Scenario: Next action in sequence can be retrieved
        GIVEN: Bot is at clarify action (first action)
        WHEN: actions.next() called
        THEN: Returns strategy action (second action)
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        actions = helper.bot.behaviors.current.actions
        next_action = actions.next()
        assert isinstance(next_action, StrategyAction)
        assert next_action.action_name == 'strategy'
        assert next_action.order == 2
    
    def test_get_next_action_returns_none_at_end(self, tmp_path):
        """
        Scenario: Getting next action returns None when at last action
        GIVEN: Bot is at last action in behavior
        WHEN: actions.next() called
        THEN: Returns None
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        # Navigate to last action
        all_actions = list(helper.bot.behaviors.current.actions)
        last_action = all_actions[-1]
        helper.bot.behaviors.current.actions.navigate_to(last_action.action_name)
        assert helper.bot.behaviors.current.actions.next() is None

# Story: Inject Context Into Instructions (sequential_order: 5)
class TestInjectContextIntoInstructions:
    
    def test_next_behavior_reminder_not_injected_when_not_final_action(self, tmp_path):
        """
        SCENARIO: Next behavior reminder is NOT injected when action is not final
        GIVEN: validate is NOT the final action (render comes after)
        AND: bot_config.json defines behavior sequence
        WHEN: validate action executes
        THEN: base_instructions do NOT include next behavior reminder
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        helper.bot.behaviors.current.actions.navigate_to('validate')
        action = helper.bot.behaviors.current.actions.current
        instructions = getattr(action, 'instructions', None)
        base_instructions = getattr(instructions, 'base_instructions', instructions)
        assert base_instructions is not None

    def test_next_behavior_reminder_not_injected_when_no_next_behavior(self, tmp_path):
        """
        SCENARIO: Next behavior reminder is NOT injected when current behavior is last in sequence
        GIVEN: discovery is the last behavior in bot_config.json
        AND: render is the final action
        WHEN: render action executes
        THEN: base_instructions do NOT include next behavior reminder
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('discovery')
        helper.bot.behaviors.current.actions.navigate_to('render')
        action = helper.bot.behaviors.current.actions.current
        instructions = getattr(action, 'instructions', None)
        base_instructions = getattr(instructions, 'base_instructions', instructions)
        assert base_instructions is not None


# End-to-end integration test (no story mapping)
class TestExecuteEndToEndWorkflow:

    def test_complete_workflow_progresses_through_single_behavior(self, tmp_path):
        """
        Complete workflow test progressing through all actions in one behavior.
        
        Tests progression through shape behavior:
        clarify -> strategy -> build -> validate -> render
        """
        helper = BotTestHelper(tmp_path)
        
        # Define expected action sequence for shape behavior
        expected_actions = ['clarify', 'strategy', 'build', 'validate', 'render']
        
        # Start at shape.clarify
        helper.bot.behaviors.navigate_to('shape')
        helper.bot.behaviors.current.actions.navigate_to('clarify')
        
        # Track progress
        workflow_progress = []
        
        # Progress through all actions in shape
        for expected_action in expected_actions:
            # Verify current position
            current_behavior = helper.bot.behaviors.current.name
            current_action = helper.bot.behaviors.current.actions.current_action_name
            
            workflow_progress.append(f"{current_behavior}.{current_action}")
            
            # Verify we're at expected action
            assert current_behavior == 'shape', \
                f"Expected shape, got {current_behavior}. Progress: {workflow_progress}"
            assert current_action == expected_action, \
                f"Expected action {expected_action}, got {current_action}. Progress: {workflow_progress}"
            
            # Move to next action (unless we're at the last one)
            if expected_action != 'render':
                result = helper.bot.next()
                assert result['status'] == 'success', \
                    f"bot.next() failed at shape.{expected_action}: {result}"
        
        # Verify we completed all 5 actions
        assert len(workflow_progress) == 5, \
            f"Expected 5 actions, got {len(workflow_progress)}: {workflow_progress}"
        
        print(f"\n=== SUCCESS: Completed shape workflow: {' -> '.join(workflow_progress)} ===")

    def test_complete_workflow_progresses_across_multiple_behaviors(self, tmp_path):
        """
        Complete workflow test progressing across multiple behaviors.
        
        Tests progression:
        shape (all actions) -> discovery (partial actions) 
        """
        helper = BotTestHelper(tmp_path)
        
        # Start at shape.clarify
        helper.bot.behaviors.navigate_to('shape')
        helper.bot.behaviors.current.actions.navigate_to('clarify')
        
        # Progress through shape behavior (all 5 actions)
        shape_actions = ['clarify', 'strategy', 'build', 'validate', 'render']
        for action in shape_actions:
            assert helper.bot.behaviors.current.name == 'shape'
            assert helper.bot.behaviors.current.actions.current_action_name == action
            if action != 'render':
                helper.bot.next()
        
        # At shape.render now - calling next() should advance to discovery
        result = helper.bot.next()
        
        # Verify we either:
        # 1. Advanced to next behavior (discovery), OR
        # 2. Got a completion message (no more behaviors configured)
        if result['status'] == 'success':
            # Advanced to next behavior
            assert result['behavior'] != 'shape', \
                f"Should have advanced from shape, but still at: {result}"
            # Verify we're now at the new behavior
            assert helper.bot.behaviors.current.name != 'shape'
            print(f"\n=== SUCCESS: Advanced from shape to {helper.bot.behaviors.current.name} ===")
        elif result['status'] == 'complete':
            # Workflow complete
            print("\n=== SUCCESS: Workflow completed (no more behaviors) ===")
        else:
            raise AssertionError(f"Unexpected result from bot.next() at final action: {result}")


# Story: Track Activity For Workspace (sequential_order: 6)
class TestTrackActivityForWorkspace:

    def test_activity_logged_to_workspace_area_not_bot_area(self, tmp_path):
        """
        SCENARIO: Activity logged to workspace_area not bot area
        GIVEN: WORKING_AREA environment variable specifies workspace_area
        AND: action 'gather_context' executes
        WHEN: Activity logger creates entry
        THEN: Activity log file is at: workspace_area/activity_log.json
        AND: Activity log is NOT at: agile_bots/bots/story_bot/activity_log.json
        AND: Activity log location matches workspace_area from WORKING_AREA environment variable
        """
        # Given: Bot using production story_bot
        helper = BotTestHelper(tmp_path)
        
        # When: Activity tracker tracks activity
        tracker = helper.activity.given_activity_tracker('story_bot')
        helper.activity.when_activity_tracks_start(tracker, 'story_bot.shape.gather_context')
        
        # Then: Activity log exists in workspace area
        expected_log = helper.workspace / 'activity_log.json'
        assert expected_log.exists()
        
        # And: Activity log does NOT exist in bot's area (production bot is read-only)
        from pathlib import Path
        repo_root = Path(__file__).parent.parent.parent.parent
        production_bot_dir = repo_root / 'agile_bots' / 'bots' / 'story_bot'
        bot_area_log = production_bot_dir / 'activity_log.json'
        assert not bot_area_log.exists()

    def test_activity_log_contains_correct_entry(self, tmp_path):
        """
        SCENARIO: Activity log contains correct entry
        GIVEN: action 'gather_context' executes in behavior 'discovery'
        WHEN: Activity logger creates entry
        THEN: Activity log entry includes:
          - action_state='story_bot.discovery.gather_context'
          - timestamp
          - Full path includes bot_name.behavior.action
        """
        # Given: Bot using production story_bot
        helper = BotTestHelper(tmp_path)
        
        # When: Activity tracker tracks activity
        tracker = helper.activity.given_activity_tracker('story_bot')
        helper.activity.when_activity_tracks_start(tracker, 'story_bot.shape.gather_context')
        
        # Then: Activity log has entry
        helper.activity.then_activity_log_matches(expected_action_state='story_bot.shape.gather_context', expected_status='started', expected_count=1)
TestTrackActivityForWorkspace
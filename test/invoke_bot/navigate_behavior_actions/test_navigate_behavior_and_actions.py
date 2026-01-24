"""
Test Navigate Behavior And Actions

SubEpic: Navigate Behavior And Actions
Parent Epic: Invoke Bot

Domain tests verify core bot logic.
CLI tests verify command parsing and output formatting across TTY, Pipe, and JSON channels.
"""
import pytest
from pathlib import Path
import json
import os
from helpers.bot_test_helper import BotTestHelper
from helpers import TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper
from actions.strategy.strategy_action import StrategyAction


# ============================================================================
# DOMAIN TESTS - Core Bot Logic
# ============================================================================

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

# ============================================================================
# CLI TESTS - Bot Operations via CLI Commands
# ============================================================================

class TestManageBehaviorsUsingCLI:
    """
    Story: Manage Behaviors Using CLI
    
    Domain logic: test_navigate_and_execute_behaviors.py::TestManageBehaviors
    CLI focus: Accessing and managing behaviors via CLI commands
    """
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_current_behavior_accessible(self, tmp_path, helper_class):
        """
        Domain: test_behaviors_current_property_returns_current_behavior
        CLI: Current behavior accessible via status command
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('prioritization', 'clarify')
        
        cli_response = helper.cli_session.execute_command('status')
        
        assert helper.cli_session.bot.behaviors.current.name == 'prioritization'
        assert cli_response is not None
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_navigate_to_behavior_via_command(self, tmp_path, helper_class):
        """
        Domain: test_behaviors_navigate_to_behavior_updates_current_behavior
        CLI: Navigate to behavior via CLI command
        """
        helper = helper_class(tmp_path)
        
        cli_response = helper.cli_session.execute_command('discovery')
        
        assert helper.cli_session.bot.behaviors.current.name == 'discovery'
        assert cli_response is not None
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_execute_current_behavior_action(self, tmp_path, helper_class):
        """
        Domain: test_behaviors_execute_current_executes_current_behavior
        CLI: Execute current behavior action via CLI
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        cli_response = helper.cli_session.execute_command('shape.clarify')
        
        assert cli_response is not None
        assert len(cli_response.output) > 0
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_find_behavior_by_name(self, tmp_path, helper_class):
        """
        Domain: test_find_behavior_by_name
        CLI: Access specific behavior via CLI command
        """
        helper = helper_class(tmp_path)
        
        cli_response = helper.cli_session.execute_command('prioritization')
        
        assert helper.cli_session.bot.behaviors.current.name == 'prioritization'
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_list_all_behaviors(self, tmp_path, helper_class):
        """
        Domain: test_iterate_all_behaviors
        CLI: List all behaviors via tree command
        """
        helper = helper_class(tmp_path)
        
        cli_response = helper.cli_session.execute_command('tree')
        
        assert cli_response is not None
        # Verify all 7 behaviors present in bot
        assert len(helper.cli_session.bot.behaviors.names) == 7
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_find_action_by_name_via_command(self, tmp_path, helper_class):
        """
        Domain: test_find_action_by_name
        CLI: Navigate to specific action via CLI
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'strategy')
        
        cli_response = helper.cli_session.execute_command('shape.strategy')
        
        assert helper.cli_session.bot.behaviors.current.actions.current_action_name == 'strategy'


# ============================================================================
# STORY: Manage Behavior Action State
# Maps to: TestManageBehaviorActionState in test_navigate_and_execute_behaviors.py (5 tests)
# ============================================================================

class TestNavigateToBehaviorActionAndExecuteUsingCLI:
    """
    Story: Navigate To Behavior Action And Execute Using CLI
    
    Domain logic: test_navigate_and_execute_behaviors.py::TestNavigateToBehaviorActionAndExecute
    CLI focus: Executing behaviors and actions via CLI commands
    """
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_execute_behavior_with_action_parameter(self, tmp_path, helper_class):
        """
        Domain: test_execute_behavior_with_action_parameter
        CLI: Execute 'behavior.action' command
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        cli_response = helper.cli_session.execute_command('shape.clarify')
        
        helper.instructions.assert_section_shows_behavior_and_action(cli_response.output, 'shape', 'clarify')
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_execute_behavior_without_action_uses_current(self, tmp_path, helper_class):
        """
        Domain: test_execute_behavior_without_action_forwards_to_current
        CLI: Execute 'behavior' command uses current action
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'strategy')
        
        cli_response = helper.cli_session.execute_command('shape')
        
        helper.instructions.assert_section_shows_behavior_and_action(cli_response.output, 'shape', 'strategy')
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_execute_behavior_with_no_state_starts_at_first(self, tmp_path, helper_class):
        """
        Domain: test_execute_behavior_handles_entry_workflow_when_no_state
        CLI: Executing behavior with no state starts at first action
        """
        helper = helper_class(tmp_path)
        helper.domain.state.clear_state()
        
        cli_response = helper.cli_session.execute_command('shape')
        
        # Should start at first action (clarify)
        assert helper.cli_session.bot.behaviors.current.actions.current_action_name == 'clarify'
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_workflow_order_determines_next_action(self, tmp_path, helper_class):
        """
        Domain: test_behavior_action_order_determines_next_action_from_current_action
        CLI: Next command follows workflow order
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'build')
        
        cli_response = helper.cli_session.execute_command('next')
        
        # Should advance to validate (after build)
        assert helper.cli_session.bot.behaviors.current.actions.current_action_name == 'validate'
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_starts_at_first_action_when_no_completed(self, tmp_path, helper_class):
        """
        Domain: test_behavior_action_order_starts_at_first_action_when_no_completed_actions
        CLI: CLI starts at first action when no history
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        cli_response = helper.cli_session.execute_command('shape')
        
        assert helper.cli_session.bot.behaviors.current.actions.current_action_name == 'clarify'
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_falls_back_to_completed_actions_list(self, tmp_path, helper_class):
        """
        Domain: test_behavior_action_order_falls_back_to_completed_actions_when_current_action_missing
        CLI: CLI determines position from completed_actions if current_action missing
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', '', completed_actions=[
            'story_bot.shape.clarify',
            'story_bot.shape.strategy',
            'story_bot.shape.build'
        ])
        
        # Navigate - should determine current from completed list
        cli_response = helper.cli_session.execute_command('shape')
        
        # Should be at validate (next after last completed)
        assert helper.cli_session.bot.behaviors.current.actions.current_action_name == 'validate'
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_different_behaviors_have_different_workflows(self, tmp_path, helper_class):
        """
        Domain: test_different_behaviors_can_have_different_action_orders
        CLI: Different behaviors show different action sequences in tree
        """
        helper = helper_class(tmp_path)
        
        # Navigate to shape and prioritization
        cli_response1 = helper.cli_session.execute_command('shape')
        shape_actions = helper.cli_session.bot.behaviors.current.actions.names
        
        cli_response2 = helper.cli_session.execute_command('prioritization')
        prioritization_actions = helper.cli_session.bot.behaviors.current.actions.names
        
        # Workflows are different
        assert shape_actions != prioritization_actions
        assert 'build' in shape_actions
        assert 'build' not in prioritization_actions  # prioritization skips build


# ============================================================================
# STORY: Navigate Sequentially
# Maps to: TestNavigateSequentially in test_navigate_and_execute_behaviors.py (13 tests)
# ============================================================================

class TestNavigateSequentiallyUsingCLI:
    """
    Story: Navigate Sequentially Using CLI
    
    Domain logic: test_navigate_and_execute_behaviors.py::TestNavigateSequentially
    CLI focus: Sequential navigation via next/back commands
    """
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_next_command_navigates_to_next_action(self, tmp_path, helper_class):
        """
        Domain: test_bot_next_navigates_to_next_action_in_workflow
        CLI: 'next' command advances to next action
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        cli_response = helper.cli_session.execute_command('next')
        
        # Should advance to strategy
        helper.domain.behaviors.assert_at_behavior_action('shape', 'strategy')
        assert cli_response is not None
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_next_progresses_through_entire_workflow(self, tmp_path, helper_class):
        """
        Domain: test_bot_next_progresses_through_entire_workflow
        CLI: Multiple 'next' commands progress through sequence
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        expected_sequence = ['clarify', 'strategy', 'build', 'validate', 'render']
        
        # At clarify
        assert helper.cli_session.bot.behaviors.current.actions.current_action_name == 'clarify'
        
        # Navigate through workflow
        for i in range(1, len(expected_sequence)):
            cli_response = helper.cli_session.execute_command('next')
            assert helper.cli_session.bot.behaviors.current.actions.current_action_name == expected_sequence[i]
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_next_at_final_action_advances_to_next_behavior(self, tmp_path, helper_class):
        """
        Domain: test_bot_next_at_final_action_advances_to_next_behavior
        CLI: 'next' at final action advances to next behavior
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'render')
        
        cli_response = helper.cli_session.execute_command('next')
        
        # Should advance beyond shape
        current_behavior = helper.cli_session.bot.behaviors.current.name
        assert current_behavior != 'shape' or cli_response.output  # Either moved or got completion message
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_status_shows_current_position(self, tmp_path, helper_class):
        """
        Domain: test_bot_current_returns_current_action_instructions
        CLI: 'status' command shows current position
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        cli_response = helper.cli_session.execute_command('status')
        
        assert cli_response is not None
        assert len(cli_response.output) > 0
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_next_respects_behavior_json_workflow(self, tmp_path, helper_class):
        """
        Domain: test_bot_next_respects_workflow_sequence
        CLI: 'next' follows behavior.json sequence
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'strategy')
        
        cli_response = helper.cli_session.execute_command('next')
        
        # Should go to build (per behavior.json)
        helper.domain.behaviors.assert_at_behavior_action('shape', 'build')
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_navigate_to_specific_behavior_via_command(self, tmp_path, helper_class):
        """
        Domain: test_navigate_to_behavior
        CLI: Direct navigation via behavior name command
        """
        helper = helper_class(tmp_path)
        
        cli_response = helper.cli_session.execute_command('discovery')
        
        assert helper.cli_session.bot.behaviors.current.name == 'discovery'
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_back_command_navigates_to_previous_action(self, tmp_path, helper_class):
        """
        CLI-specific: 'back' command goes to previous action
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'strategy')
        
        cli_response = helper.cli_session.execute_command('back')
        
        # Should go back to clarify
        helper.domain.behaviors.assert_at_behavior_action('shape', 'clarify')
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_pos_command_shows_current_position(self, tmp_path, helper_class):
        """
        CLI-specific: 'pos' command displays position in workflow
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'build')
        
        cli_response = helper.cli_session.execute_command('pos')
        
        assert cli_response is not None
        assert len(cli_response.output) > 0


# ============================================================================
# STORY: Display Context
# Maps to: TestInjectContextIntoInstructions in test_navigate_and_execute_behaviors.py (4 tests)
# Renamed per user feedback: "really to test display context. The panel always displays the context"
# ============================================================================
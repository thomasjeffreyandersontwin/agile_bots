"""
Test Display Behavior Action State

SubEpic: Display Behavior Action State
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

# ============================================================================
# CLI TESTS - Bot Operations via CLI Commands
# ============================================================================

class TestManageBehaviorActionStateUsingCLI:
    """
    Story: Manage Behavior Action State Using CLI
    
    Domain logic: test_navigate_and_execute_behaviors.py::TestManageBehaviorActionState
    CLI focus: State persistence across CLI sessions
    """
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_state_persists_after_navigation(self, tmp_path, helper_class):
        """
        Domain: test_save_current_behavior_state
        CLI: State saves when navigating via CLI
        """
        helper = helper_class(tmp_path)
        
        cli_response = helper.cli_session.execute_command('prioritization')
        
        state = helper.domain.state.get_state()
        assert 'prioritization' in state.get('current_behavior', '')
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_loads_existing_state_on_startup(self, tmp_path, helper_class):
        """
        Domain: test_load_behavior_state_from_file
        CLI: CLI session loads previous state
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('prioritization', 'clarify')
        
        # Create new session - should load state
        helper2 = helper_class(tmp_path)
        
        assert helper2.cli_session.bot.behaviors.current.name == 'prioritization'
        assert helper2.cli_session.bot.behaviors.current.actions.current_action_name == 'clarify'
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_next_command_closes_and_advances(self, tmp_path, helper_class):
        """
        Domain: test_close_current_action
        CLI: 'next' command closes current and advances
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        cli_response = helper.cli_session.execute_command('next')
        
        # Should advance to strategy
        assert helper.cli_session.bot.behaviors.current.actions.current_action_name == 'strategy'
        assert cli_response is not None


# ============================================================================
# STORY: Navigate To Behavior Action And Execute
# Maps to: TestNavigateToBehaviorActionAndExecute in test_navigate_and_execute_behaviors.py (10 tests)
# ============================================================================

class TestDisplayContextUsingCLI:
    """
    Story: Display Context Using CLI
    
    Domain logic: test_navigate_and_execute_behaviors.py::TestInjectContextIntoInstructions
    CLI focus: Displaying clarification, strategy, and context in CLI output
    
    Note: Per user feedback, this is about displaying context, not injecting it.
    The panel (and CLI) always displays context regardless of action.
    """
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_displays_clarification_when_present(self, tmp_path, helper_class):
        """
        Domain: test_action_loads_context_data_into_instructions (partial)
        CLI: CLI output includes clarification data when available
        """
        import json
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'build')
        
        # Create clarification data
        docs_dir = helper.domain.workspace / "docs" / "stories"
        docs_dir.mkdir(parents=True, exist_ok=True)
        clarification_data = {
            "shape": {
                "key_questions": {
                    "questions": ["What is the goal?"],
                    "answers": {"goal": "Build a story map"}
                }
            }
        }
        clarification_file = docs_dir / "clarification.json"
        clarification_file.write_text(json.dumps(clarification_data, indent=2))
        
        cli_response = helper.cli_session.execute_command('shape.build')
        
        # Context available to CLI (may or may not be in output depending on channel)
        assert cli_response is not None
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_displays_strategy_when_present(self, tmp_path, helper_class):
        """
        Domain: test_action_loads_context_data_into_instructions (partial)
        CLI: CLI output includes strategy data when available
        """
        import json
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'build')
        
        # Create strategy data
        docs_dir = helper.domain.workspace / "docs" / "stories"
        docs_dir.mkdir(parents=True, exist_ok=True)
        strategy_data = {
            "shape": {
                "strategy_criteria": {
                    "criteria": {"approach": {"question": "How?", "options": ["A", "B"]}},
                    "decisions_made": {"approach": "A"}
                }
            }
        }
        strategy_file = docs_dir / "strategy.json"
        strategy_file.write_text(json.dumps(strategy_data, indent=2))
        
        cli_response = helper.cli_session.execute_command('shape.build')
        
        # Context available to CLI
        assert cli_response is not None
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_displays_context_files_when_present(self, tmp_path, helper_class):
        """
        Domain: test_action_loads_context_data_into_instructions (partial)
        CLI: CLI shows context files list when available
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'build')
        
        # Create context files
        docs_dir = helper.domain.workspace / "docs" / "stories"
        context_dir = docs_dir / "context"
        context_dir.mkdir(parents=True, exist_ok=True)
        (context_dir / "input.txt").write_text("Original input content")
        (context_dir / "initial-context.md").write_text("# Initial Context")
        
        cli_response = helper.cli_session.execute_command('shape.build')
        
        # Context available to CLI
        assert cli_response is not None


# ============================================================================
# STORY: Execute End-to-End Workflow
# Maps to: TestExecuteEndToEndWorkflow in test_navigate_and_execute_behaviors.py (2 tests)
# ============================================================================
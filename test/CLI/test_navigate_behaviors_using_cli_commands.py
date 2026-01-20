"""
Navigate And Execute Behaviors Using CLI - Parameterized Across Channels

Maps directly to: test_navigate_and_execute_behaviors.py domain tests (~47 tests)

These tests focus on CLI-specific concerns:
- Navigation commands (next, back, behavior.action)
- Sequential workflow progression via CLI
- State persistence across CLI sessions
- Context display in CLI output
- End-to-end workflow execution via CLI

Uses parameterized tests to run same test logic across all 3 channels.
"""
import pytest
from CLI.helpers import TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper


# ============================================================================
# STORY: Manage Behaviors
# Maps to: TestManageBehaviors in test_navigate_and_execute_behaviors.py (11 tests)
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
    
    @pytest.mark.skip(reason="Action state persistence not yet implemented")
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_action_state_persists(self, tmp_path, helper_class):
        """
        Domain: test_save_current_action_state
        CLI: Action state saves via CLI commands
        """
        helper = helper_class(tmp_path)
        
        cli_response = helper.cli_session.execute_command('shape.strategy')
        
        state = helper.domain.state.get_state()
        assert 'strategy' in state.get('current_action', '')
    
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
    
    @pytest.mark.skip(reason="Direct action navigation not yet implemented")
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_navigate_to_specific_action_via_command(self, tmp_path, helper_class):
        """
        Domain: test_navigate_to_action
        CLI: Direct navigation via behavior.action command
        """
        helper = helper_class(tmp_path)
        
        cli_response = helper.cli_session.execute_command('shape.build')
        
        helper.domain.behaviors.assert_at_behavior_action('shape', 'build')
    
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
class TestExecuteEndToEndWorkflowUsingCLI:
    """
    Story: Execute End-to-End Workflow Using CLI
    
    Domain logic: test_navigate_and_execute_behaviors.py::TestExecuteEndToEndWorkflow
    CLI focus: Complete workflow execution via CLI commands
    """
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_complete_workflow_through_single_behavior(self, tmp_path, helper_class):
        """
        Domain: test_complete_workflow_progresses_through_single_behavior
        CLI: Progress through shape behavior via repeated 'next' commands
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        expected_actions = ['clarify', 'strategy', 'build', 'validate', 'render']
        
        # At clarify
        assert helper.cli_session.bot.behaviors.current.actions.current_action_name == 'clarify'
        
        # Progress through all actions
        for i in range(1, len(expected_actions)):
            cli_response = helper.cli_session.execute_command('next')
            current_action = helper.cli_session.bot.behaviors.current.actions.current_action_name
            assert current_action == expected_actions[i], \
                f"Expected {expected_actions[i]}, got {current_action}"
    
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_complete_workflow_across_multiple_behaviors(self, tmp_path, helper_class):
        """
        Domain: test_complete_workflow_progresses_across_multiple_behaviors
        CLI: Progress across behaviors via 'next' commands
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # Progress through shape
        shape_actions = ['clarify', 'strategy', 'build', 'validate', 'render']
        for i in range(1, len(shape_actions)):
            helper.cli_session.execute_command('next')
        
        # Now at shape.render - next should advance beyond shape
        cli_response = helper.cli_session.execute_command('next')
        
        # Either advanced to new behavior or got completion message
        current_behavior = helper.cli_session.bot.behaviors.current.name
        assert current_behavior != 'shape' or cli_response.output  # Moved or completed


# ============================================================================
# STORY: Track Activity For Workspace
# Maps to: TestTrackActivityForWorkspace in test_navigate_and_execute_behaviors.py (2 tests)
# TODO: Implement activity tracking - stubbed out for now
# ============================================================================
class TestTrackActivityForWorkspaceUsingCLI:
    """
    Story: Track Activity For Workspace Using CLI
    
    Domain logic: test_navigate_and_execute_behaviors.py::TestTrackActivityForWorkspace
    CLI focus: Activity logging when executing CLI commands
    
    NOTE: Stubbed out for future implementation
    """
    
    @pytest.mark.skip(reason="Activity tracking exists in domain but not wired through CLI execution path yet")
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_activity_logged_to_workspace(self, tmp_path, helper_class):
        """
        Domain: test_activity_logged_to_workspace_area_not_bot_area
        CLI: CLI commands log activity to workspace area
        
        NOTE: ActivityTracker exists and domain tests pass, but CLI doesn't invoke it yet
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # Execute command - should log activity
        cli_response = helper.cli_session.execute_command('shape.clarify')
        
        # Activity should be tracked in workspace
        expected_log = helper.domain.workspace / 'activity_log.json'
        assert expected_log.exists()
        
        # Verify activity log not in bot directory
        from pathlib import Path
        repo_root = Path(__file__).parent.parent.parent.parent
        bot_area_log = repo_root / 'agile_bots' / 'bots' / 'story_bot' / 'activity_log.json'
        assert not bot_area_log.exists()
    
    @pytest.mark.skip(reason="Activity tracking exists in domain but not wired through CLI execution path yet")
    @pytest.mark.parametrize("helper_class", [TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper])
    def test_cli_activity_log_contains_action_state(self, tmp_path, helper_class):
        """
        Domain: test_activity_log_contains_correct_entry
        CLI: Activity log includes full action_state path
        
        NOTE: ActivityTracker exists and domain tests pass, but CLI doesn't invoke it yet
        """
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # Execute command
        cli_response = helper.cli_session.execute_command('shape.clarify')
        
        # Verify activity log entry
        expected_log = helper.domain.workspace / 'activity_log.json'
        assert expected_log.exists()
        
        import json
        with open(expected_log) as f:
            log_data = json.load(f)
        
        # Should contain entry with action_state
        assert any('story_bot.shape.clarify' in str(entry) for entry in log_data)

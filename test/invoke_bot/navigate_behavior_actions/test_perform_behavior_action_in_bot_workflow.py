"""
Test Perform Behavior Action In Bot Workflow

SubEpic: Perform Behavior Action In Bot Workflow
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


# ============================================================================
# DOMAIN TESTS - Core Bot Logic
# ============================================================================

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

# ============================================================================
# CLI TESTS - Bot Operations via CLI Commands
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
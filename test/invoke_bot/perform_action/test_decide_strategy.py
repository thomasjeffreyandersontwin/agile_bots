"""
Test Decide Strategy

SubEpic: Decide Strategy
Parent Epic: Invoke Bot > Perform Action

Domain tests verify core action logic.
CLI tests verify command parsing and output formatting across TTY, Pipe, and JSON channels.
"""
import pytest
from pathlib import Path
import json
from helpers.bot_test_helper import BotTestHelper
from helpers import TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper
from actions.build.build_action import BuildStoryGraphAction
from actions.render.render_action import RenderOutputAction
from actions.action_context import (
    ClarifyActionContext,
    StrategyActionContext,
    ValidateActionContext,
    ScopeActionContext
)


# ============================================================================
# DOMAIN TESTS - Core Action Logic
# ============================================================================

class TestDecideStrategy:

    def test_action_injects_decision_criteria_and_assumptions(self, tmp_path):
        """
        SCENARIO: Action Injects Decision Criteria And Assumptions
        GIVEN: Production story_bot with shape behavior (has guardrails)
        WHEN: Action injects strategy criteria and assumptions
        THEN: Instructions contain all required strategy fields
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action_obj = helper.bot.behaviors.current.actions.find_by_name('strategy')
        
        instructions = action_obj.do_execute()
        
        helper.strategy.assert_strategy_instructions(instructions)

    def test_save_strategy_data_when_parameters_provided(self, tmp_path):
        """
        SCENARIO: Save strategy data when parameters are provided
        GIVEN: Production story_bot strategy action
        WHEN: do_execute is called with decisions_made and assumptions_made
        THEN: strategy.json file is created in docs/stories/ folder
        AND: file contains behavior section with decisions_made and assumptions_made
        """
        # Given: Production story_bot strategy action
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('strategy')
        
        # When: Action executes with parameters
        decisions_made = {
            'drill_down': 'Dig deep on system interactions',
            'flow_scope': 'End-to-end user-system behavior'
        }
        assumptions_made = [
            'Focus on user flow over internal systems',
            'Cover the end-to-end scenario'
        ]
        context = StrategyActionContext(
            decisions_made=decisions_made,
            assumptions_made=assumptions_made
        )
        action.do_execute(context)
        
        # Then: strategy.json file exists and contains expected data
        helper.strategy.assert_strategy_file_exists()
        helper.strategy.assert_strategy_contains_behavior(
            'shape',
            expected_decisions=decisions_made,
            expected_assumptions=assumptions_made
        )

    def test_preserve_existing_strategy_data_when_saving(self, tmp_path):
        """
        SCENARIO: Preserve existing strategy data when saving
        GIVEN: strategy.json already exists with data for 'discovery' behavior
        AND: Production story_bot strategy action for 'shape' behavior
        WHEN: do_execute is called with parameters
        THEN: strategy.json contains both 'discovery' and 'shape' sections
        AND: existing 'discovery' data is preserved
        """
        # Given: Existing strategy.json with discovery data (actual format)
        helper = BotTestHelper(tmp_path)
        existing_data = {
            'discovery': {
                'decisions': {'scope': 'Component level'},
                'assumptions': ['Stories follow user story format']
            }
        }
        helper.strategy.given_existing_strategy_data(existing_data)
        
        # Setup production strategy action for shape
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('strategy')
        
        # When: Action executes with parameters
        context = StrategyActionContext(
            decisions_made={
                'drill_down': 'Dig deep on system interactions',
                'flow_scope': 'End-to-end user-system behavior'
            },
            assumptions_made=[
                'Focus on user flow over internal systems',
                'Cover the end-to-end scenario'
            ]
        )
        action.do_execute(context)
        
        # Then: Both behaviors' data are preserved
        helper.strategy.assert_strategy_contains_behavior(
            'discovery',
            expected_decisions={'scope': 'Component level'},
            expected_assumptions=['Stories follow user story format']
        )
        helper.strategy.assert_strategy_contains_behavior(
            'shape',
            expected_decisions={'drill_down': 'Dig deep on system interactions', 'flow_scope': 'End-to-end user-system behavior'},
            expected_assumptions=['Focus on user flow over internal systems', 'Cover the end-to-end scenario']
        )

    def test_skip_saving_when_no_strategy_parameters_provided(self, tmp_path):
        """
        SCENARIO: Skip saving when no strategy parameters are provided
        GIVEN: Production story_bot strategy action
        WHEN: do_execute is called with empty parameters
        THEN: strategy.json file is not created
        """
        # Given: Production story_bot strategy action
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('strategy')
        
        # When: Action executes with empty parameters
        context = StrategyActionContext(decisions_made=None, assumptions_made=None)
        action.do_execute(context)
        
        # Then: strategy.json file is not created
        helper.strategy.assert_strategy_file_not_exists()

# ============================================================================
# STORY: Render Output
# ============================================================================

# ============================================================================
# CLI TESTS - Action Execution via CLI Commands
# ============================================================================

class TestDecideStrategyUsingCLI:
    """
    Story: Decide Strategy Using CLI
    
    Domain logic: test_perform_action.py::TestDecideStrategy
    CLI focus: Execute strategy action and verify criteria/assumptions in output
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_strategy_action_shows_criteria_and_assumptions(self, tmp_path, helper_class):
        """
        SCENARIO: Strategy action shows criteria and assumptions in CLI output
        GIVEN: CLI is at shape.strategy
        WHEN: user navigates to shape.strategy
        THEN: CLI output contains decision criteria and assumptions
        
        Domain: test_action_injects_decision_criteria_and_assumptions
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'strategy')
        
        # When
        cli_response = helper.cli_session.execute_command('shape.strategy')
        
        # Then
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'strategy')
        # Strategy content should be in output
        output_lower = cli_response.output.lower()
        assert 'strateg' in output_lower or 'decision' in output_lower or 'assumption' in output_lower


# ============================================================================
# STORY: Render Output
# Maps to: TestRenderOutput in test_perform_action.py
# ============================================================================
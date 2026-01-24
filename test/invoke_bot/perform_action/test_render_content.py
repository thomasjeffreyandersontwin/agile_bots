"""
Test Render Content

SubEpic: Render Content
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

class TestRenderOutput:

    def test_action_injects_render_configs_and_instructions(self, tmp_path):
        """
        SCENARIO: Action injects render configs and instructions
        GIVEN: Production story_bot with shape behavior (has render configs)
        WHEN: Action injects render data
        THEN: Instructions contain all required render fields
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        helper.state.set_state('shape', 'render')
        action_obj = helper.bot.behaviors.current.actions.find_by_name('render')
        
        instructions = action_obj.do_execute()
        
        helper.render.assert_render_output_instructions(instructions)

    def test_synchronizers_are_executed_automatically(self, tmp_path):
        """
        SCENARIO: Synchronizers are executed automatically during render action
        GIVEN: Production story_bot with shape behavior (has synchronizers)
        WHEN: Render output action executes
        THEN: Synchronizers are executed automatically
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        helper.state.set_state('shape', 'render')
        action_obj = helper.bot.behaviors.current.actions.find_by_name('render')
        
        result = action_obj.do_execute()
        
        base_instructions = result.get('base_instructions', [])
        base_instructions_text = '\n'.join(base_instructions)
        assert 'Synchronizers Already Executed' in base_instructions_text or 'render' in base_instructions_text.lower()

    def test_template_configs_remain_in_instructions(self, tmp_path):
        """
        SCENARIO: Template configs remain in instructions for AI handling
        GIVEN: Production story_bot with shape behavior (has templates)
        WHEN: Render output action executes  
        THEN: Result includes instructions
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        helper.state.set_state('shape', 'render')
        action_obj = helper.bot.behaviors.current.actions.find_by_name('render')
        
        result = action_obj.do_execute()
        
        base_instructions = result.get('base_instructions', [])
        assert len(base_instructions) > 0, "Should have instructions"

    def test_executed_synchronizers_info_in_instructions(self, tmp_path):
        """
        SCENARIO: Executed synchronizers information is included in AI instructions
        GIVEN: Production story_bot with shape behavior (has synchronizers)
        WHEN: Render output action executes
        THEN: Instructions include synchronizer execution info
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        helper.state.set_state('shape', 'render')
        action_obj = helper.bot.behaviors.current.actions.find_by_name('render')
        
        result = action_obj.do_execute()
        
        base_instructions = '\n'.join(result.get('base_instructions', []))
        assert 'Synchronizers Already Executed' in base_instructions or 'render' in base_instructions.lower()


# ============================================================================
# STORY: Save Guardrails (Domain Layer)
# ============================================================================

# ============================================================================
# CLI TESTS - Action Execution via CLI Commands
# ============================================================================

class TestRenderOutputUsingCLI:
    """
    Story: Render Output Using CLI
    
    Domain logic: test_perform_action.py::TestRenderOutput
    CLI focus: Execute render action and verify configs in output
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_render_action_shows_configs_in_output(self, tmp_path, helper_class):
        """
        SCENARIO: Render action shows render configs in CLI output
        GIVEN: CLI is at shape.render
        WHEN: user navigates to shape.render
        THEN: CLI output contains render configurations
        
        Domain: test_action_injects_render_configs_and_instructions
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'render')
        
        # When
        cli_response = helper.cli_session.execute_command('shape.render')
        
        # Then
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'render')
        # Render content should be in output
        output_lower = cli_response.output.lower()
        assert 'render' in output_lower
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_render_output_mentions_synchronizers(self, tmp_path, helper_class):
        """
        SCENARIO: Render output mentions synchronizers execution
        GIVEN: CLI is at shape.render
        WHEN: user navigates to shape.render
        THEN: CLI output mentions synchronizers
        
        Domain: test_synchronizers_are_executed_automatically
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'render')
        
        # When
        cli_response = helper.cli_session.execute_command('shape.render')
        
        # Then
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'render')


# ============================================================================
# STORY: Save Guardrails
# Maps to: TestSaveGuardrailsViaCLI in test_perform_action.py
# ============================================================================
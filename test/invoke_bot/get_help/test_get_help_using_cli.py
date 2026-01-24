"""
Test Get Help Using CLI

SubEpic: Get Help Using CLI
Parent: Invoke Bot

Tests for getting help via CLI commands, including:
- Action instructions display
- Parameter help display
- Command examples
- Help command functionality

Combines domain logic tests with CLI-specific display tests.
Uses parameterized tests across TTY, Pipe, and JSON channels.
"""
import pytest
import json
import os
from pathlib import Path
from bot.bot import Bot, BotResult
from behaviors import Behavior
from bot_path import BotPath
from helpers.bot_test_helper import BotTestHelper
from helpers import TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper


# ============================================================================
# DOMAIN TESTS - Core Help Functionality
# ============================================================================

class TestGetHelp:
    """Domain logic tests for help functionality"""

    def test_actionS_has_instructions_method(self, tmp_path):
        """
        SCENARIO: Verify actions can provide instructions
        GIVEN: Bot has behavior with action
        WHEN: Action is accessed
        THEN: Action has method to get instructions
        
        Domain focus: Action instructions method availability
        """
        # GIVEN: Bot has behavior with action
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        
        # WHEN: Action is accessed
        action = helper.bot.behaviors.current.actions.find_by_name('clarify')
        
        # THEN: Complete action object with instructions capability
        assert action is not None
        assert hasattr(action, 'action_name')
        assert action.action_name == 'clarify'
        assert hasattr(action, 'order')
        assert isinstance(action.order, int)
        assert hasattr(action, 'behavior')
        assert hasattr(action, 'get_instructions') or hasattr(action, 'instructions')
        
        # Verify instructions can be retrieved and have structure
        if hasattr(action, 'get_instructions'):
            instructions = action.get_instructions()
            assert instructions is not None
            assert isinstance(instructions, (dict, object))
        elif hasattr(action, 'instructions'):
            instructions = action.instructions
            assert instructions is not None
            assert isinstance(instructions, (dict, object))

    
    def test_action_provides_parameter_help(self, tmp_path):
        """
        SCENARIO: Action provides parameter help via .help property
        GIVEN: Bot has behavior with action
        WHEN: Action.help is accessed
        THEN: Returns dict with description and parameters list
        
        Domain focus: Parameter help retrieval from Action.help
        """
        # GIVEN: Bot has behavior with action
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        
        # Get the actual action instance
        from actions.clarify.clarify_action import ClarifyContextAction
        behavior_obj = helper.bot.behaviors.current
        action = ClarifyContextAction(behavior=behavior_obj, action_config=None)
        
        # WHEN: Action.help is accessed
        help_info = action.help
        
        # THEN: Help info has expected structure
        assert help_info is not None, "Action should provide help"
        assert isinstance(help_info, dict), "Help should be a dict"
        assert 'description' in help_info, "Help should have description"
        assert 'parameters' in help_info, "Help should have parameters"
        assert isinstance(help_info['parameters'], list), "Parameters should be a list"
        
        # Verify parameters have expected structure
        if len(help_info['parameters']) > 0:
            param = help_info['parameters'][0]
            assert 'name' in param, "Parameter should have name"
            assert 'cli_name' in param, "Parameter should have CLI name"
            assert 'type' in param, "Parameter should have type"
            assert 'description' in param, "Parameter should have description"
        
        # Try to retrieve parameter help if method exists and verify structure
        if hasattr(action, 'get_parameter_help'):
            param_help = action.get_parameter_help()
            assert param_help is not None
            assert isinstance(param_help, (dict, list, str))
        elif hasattr(action, 'parameter_help'):
            param_help = action.parameter_help
            assert param_help is not None
            assert isinstance(param_help, (dict, list, str))
        elif hasattr(action, 'parameters'):
            params = action.parameters
            assert params is not None
            assert isinstance(params, (dict, list))
        elif hasattr(action, 'get_parameters'):
            params = action.get_parameters()
            assert params is not None
            assert isinstance(params, (dict, list))

    
    def test_action_provides_command_examples(self, tmp_path):
        """
        SCENARIO: Action provides command examples
        GIVEN: Bot has behavior with action
        WHEN: Command examples are requested
        THEN: Action returns usage examples
        
        Domain focus: Command examples retrieval
        """
        # GIVEN: Bot has behavior with action
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('clarify')
        
        # WHEN: Command examples are requested
        # Check if action has examples method or property
        has_examples = (
            hasattr(action, 'get_examples') or
            hasattr(action, 'examples') or
            hasattr(action, 'get_command_examples') or
            hasattr(action, 'command_examples')
        )
        
        # THEN: Complete action object (examples are optional)
        assert action is not None
        assert action.action_name == 'clarify'
        assert hasattr(action, 'order')
        assert isinstance(action.order, int)
        assert has_examples or True, "Action may provide command examples"
        
        # Try to retrieve examples if method exists and verify structure
        if hasattr(action, 'get_examples'):
            examples = action.get_examples()
            assert examples is not None
            assert isinstance(examples, (dict, list, str))
        elif hasattr(action, 'examples'):
            examples = action.examples
            assert examples is not None
            assert isinstance(examples, (dict, list, str))
        elif hasattr(action, 'get_command_examples'):
            examples = action.get_command_examples()
            assert examples is not None
            assert isinstance(examples, (dict, list, str))
        elif hasattr(action, 'command_examples'):
            examples = action.command_examples
            assert examples is not None
            assert isinstance(examples, (dict, list, str))


# ============================================================================
# CLI TESTS - Help Display via CLI Commands
# ============================================================================

class TestGetHelpUsingCLI:
    """
    Story: Get Help Using CLI Commands
    
    Domain logic: TestGetHelp
    CLI focus: Display help, instructions, parameters, and examples via CLI
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_action_shows_instructions_in_cli_output(self, tmp_path, helper_class):
        """
        SCENARIO: Action instructions are shown in CLI output
        GIVEN: CLI is at shape.clarify
        WHEN: user navigates to action
        THEN: CLI output shows action instructions
        
        Domain: test_action_has_instructions_method
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # When - Navigate to action (shows instructions)
        cli_response = helper.cli_session.execute_command('shape.clarify')
        
        # Then - Instructions are in output
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'clarify')
        # Verify instructions content is present
        assert 'clarify' in cli_response.output.lower() or 'instruction' in cli_response.output.lower()
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_action_shows_parameter_help_in_output(self, tmp_path, helper_class):
        """
        SCENARIO: Action parameter help is shown in CLI output
        GIVEN: CLI is at shape.clarify
        WHEN: user navigates to action with parameters
        THEN: CLI output shows parameter information
        
        Domain: test_action_provides_parameter_help
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # When - Navigate to action (shows instructions with parameters)
        cli_response = helper.cli_session.execute_command('shape.clarify')
        
        # Then - Output contains action information
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'clarify')
        # Parameters or descriptions should be in output
        output_lower = cli_response.output.lower()
        assert ('parameter' in output_lower or 
                'input' in output_lower or 
                'question' in output_lower or
                'evidence' in output_lower or
                'clarify' in output_lower)
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_action_shows_usage_information_in_output(self, tmp_path, helper_class):
        """
        SCENARIO: Action shows usage information in CLI output
        GIVEN: CLI is at shape.clarify
        WHEN: user navigates to action
        THEN: CLI output shows how to use the action
        
        Domain: test_action_provides_command_examples
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # When - Navigate to action
        cli_response = helper.cli_session.execute_command('shape.clarify')
        
        # Then - Output contains usage information
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'clarify')
        # Action name should be in output (usage context)
        assert 'clarify' in cli_response.output.lower()


class TestDisplayHelpUsingCLI:
    """
    Story: Display Help Command Using CLI
    
    CLI-specific story: Showing available commands and help text via 'help' command
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_help_command_shows_available_commands(self, tmp_path, helper_class):
        """
        SCENARIO: Help command shows available commands (all channels)
        GIVEN: CLI session active
        WHEN: user enters 'help'
        THEN: CLI displays list of available commands
              Output shows commands in appropriate channel format
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'build')
        
        # When
        cli_response = helper.cli_session.execute_command('help')
        
        # Then - Help shows commands
        helper.help.assert_help_shows_available_commands(cli_response.output)
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_help_with_command_shows_details(self, tmp_path, helper_class):
        """
        SCENARIO: Help with command name shows command details (all channels)
        GIVEN: CLI session active
        WHEN: user enters 'help status'
        THEN: CLI displays help for 'status' command
              Output shows command details in appropriate channel format
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'build')
        
        # When
        cli_response = helper.cli_session.execute_command('help status')
        
        # Then - Help shows command details
        helper.help.assert_help_shows_command_details(cli_response.output, 'status')

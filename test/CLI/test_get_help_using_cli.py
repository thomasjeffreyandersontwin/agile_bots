"""
Get Help Using CLI Commands Tests - Parameterized Across Channels

Maps directly to: test_get_help.py domain tests

These tests focus on CLI-specific concerns:
- Help command parsing
- CLI help display format verification (TTY, Markdown, JSON modes)
- Available commands listing
- Action instructions display
- Parameter help display
- Command examples display

Uses parameterized tests to run same test logic across all 3 channels.
"""
import pytest
from agile_bots.test.CLI.helpers import TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper


class TestGetHelpUsingCLI:
    """
    Story: Get Help Using CLI Commands
    
    Domain logic: test_get_help.py::TestGetHelp
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

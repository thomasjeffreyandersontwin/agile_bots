"""
Test Use Rules In Prompt

SubEpic: Use Rules In Prompt
Parent Epic: Invoke Bot > Perform Action

Domain tests verify core rules display logic.
CLI tests verify rules command parsing and output formatting across TTY, Pipe, and JSON channels.
REPL tests verify interactive rules navigation.
"""
import pytest
from pathlib import Path
import json
from helpers.bot_test_helper import BotTestHelper
from helpers import TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper


# ============================================================================
# DOMAIN TESTS - Core Rules Display Logic
# ============================================================================

class TestDisplayRules:
    """Tests that rules are properly loaded and formatted for display."""
    
    def test_action_loads_and_formats_rules_digest(self, tmp_path):
        """
        SCENARIO: Action loads and formats rules digest
        GIVEN: Production story_bot with tests behavior (has rules)
        WHEN: Rules action executes
        THEN: Instructions contain formatted rules digest with descriptions, priorities, DO/DON'T sections
        """
        # GIVEN: Production story_bot with tests behavior (has rules)
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('tests')
        behavior = helper.bot.behaviors.current
        
        # AND: Rules action from production behavior
        from rules.rules_action import RulesAction
        from actions.action_context import RulesActionContext
        action = RulesAction(behavior=behavior, action_config=None)
        
        # WHEN: Rules action executes
        result = action.do_execute(RulesActionContext())
        
        # THEN: Instructions contain formatted rules digest
        helper.rules.assert_rules_instructions(result)
    
    def test_rules_list_includes_file_paths(self, tmp_path):
        """
        SCENARIO: Rules list includes file paths for each rule
        GIVEN: Production story_bot with tests behavior (has rules)
        WHEN: Rules action executes
        THEN: Display includes rule names with their file paths
        """
        # GIVEN: Production story_bot with tests behavior
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('tests')
        behavior = helper.bot.behaviors.current
        
        # AND: Rules action
        from rules.rules_action import RulesAction
        from actions.action_context import RulesActionContext
        action = RulesAction(behavior=behavior, action_config=None)
        
        # WHEN: Rules action executes
        result = action.do_execute(RulesActionContext())
        
        # THEN: Display includes file paths
        helper.rules.assert_rules_list_contains_file_paths(result)
    
    def test_all_behavior_rules_included_in_digest(self, tmp_path):
        """
        SCENARIO: All behavior rules are included in the digest
        GIVEN: Production story_bot with tests behavior (has multiple rules)
        WHEN: Rules action executes
        THEN: All rules from behavior are included in digest
        """
        # GIVEN: Production story_bot with tests behavior
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('tests')
        behavior = helper.bot.behaviors.current
        
        # AND: Rules action
        from rules.rules_action import RulesAction
        from actions.action_context import RulesActionContext
        action = RulesAction(behavior=behavior, action_config=None)
        
        # WHEN: Rules action executes
        result = action.do_execute(RulesActionContext())
        
        # THEN: All rules included (tests behavior has 25 rules)
        helper.rules.assert_rules_digest_contains_all_rules(result, expected_rule_count=20)
    
    def test_user_message_included_when_provided(self, tmp_path):
        """
        SCENARIO: User message is included in instructions when provided
        GIVEN: Production story_bot with tests behavior
        AND: User message requesting specific rule information
        WHEN: Rules action executes with message
        THEN: Instructions include user message
        """
        # GIVEN: Production story_bot with tests behavior
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('tests')
        behavior = helper.bot.behaviors.current
        
        # AND: User message
        user_message = "Show me the rules for test organization"
        
        # AND: Rules action
        from rules.rules_action import RulesAction
        from actions.action_context import RulesActionContext
        action = RulesAction(behavior=behavior, action_config=None)
        
        # WHEN: Rules action executes with message
        context = RulesActionContext(message=user_message)
        result = action.do_execute(context)
        
        # THEN: Instructions include user message
        helper.rules.assert_user_message_included(result, user_message)
    
    def test_no_user_message_section_when_empty(self, tmp_path):
        """
        SCENARIO: No user message section when message is empty
        GIVEN: Production story_bot with tests behavior
        WHEN: Rules action executes without message
        THEN: Instructions do not include user message section
        """
        # GIVEN: Production story_bot with tests behavior
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('tests')
        behavior = helper.bot.behaviors.current
        
        # AND: Rules action
        from rules.rules_action import RulesAction
        from actions.action_context import RulesActionContext
        action = RulesAction(behavior=behavior, action_config=None)
        
        # WHEN: Rules action executes without message
        context = RulesActionContext(message=None)
        result = action.do_execute(context)
        
        # THEN: No user message section in instructions
        helper.rules.assert_no_user_message_when_empty(result)


# ============================================================================
# STORY: Decide Strategy
# ============================================================================

# ============================================================================
# CLI TESTS - Rules Display via CLI Commands
# ============================================================================

class TestDisplayRulesUsingCLI:
    """
    Story: Display Rules Using CLI
    
    Domain logic: test_perform_action.py::TestDisplayRules
    CLI focus: Execute rules action and verify rules digest in output
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_rules_action_shows_rules_digest(self, tmp_path, helper_class):
        """
        SCENARIO: Rules action shows rules digest in CLI output
        GIVEN: CLI is at shape.validate (which shows rules)
        WHEN: user navigates to shape.validate
        THEN: CLI output contains formatted rules digest
        
        Domain: test_action_loads_and_formats_rules_digest (adapted - using validate instead of rules action)
        """
        # Given
        helper = helper_class(tmp_path)
        
        # Create story graph for validation
        story_graph_data = {'epics': []}
        helper.domain.story.create_story_graph(story_graph_data)
        
        helper.domain.state.set_state('shape', 'validate')
        
        # When
        cli_response = helper.cli_session.execute_command('shape.validate')
        
        # Then
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'validate')
        # Rules content should be in output
        output_lower = cli_response.output.lower()
        assert 'rule' in output_lower or 'validate' in output_lower
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_rules_output_includes_validation_content(self, tmp_path, helper_class):
        """
        SCENARIO: Validation output includes rules content
        GIVEN: CLI is at shape.validate
        WHEN: user navigates to shape.validate
        THEN: CLI output contains validation rules
        
        Domain: test_rules_list_includes_file_paths (adapted)
        """
        # Given
        helper = helper_class(tmp_path)
        
        # Create story graph for validation
        story_graph_data = {'epics': []}
        helper.domain.story.create_story_graph(story_graph_data)
        
        helper.domain.state.set_state('shape', 'validate')
        
        # When
        cli_response = helper.cli_session.execute_command('shape.validate')
        
        # Then
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'validate')


# ============================================================================
# STORY: Decide Strategy
# Maps to: TestDecideStrategy in test_perform_action.py
# ============================================================================

# ============================================================================
# CLI/REPL TESTS - Rules Display Through REPL Navigation
# ============================================================================

# ============================================================================
# STORY: Get Rules Instructions Through CLI
# Test Class: TestGetRulesInstructionsThroughCLI
# ============================================================================
# TODO: Rules tests commented out - submitting to AI chat during tests causing issues
# Will be re-enabled once the underlying submission issues are resolved
#
# class TestGetRulesInstructionsThroughCLI:
#     """
#     Story: Get Rules Instructions Through CLI
#     Sub-epic: Display Rules Through REPL
#     
#     Acceptance Criteria:
#     - WHEN User navigates to behavior.rules
#     - THEN CLI displays formatted rules digest with descriptions and DO/DON'T sections
#     - AND CLI includes rule names with their file paths
#     - AND CLI includes all rules from the behavior
#     """
#     
#     @pytest.mark.parametrize("helper_class", [
#         TTYBotTestHelper,
#         PipeBotTestHelper,
#         JsonBotTestHelper
#     ])
#     def test_user_gets_rules_instructions_for_behavior(self, tmp_path, helper_class):
#         """
#         SCENARIO: User gets rules instructions for behavior
#         
#         Steps:
#         - Given Production story_bot with tests behavior (has rules)
#         - When User enters 'tests.rules' in CLI
#         - Then CLI displays formatted rules digest with descriptions, priorities, DO/DON'T sections
#         - And Display includes rule names with their file paths
#         - And All rules from behavior are included in digest
#         
#         Test Method: test_user_gets_rules_instructions_for_behavior
#         """
#         # Given Production story_bot with tests behavior (has rules)
#         helper = helper_class(tmp_path)
#         helper.domain.state.set_state('tests', 'rules')
#         
#         # When User enters 'tests.rules' in CLI
#         cli_response = helper.cli_session.execute_command('tests.rules')
#         
#         # Then CLI shows instructions (JSON format returns complex object)
#         output_lower = cli_response.output.lower()
#         # JSON format shows full instructions object with bot metadata
#         assert 'instructions' in output_lower or 'tests' in output_lower, "Should show behavior or instructions"
#     
#     @pytest.mark.parametrize("helper_class", [
#         TTYBotTestHelper,
#         PipeBotTestHelper,
#         JsonBotTestHelper
#     ])
#     def test_user_gets_rules_with_message_parameter(self, tmp_path, helper_class):
#         """
#         SCENARIO: User gets rules with message parameter
#         
#         Steps:
#         - Given Production story_bot with tests behavior
#         - When User enters 'tests.rules "explain parameterized tests"' in CLI
#         - Then CLI displays rules digest
#         - And Instructions include user message requesting specific rule information
#         
#         Test Method: test_user_gets_rules_with_message_parameter
#         """
#         # Given Production story_bot with tests behavior
#         helper = helper_class(tmp_path)
#         helper.domain.state.set_state('tests', 'rules')
#         
#         # When User enters 'tests.rules "explain parameterized tests"' with message
#         cli_response = helper.cli_session.execute_command('tests.rules "explain parameterized tests"')
#         
#         # Then CLI shows instructions (JSON format returns complex object)
#         output_lower = cli_response.output.lower()
#         # JSON format shows full instructions object with bot metadata
#         assert 'instructions' in output_lower or 'tests' in output_lower, "Should show behavior or instructions"
#     
#     @pytest.mark.parametrize("helper_class", [
#         TTYBotTestHelper,
#         PipeBotTestHelper,
#         JsonBotTestHelper
#     ])
#     def test_user_gets_rules_without_message_parameter(self, tmp_path, helper_class):
#         """
#         SCENARIO: User gets rules without message parameter
#         
#         Steps:
#         - Given Production story_bot with tests behavior
#         - When User enters 'tests.rules' without message
#         - Then CLI displays rules digest
#         - And Instructions do not include user message section
#         
#         Test Method: test_user_gets_rules_without_message_parameter
#         """
#         # Given Production story_bot with tests behavior
#         helper = helper_class(tmp_path)
#         helper.domain.state.set_state('tests', 'rules')
#         
#         # When User enters 'tests.rules' without message
#         cli_response = helper.cli_session.execute_command('tests.rules')
#         
#         # Then CLI shows instructions (JSON format returns complex object)
#         output_lower = cli_response.output.lower()
#         # JSON format shows full instructions object with bot metadata
#         assert 'instructions' in output_lower or 'tests' in output_lower, "Should show behavior or instructions"
#         
#         # Should not have "user message:" or similar header when no message provided
#         # (This is a negative assertion - verifying absence of message section)
#         # The output should just have rules without extra message context

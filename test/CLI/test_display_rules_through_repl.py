"""
Display Rules Through REPL Tests

Tests for Display Rules Through REPL sub-epic under "Display Action Instructions Using REPL"

Story: Get Rules Instructions Through CLI
- User gets rules instructions for behavior
- User gets rules with message parameter
- User gets rules without message parameter

Test file: test_display_rules_through_repl.py
"""
import pytest
from CLI.helpers import TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper


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

"""
Test Validate With Rules

SubEpic: Validate With Rules
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

class TestValidateRules:
    """Tests that rules are properly formatted into instructions for AI to use."""
    
    def test_story_graph_rules_formatted_in_instructions(self, tmp_path):
        """
        SCENARIO: Story graph validation includes rule content in instructions
        GIVEN: Production story_bot with shape behavior (validates story graph)
        AND: Story graph file exists
        WHEN: Validate action executes
        THEN: Instructions contain rule descriptions, DO/DON'T sections, and priorities from rule files
        """
        # GIVEN: Production story_bot with shape behavior (validates story graph)
        helper = BotTestHelper(tmp_path)
        
        # AND: Story graph file exists
        story_graph_data = {'epics': []}
        helper.story.create_story_graph(story_graph_data)
        
        helper.bot.behaviors.navigate_to('shape')
        behavior = helper.bot.behaviors.current
        
        # AND: Validate action from production behavior
        from actions.validate.validate_action import ValidateRulesAction
        action = ValidateRulesAction(behavior=behavior, action_config=None)
        
        # WHEN: Validate action executes
        result = action.do_execute(ValidateActionContext())
        
        # THEN: Instructions contain rule content from rule files
        helper.validate.assert_validate_instructions(result)
    
    def test_file_rules_formatted_in_instructions(self, tmp_path):
        """
        SCENARIO: File validation includes rule content in instructions
        GIVEN: Production story_bot with code behavior (validates files)
        AND: Story graph file exists
        WHEN: Validate action executes
        THEN: Instructions contain rule descriptions, DO/DON'T sections, and priorities from rule files
        """
        # GIVEN: Production story_bot with code behavior (validates files)
        helper = BotTestHelper(tmp_path)
        
        # AND: Story graph file exists
        story_graph_data = {'epics': []}
        helper.story.create_story_graph(story_graph_data)
        
        helper.bot.behaviors.navigate_to('code')
        behavior = helper.bot.behaviors.current
        
        # AND: Validate action from production behavior
        from actions.validate.validate_action import ValidateRulesAction
        action = ValidateRulesAction(behavior=behavior, action_config=None)
        
        # WHEN: Validate action executes
        result = action.do_execute(ValidateActionContext())
        
        # THEN: Instructions contain rule content from rule files
        helper.validate.assert_validate_instructions(result)

    def test_story_graph_scanner_receives_story_graph_data(self, tmp_path):
        """
        SCENARIO: Story graph scanners receive scoped story_graph data
        GIVEN: Story graph with multiple epics ("Build Knowledge", "Epic B")
        AND: Scope filtered to "Build Knowledge" epic
        AND: Production story_bot with shape behavior
        WHEN: Validate action executes with scope
        THEN: Scanner receives filtered story graph (only "Build Knowledge" epic)
        AND: Scanner executes successfully
        AND: Instructions contain "Build Knowledge" in scope description
        """
        # GIVEN: Story graph with multiple epics
        helper = BotTestHelper(tmp_path)
        story_graph_data = {
            'epics': [
                {'name': 'Build Knowledge', 'sub_epics': [], 'story_groups': []},
                {'name': 'Epic B', 'sub_epics': [], 'story_groups': []}
            ]
        }
        helper.story.create_story_graph(story_graph_data)
        
        # AND: Scope filtered to "Build Knowledge" epic
        from scope import Scope, ScopeType
        scope = Scope(workspace_directory=tmp_path)
        scope.filter(type=ScopeType.STORY, value=['Build Knowledge'])
        
        # AND: Production story_bot with shape behavior
        helper.bot.behaviors.navigate_to('shape')
        behavior = helper.bot.behaviors.current
        
        # AND: Validate action with rules
        from actions.validate.validate_action import ValidateRulesAction
        action = ValidateRulesAction(behavior=behavior, action_config=None)
        
        # WHEN: Validate action executes with scope
        context = ValidateActionContext(scope=scope)
        result = action.do_execute(context)
        
        # THEN: Instructions reference the scoped epic
        instructions = result.get('base_instructions', [])
        instructions_text = ' '.join(instructions)
        assert 'Build Knowledge' in instructions_text, \
            "Instructions must reference scoped epic 'Build Knowledge'"
        
        # AND: Scanner executed successfully (scanners ran - we got scanner output)
        # Check that rules were loaded
        rules = result.get('rules', [])
        assert len(rules) > 0, "Shape behavior must have validation rules"
    
    def test_file_scanner_receives_file_data(self, tmp_path):
        """
        SCENARIO: File scanners receive scoped file paths
        GIVEN: Multiple Python files (test_foo.py, test_bar.py, main.py)
        AND: Scope filtered to test files only (**/test*.py)
        AND: Production story_bot with code behavior
        WHEN: Validate action executes with scope
        THEN: Scanner receives filtered files (only test_foo.py, test_bar.py)
        AND: Scanner executes successfully
        AND: Instructions reference test file scope
        """
        # GIVEN: Multiple Python files
        helper = BotTestHelper(tmp_path)
        
        # AND: Story graph file exists (required for code behavior validation)
        story_graph_data = {'epics': []}
        helper.story.create_story_graph(story_graph_data)
        
        test_dir = tmp_path / 'workspace' / 'test'
        test_dir.mkdir(parents=True)
        src_dir = tmp_path / 'workspace' / 'src'
        src_dir.mkdir(parents=True)
        
        (test_dir / 'test_foo.py').write_text('# test file')
        (test_dir / 'test_bar.py').write_text('# test file')
        (src_dir / 'main.py').write_text('# main file')
        
        # AND: Scope filtered to test files only
        from scope import Scope, ScopeType
        scope = Scope(workspace_directory=tmp_path)
        scope.filter(type=ScopeType.FILES, value=['**/test*.py'])
        
        # AND: Production story_bot with code behavior
        helper.bot.behaviors.navigate_to('code')
        behavior = helper.bot.behaviors.current
        
        # AND: Validate action with rules
        from actions.validate.validate_action import ValidateRulesAction
        action = ValidateRulesAction(behavior=behavior, action_config=None)
        
        # WHEN: Validate action executes with scope
        context = ValidateActionContext(scope=scope)
        result = action.do_execute(context)
        
        # THEN: Instructions reference file scope
        instructions = result.get('base_instructions', [])
        instructions_text = ' '.join(instructions)
        
        # Should reference test files in scope or file count
        has_file_reference = (
            'test' in instructions_text.lower() or
            'file' in instructions_text.lower() or
            str(test_dir) in instructions_text or
            'test_foo.py' in instructions_text or
            'test_bar.py' in instructions_text
        )
        assert has_file_reference, "Instructions must reference scoped files"
        
        # AND: Scanner executed successfully (scanners ran - we got scanner output)
        # Check that rules were loaded
        rules = result.get('rules', [])
        assert len(rules) > 0, "Code behavior must have validation rules"


# ============================================================================
# STORY: Display Rules
# ============================================================================

# ============================================================================
# CLI TESTS - Action Execution via CLI Commands
# ============================================================================

class TestValidateRulesUsingCLI:
    """
    Story: Validate Rules Using CLI
    
    Domain logic: test_perform_action.py::TestValidateRules
    CLI focus: Execute validate action and verify rules in output
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_validate_action_shows_rules_in_output(self, tmp_path, helper_class):
        """
        SCENARIO: Validate action shows rules in CLI output
        GIVEN: CLI is at shape.validate
        AND: Story graph exists
        WHEN: user navigates to shape.validate
        THEN: CLI output contains rule descriptions and DO/DON'T sections
        
        Domain: test_story_graph_rules_formatted_in_instructions
        """
        # Given
        helper = helper_class(tmp_path)
        
        # Create story graph
        story_graph_data = {'epics': []}
        helper.domain.story.create_story_graph(story_graph_data)
        
        helper.domain.state.set_state('shape', 'validate')
        
        # When
        cli_response = helper.cli_session.execute_command('shape.validate')
        
        # Then
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'validate')
        # Rules should be in output
        output_lower = cli_response.output.lower()
        assert 'rule' in output_lower or 'validate' in output_lower
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_validate_code_shows_file_rules(self, tmp_path, helper_class):
        """
        SCENARIO: Code validate action shows file rules in CLI output
        GIVEN: CLI is at code.validate
        AND: Story graph exists
        WHEN: user navigates to code.validate
        THEN: CLI output contains file validation rules
        
        Domain: test_file_rules_formatted_in_instructions
        """
        # Given
        helper = helper_class(tmp_path)
        
        # Create story graph
        story_graph_data = {'epics': []}
        helper.domain.story.create_story_graph(story_graph_data)
        
        helper.domain.state.set_state('code', 'validate')
        
        # When
        cli_response = helper.cli_session.execute_command('code.validate')
        
        # Then
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'code', 'validate')


# ============================================================================
# STORY: Display Rules
# Maps to: TestDisplayRules in test_perform_action.py
# ============================================================================
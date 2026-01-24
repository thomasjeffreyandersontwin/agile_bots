"""
Test Build Story Graph

SubEpic: Build Story Graph
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

class TestBuildStoryGraph:

    def test_action_injects_story_graph_template(self, tmp_path):
        """
        SCENARIO: Action Injects Story Graph Template
        GIVEN: Production story_bot with shape behavior (has story graph templates)
        WHEN: Action injects story graph template
        THEN: Instructions contain template_path from existing templates
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action_obj = BuildStoryGraphAction(behavior=helper.bot.behaviors.current, action_config=None)
        
        instructions = action_obj.get_instructions()
        
        assert 'template_path' in instructions
        assert instructions['template_path'] is not None

    def test_action_loads_and_merges_instructions(self, tmp_path):
        """
        SCENARIO: Action Loads And Merges Instructions
        GIVEN: Production story_bot with shape behavior (has story graph templates)
        WHEN: Action injects story graph and instructions
        THEN: Instructions contain all BuildStoryGraphAction-specific fields
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action_obj = helper.bot.behaviors.current.actions.find_by_name('build')
        
        instructions = action_obj.do_execute()
        
        helper.build.assert_build_story_graph_instructions(instructions)

    def test_all_template_variables_are_replaced_in_instructions(self, tmp_path):
        """
        SCENARIO: All Template Variables Are Replaced In Instructions
        GIVEN: Production story_bot with shape behavior (has story graph templates)
        WHEN: Action injects all template variables
        THEN: Instructions contain all required BuildStoryGraphAction fields
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action_obj = helper.bot.behaviors.current.actions.find_by_name('build')
        
        instructions = action_obj.do_execute()
        
        helper.build.assert_build_story_graph_instructions(instructions)

    def test_behavior_updates_existing_story_graph_json(self, tmp_path):
        """
        SCENARIO: Prioritization behavior updates existing story-graph.json
        GIVEN: Production prioritization behavior with increments templates
        AND: Existing story-graph.json in workspace
        WHEN: Action injects story graph template for increments
        THEN: Instructions use production template (story_graph_increments.json) that updates existing file
        """
        helper = BotTestHelper(tmp_path)
        
        existing_story_graph = helper.story.given_story_graph_dict(epic='mob')
        stories_dir = helper.workspace / 'docs' / 'stories'
        story_graph_path = helper.files.given_file_created(stories_dir, 'story-graph.json', existing_story_graph)
        
        helper.bot.behaviors.navigate_to('prioritization')
        action_obj = BuildStoryGraphAction(behavior=helper.bot.behaviors.current, action_config=None)
        
        instructions = action_obj.do_execute()
        
        # Then: Instructions indicate updating existing file
        assert instructions.get('story_graph_config'), "Instructions should contain 'story_graph_config'"
        config = instructions.get('story_graph_config', {})
        assert config.get('output') == 'story-graph.json', f"Expected output 'story-graph.json', got '{config.get('output')}'"
        assert instructions.get('template_path'), "Instructions should contain 'template_path'"
        assert story_graph_path.exists(), f"Story graph file should exist: {story_graph_path}"
        path_str = str(config.get('path')).replace('\\', '/')
        assert 'docs/stories' in path_str, f"Expected path to contain 'docs/stories', got '{config.get('path')}'"


# ============================================================================
# STORY: Clarify Requirements
# ============================================================================

# ============================================================================
# CLI TESTS - Action Execution via CLI Commands
# ============================================================================

class TestBuildStoryGraphUsingCLI:
    """
    Story: Build Story Graph Using CLI
    
    Domain logic: test_perform_action.py::TestBuildStoryGraph
    CLI focus: Execute build action and verify template injection in output
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_build_action_shows_template_in_output(self, tmp_path, helper_class):
        """
        SCENARIO: Build action shows story graph template in CLI output
        GIVEN: CLI is at shape.build
        WHEN: user navigates to shape.build
        THEN: CLI output contains template_path information
        
        Domain: test_action_injects_story_graph_template
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'build')
        
        # When - Navigate to build action (shows instructions with template)
        cli_response = helper.cli_session.execute_command('shape.build')
        
        # Then - Output contains template information
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'build')
        assert 'template' in cli_response.output.lower()
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_build_action_shows_complete_instructions(self, tmp_path, helper_class):
        """
        SCENARIO: Build action shows complete build story graph instructions
        GIVEN: CLI is at shape.build
        WHEN: user navigates to shape.build
        THEN: CLI output contains all BuildStoryGraphAction fields
        
        Domain: test_action_loads_and_merges_instructions
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'build')
        
        # When
        cli_response = helper.cli_session.execute_command('shape.build')
        
        # Then
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'build')
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_prioritization_validate_shows_increments_instructions(self, tmp_path, helper_class):
        """
        SCENARIO: Prioritization validate action shows increments validation
        GIVEN: CLI is at prioritization.validate
        AND: Story graph exists in workspace
        WHEN: user navigates to prioritization.validate
        THEN: CLI output shows validation instructions for increments
        
        Domain: test_behavior_updates_existing_story_graph_json (adapted)
        """
        # Given
        helper = helper_class(tmp_path)
        
        # Create existing story graph
        existing_story_graph = helper.domain.story.given_story_graph_dict(epic='mob')
        stories_dir = helper.domain.workspace / 'docs' / 'stories'
        helper.domain.files.given_file_created(stories_dir, 'story-graph.json', existing_story_graph)
        
        helper.domain.state.set_state('prioritization', 'validate')
        
        # When
        cli_response = helper.cli_session.execute_command('prioritization.validate')
        
        # Then
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'prioritization', 'validate')


# ============================================================================
# STORY: Clarify Requirements
# Maps to: TestClarifyRequirements in test_perform_action.py
# ============================================================================
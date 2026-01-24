"""
Test Set Story Filter

SubEpic: Set Story Filter
Parent Epic: Invoke Bot > Edit Story Map

Domain tests verify core scope management logic.
CLI tests verify command parsing and output formatting across TTY, Pipe, and JSON channels.
"""
import pytest
from pathlib import Path
import json
import os
from helpers.bot_test_helper import BotTestHelper
from helpers import TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper


# ============================================================================
# DOMAIN TESTS - Core Scope Logic
# ============================================================================

class TestFilterScopeByStories:
    
    def test_filter_returns_all_when_scope_is_all(self, tmp_path):
        """
        SCENARIO: Filter returns all when scope is all
        GIVEN: Story graph with multiple epics and increments
        WHEN: Filter with scope type 'all'
        THEN: Story graph contains all epics and increments
        """
        helper = BotTestHelper(tmp_path)
        story_graph = helper.story.story_graph_with_epics_and_increments()
        
        filtered_graph = helper.scope.filter_story_graph('build', 'all', None, story_graph=story_graph)
        
        helper.scope.assert_story_graph_contains_all_epics(filtered_graph, 2)
        helper.scope.assert_story_graph_contains_all_increments(filtered_graph, 2)
    
    def test_filter_by_single_story_name_returns_matching_story(self, tmp_path):
        """
        SCENARIO: Filter by single story name returns matching story
        GIVEN: Story graph with multiple stories
        WHEN: Filter with single story name
        THEN: Story graph contains only matching story and its parent epic
        """
        helper = BotTestHelper(tmp_path)
        story_graph = helper.story.story_graph_with_epics_and_increments()
        
        filtered_graph = helper.scope.filter_story_graph('build', 'story', ['Story A1'], story_graph=story_graph)
        
        helper.scope.assert_story_graph_contains_epic(filtered_graph, 'Epic A')
        helper.scope.assert_story_graph_contains_story(filtered_graph, 'Story A1')
        assert 'Epic B' not in [epic.get('name') for epic in filtered_graph.get('epics', [])]
    
    def test_filter_by_single_epic_name_returns_matching_epic(self, tmp_path):
        """
        SCENARIO: Filter by single epic name returns matching epic
        GIVEN: Story graph with multiple epics
        WHEN: Filter with single epic name
        THEN: Story graph contains only matching epic and its increments
        """
        helper = BotTestHelper(tmp_path)
        story_graph = helper.story.story_graph_with_epics_and_increments()
        
        filtered_graph = helper.scope.filter_story_graph('build', 'epic', ['Epic A'], story_graph=story_graph)
        
        helper.scope.assert_story_graph_contains_epic(filtered_graph, 'Epic A')
        assert 'Epic B' not in [epic.get('name') for epic in filtered_graph.get('epics', [])]
        helper.scope.assert_story_graph_contains_increment(filtered_graph, 'Increment 1')
    
    def test_filter_by_increment_priorities_returns_matching_increments(self, tmp_path):
        """
        SCENARIO: Filter by increment priorities returns matching increments
        GIVEN: Story graph with increments having different priorities
        WHEN: Filter with increment priorities
        THEN: Story graph contains only matching increments and their stories
        """
        helper = BotTestHelper(tmp_path)
        story_graph = helper.story.story_graph_with_epics_and_increments()
        
        filtered_graph = helper.scope.filter_story_graph('build', 'increment', [1], story_graph=story_graph)
        
        helper.scope.assert_story_graph_contains_increment(filtered_graph, 'Increment 1')
        assert 'Increment 2' not in [inc.get('name') for inc in filtered_graph.get('increments', [])]
        helper.scope.assert_story_graph_contains_epic(filtered_graph, 'Epic A')
    
    def test_filter_by_increment_names_returns_matching_increments(self, tmp_path):
        """
        SCENARIO: Filter by increment names returns matching increments
        GIVEN: Story graph with increments having different names
        WHEN: Filter with increment names
        THEN: Story graph contains only matching increments and their stories
        """
        helper = BotTestHelper(tmp_path)
        story_graph = helper.story.story_graph_with_epics_and_increments()
        
        filtered_graph = helper.scope.filter_story_graph('build', 'increment', ['Increment 1'], story_graph=story_graph)
        
        helper.scope.assert_story_graph_contains_increment(filtered_graph, 'Increment 1')
        assert 'Increment 2' not in [inc.get('name') for inc in filtered_graph.get('increments', [])]
        helper.scope.assert_story_graph_contains_epic(filtered_graph, 'Epic A')
    
    def test_filter_returns_parent_epic_when_child_story_matches(self, tmp_path):
        """
        SCENARIO: Filter returns parent epic when child story matches
        GIVEN: Story graph with epic containing story
        WHEN: Scope set to story name
        THEN: Story and parent epic are both returned
        """
        helper = BotTestHelper(tmp_path)
        story_graph = helper.story.story_graph_with_epics_and_increments()
        
        filtered_graph = helper.scope.filter_story_graph('build', 'story', ['Story A1'], story_graph=story_graph)
        
        helper.scope.assert_story_graph_contains_story(filtered_graph, 'Story A1')
        helper.scope.assert_story_graph_contains_epic(filtered_graph, 'Epic A')

# ============================================================================
# CLI TESTS - Scope Operations via CLI Commands
# ============================================================================

class TestFilterScopeByStoriesUsingCLI:
    """
    Story: Filter Scope By Stories Using CLI
    
    Domain logic: test_manage_scope.py::TestFilterScopeByStories
    CLI focus: Story filtering via scope commands
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_scope_all_returns_all_stories_via_cli(self, tmp_path, helper_class):
        """
        SCENARIO: Scope 'all' returns all stories via CLI
        GIVEN: CLI session with story graph
        WHEN: scope set to 'all'
        THEN: All stories accessible
        
        Domain: test_filter_returns_all_when_scope_is_all
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # When
        cli_response = helper.cli_session.execute_command('scope set all')
        
        # Then - Validate complete scope response for 'all' scope
        helper.bot.assert_scope_response_present(cli_response.output)
        assert 'all' in cli_response.output.lower()
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_scope_single_story_via_cli(self, tmp_path, helper_class):
        """
        SCENARIO: Scope single story via CLI
        GIVEN: CLI session
        WHEN: scope set to single story
        THEN: Only specified story in scope
        
        Domain: test_filter_by_single_story_name_returns_matching_story
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # When
        cli_response = helper.cli_session.execute_command('scope set story TestStory')
        
        # Then - Validate complete scope response showing story scope
        helper.scope.assert_scope_shows_target(cli_response.output, 'story', 'TestStory')
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_scope_single_epic_via_cli(self, tmp_path, helper_class):
        """
        SCENARIO: Scope single epic via CLI
        GIVEN: CLI session
        WHEN: scope set to single epic
        THEN: Only specified epic in scope
        
        Domain: test_filter_by_single_epic_name_returns_matching_epic
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # When
        cli_response = helper.cli_session.execute_command('scope set epic TestEpic')
        
        # Then - Validate complete scope response showing epic scope
        helper.scope.assert_scope_shows_target(cli_response.output, 'epic', 'TestEpic')
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_scope_increment_priority_via_cli(self, tmp_path, helper_class):
        """
        SCENARIO: Scope by increment priority via CLI
        GIVEN: CLI session
        WHEN: scope set to increment priority
        THEN: Only specified increment in scope
        
        Domain: test_filter_by_increment_priorities_returns_matching_increments
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # When
        cli_response = helper.cli_session.execute_command('scope set increment 1')
        
        # Then - Validate complete scope response showing increment scope
        helper.scope.assert_scope_shows_target(cli_response.output, 'increment', '1')
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_scope_increment_name_via_cli(self, tmp_path, helper_class):
        """
        SCENARIO: Scope by increment name via CLI
        GIVEN: CLI session
        WHEN: scope set to increment name
        THEN: Only specified increment in scope
        
        Domain: test_filter_by_increment_names_returns_matching_increments
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # When
        cli_response = helper.cli_session.execute_command('scope set increment Increment1')
        
        # Then - Validate complete scope response showing increment scope
        helper.scope.assert_scope_shows_target(cli_response.output, 'increment', 'Increment1')


# ============================================================================
# STORY: Filter Scope By Files
# Maps to: TestFilterScopeByFiles in test_manage_scope.py (~many tests)
# ============================================================================
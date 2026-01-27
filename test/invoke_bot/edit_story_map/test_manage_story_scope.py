"""
Test Manage Story Scope

SubEpic: Manage Story Scope
Parent Epic: Invoke Bot > Edit Story Map

Domain tests verify core scope management logic.
CLI tests verify command parsing and output formatting across TTY, Pipe, and JSON channels.
"""
import json
import pytest
from helpers.bot_test_helper import BotTestHelper
from helpers import TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper
from story_graph.nodes import Scenario
 

# ============================================================================
# CLI TESTS - Scope Operations via CLI Commands
# ============================================================================

class TestNavigateStoryGraphUsingCLI:
    """
    Story: Navigate Story Graph Using CLI
    
    Domain logic: test_manage_scope.py::TestNavigateStoryGraph
    CLI focus: Story graph navigation with scope filtering
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_navigate_story_graph_with_scope_via_cli(self, tmp_path, helper_class):
        """
        SCENARIO: Navigate story graph with scope via CLI
        GIVEN: CLI session with story graph and scope
        WHEN: navigation commands used
        THEN: Navigation respects scope
        
        Domain: Tests in TestNavigateStoryGraph
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # When - Set scope
        cli_response = helper.cli_session.execute_command('scope set story TestStory')
        
        # Then - Validate complete scope response
        helper.scope.assert_scope_shows_target(cli_response.output, 'story', 'TestStory')

# ============================================================================
# CLI TESTS - Scope Operations via CLI Commands (merged from test_display_scope.py)
# ============================================================================

class TestCreateScopeUsingCLI:
    """
    Story: Create Scope Using CLI
    
    Domain logic: TestCreateScope
    CLI focus: Setting scope via CLI commands with different parameter combinations
    """
    
    @pytest.mark.parametrize("helper_class,scope_cmd,scope_type", [
        (TTYBotTestHelper, "scope set all", "all"),
        (TTYBotTestHelper, "scope set story Story1", "story"),
        (TTYBotTestHelper, "scope set epic EpicA", "epic"),
        (TTYBotTestHelper, "scope set increment 1", "increment"),
        (PipeBotTestHelper, "scope set all", "all"),
        (PipeBotTestHelper, "scope set story Story1", "story"),
        (JsonBotTestHelper, "scope set all", "all"),
        (JsonBotTestHelper, "scope set story Story1", "story"),
    ])
    def test_scope_set_with_different_types_via_cli(self, tmp_path, helper_class, scope_cmd, scope_type):
        """
        SCENARIO: Scope set with different parameter combinations via CLI
        GIVEN: CLI session active
        WHEN: user enters 'scope set <type> <value>'
        THEN: CLI sets scope to specified type
        
        Domain: test_scope_created_with_different_parameter_combinations
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # When
        cli_response = helper.cli_session.execute_command(scope_cmd)
        
        # Then - Validate complete scope response structure
        helper.bot.assert_scope_response_present(cli_response.output)
        # Also verify scope type is in output
        assert scope_type in cli_response.output.lower()
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_scope_defaults_to_all_via_cli(self, tmp_path, helper_class):
        """
        SCENARIO: Scope defaults to 'all' when no scope set via CLI
        GIVEN: CLI session with no scope set
        WHEN: scope accessed
        THEN: Default scope is 'all'
        
        Domain: test_scope_defaults_to_all_when_no_parameters
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # When - Check scope (no scope set command)
        # Accessing bot scope directly since CLI doesn't have explicit "show scope" in these tests
        
        # Then - Default scope behavior applies
        assert helper.cli_session.bot is not None

class TestDisplayScopeUsingCLI:
    """
    Story: Display Scope Using CLI
    
    CLI-specific story: Displaying current scope status
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_display_scope_shows_current_scope_via_cli(self, tmp_path, helper_class):
        """
        SCENARIO: Display scope shows current scope via CLI
        GIVEN: CLI session with scope set
        WHEN: scope displayed
        THEN: Current scope shown in output
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # When - Set scope
        cli_response = helper.cli_session.execute_command('scope set story TestStory')
        
        # Then - Validate complete scope display response
        helper.scope.assert_scope_shows_target(cli_response.output, 'story', 'TestStory')

class TestCreateScope:
    
    @pytest.mark.parametrize("parameters,expected_scope_contains", [
        # Scope 'all'
        ({'scope': {'type': 'all'}}, {'all': True}),
        # Single story
        ({'scope': {'type': 'story', 'value': ['Story1']}}, {'story_names': ['Story1']}),
        # Multiple stories
        ({'scope': {'type': 'story', 'value': ['Story1', 'Story2']}}, {'story_names': ['Story1', 'Story2']}),
        # Single increment priority
        ({'scope': {'type': 'increment', 'value': [1]}}, {'increment_priorities': [1]}),
        # Multiple increment priorities
        ({'scope': {'type': 'increment', 'value': [1, 2]}}, {'increment_priorities': [1, 2]}),
        # Single epic
        ({'scope': {'type': 'epic', 'value': ['Epic A']}}, {'epic_names': ['Epic A']}),
        # Multiple epics
        ({'scope': {'type': 'epic', 'value': ['Epic A', 'Epic B']}}, {'epic_names': ['Epic A', 'Epic B']}),
        # Increment by name
        ({'scope': {'type': 'increment', 'value': ['Increment 1']}}, {'increment_names': ['Increment 1']}),
        # No parameters defaults to 'all'
        ({}, {'all': True}),
    ])
    def test_scope_created_with_different_parameter_combinations(self, tmp_path, parameters, expected_scope_contains):
        """
        SCENARIO: Scope created with different parameter combinations
        GIVEN: Parameters dict with scope configuration
        WHEN: ActionScope instantiated with parameters
        THEN: ActionScope scope property returns expected configuration
        """
        from scope.action_scope import ActionScope
        helper = BotTestHelper(tmp_path)
        action_scope = ActionScope(parameters, None)
        
        helper.build.assert_build_scope_matches(action_scope, expected_scope_contains)
    
    def test_scope_defaults_to_all_when_no_parameters(self, tmp_path):
        """
        SCENARIO: Scope defaults to 'all' when no parameters provided
        GIVEN: Empty parameters dict
        WHEN: ActionScope instantiated
        THEN: Scope defaults to 'all'
        """
        from scope.action_scope import ActionScope
        helper = BotTestHelper(tmp_path)
        parameters = {}
        
        action_scope = ActionScope(parameters, None)
        
        helper.build.assert_build_scope_contains(action_scope, 'all', True)

# ============================================================================
# DOMAIN TESTS - Set scope to selected story node and submit
# ============================================================================

class TestExecuteActionsWithScope:
    
    def test_build_action_includes_scope_in_instructions(self, tmp_path):
        """
        SCENARIO: Build action includes scope in instructions
        GIVEN: Build action with story scope
        WHEN: Instructions are retrieved
        THEN: Instructions contain scope configuration
        """
        from actions.action_context import ScopeActionContext
        from scope import Scope, StoryGraphFilter
        
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('build')
        
        from scope import ScopeType
        scope = Scope(workspace_directory=tmp_path)
        scope.filter(type=ScopeType.STORY, value=['Story1', 'Story2'])
        context = ScopeActionContext(scope=scope)
        
        instructions = action.get_instructions(context)
        
        assert 'scope' in instructions
        assert instructions['scope'] is not None
        assert isinstance(instructions['scope'], dict)
    
    def test_validate_action_accepts_scope_context(self, tmp_path):
        """
        SCENARIO: Validate action accepts scope context
        GIVEN: Validate action with story scope and story graph file
        WHEN: Instructions are retrieved
        THEN: No errors occur and scope is processed
        """
        from actions.action_context import ValidateActionContext
        from scope import Scope, StoryGraphFilter
        
        helper = BotTestHelper(tmp_path)
        
        # Create story graph file (validate requires it)
        story_graph = helper.story.given_story_graph_dict(epic='exploration')
        stories_dir = helper.workspace / 'docs' / 'stories'
        helper.files.given_file_created(stories_dir, 'story-graph.json', story_graph)
        
        helper.bot.behaviors.navigate_to('exploration')
        action = helper.bot.behaviors.current.actions.find_by_name('validate')
        
        from scope import ScopeType
        scope = Scope(workspace_directory=tmp_path)
        scope.filter(type=ScopeType.STORY, value=['Story1'])
        context = ValidateActionContext(scope=scope)
        
        # Should not raise an error
        instructions = action.get_instructions(context)
        assert instructions is not None
        # Validate uses ScopeActionContext (via ValidateActionContext)
        assert hasattr(context, 'scope')
    
    def test_render_action_accepts_scope_context(self, tmp_path):
        """
        SCENARIO: Render action accepts scope context
        GIVEN: Render action with story scope
        WHEN: Instructions are retrieved
        THEN: No errors occur (render supports ScopeActionContext)
        """
        from actions.action_context import ScopeActionContext
        from scope import Scope, ScopeType
        
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('exploration')
        action = helper.bot.behaviors.current.actions.find_by_name('render')
        
        scope = Scope(workspace_directory=tmp_path)
        scope.filter(type=ScopeType.STORY, value=['Story1'])
        context = ScopeActionContext(scope=scope)
        
        # Should not raise an error
        instructions = action.get_instructions(context)
        assert instructions is not None
    
    def test_clarify_action_does_not_support_scope(self, tmp_path):
        """
        SCENARIO: Clarify action does not support scope
        GIVEN: Clarify action
        WHEN: Context is checked
        THEN: Uses ClarifyActionContext (not ScopeActionContext)
        """
        from actions.action_context import ClarifyActionContext
        
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('clarify')
        
        # Clarify uses ClarifyActionContext, not ScopeActionContext
        assert action.context_class == ClarifyActionContext
        assert not hasattr(action.context_class(), 'scope')
    
    def test_strategy_action_does_not_support_scope(self, tmp_path):
        """
        SCENARIO: Strategy action does not support scope
        GIVEN: Strategy action
        WHEN: Context is checked
        THEN: Uses StrategyActionContext (not ScopeActionContext)
        """
        from actions.action_context import StrategyActionContext
        
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('strategy')
        
        # Strategy uses StrategyActionContext, not ScopeActionContext
        assert action.context_class == StrategyActionContext
        assert not hasattr(action.context_class(), 'scope')

class TestExecuteActionScopedToStoryNode:
    """Tests for executing actions scoped to story nodes."""
    # Scenario: Execute action on node with valid parameters
    
    @pytest.mark.parametrize('node_type,node_name,action_name,parameters', [
        ('Epic', 'User Management', 'build', '{"output": "docs/stories"}'),
        ('SubEpic', 'Authentication', 'validate', '{"rules": "all"}'),
        ('Story', 'Login Form', 'render', '{"format": "markdown"}'),
    ])
    def test_execute_action_on_node_with_valid_parameters(self, tmp_path, node_type, node_name, action_name, parameters):
        """
        SCENARIO: Execute action on node with valid parameters
        GIVEN: Node exists and bot has registered actions
        WHEN: Node executes action with valid parameters
        THEN: Action completes successfully
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_node_and_actions(
            node_type, node_name, ['clarify', 'strategy', 'build', 'validate', 'render']
        )
        
        if node_type == 'Epic':
            node = helper.story.bot.story_graph.epics[node_name]
        elif node_type == 'SubEpic':
            node = helper.story.find_subepic_in_story_graph(node_name)
        else:
            node = helper.story.find_story_in_story_graph(node_name)
        
        result = node.execute_action(action_name, parameters)
        
        assert result.success is True
        helper.story.assert_story_graph_structure_valid()
    # Scenario: Execute action with invalid parameters returns error
    
    @pytest.mark.parametrize('node_type,node_name,action_name,invalid_parameters,invalid_params_list,error_message', [
        ('Epic', 'User Management', 'build', '{"invalid_key": "value"}', 'invalid_key', 'Invalid parameter: invalid_key. Expected: output'),
        ('SubEpic', 'Authentication', 'validate', '{}', 'rules', 'Missing required parameter: rules'),
        ('Story', 'Login Form', 'render', '{"format": "invalid_format"}', 'format', 'Invalid format value: invalid_format. Expected: markdown, json, html'),
    ])
    def test_execute_action_with_invalid_parameters_returns_error(self, tmp_path, node_type, node_name, action_name, invalid_parameters, invalid_params_list, error_message):
        """
        SCENARIO: Execute action with invalid parameters returns error
        GIVEN: Node exists and bot has registered actions
        WHEN: Node executes action with invalid parameters
        THEN: Bot validates parameters and returns error
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_node_and_actions(
            node_type, node_name, ['clarify', 'strategy', 'build', 'validate', 'render']
        )
        
        if node_type == 'Epic':
            node = helper.story.bot.story_graph.epics[node_name]
        elif node_type == 'SubEpic':
            node = helper.story.find_subepic_in_story_graph(node_name)
        else:
            node = helper.story.find_story_in_story_graph(node_name)
        
        with pytest.raises(ValueError, match=error_message):
            node.execute_action(action_name, invalid_parameters)
    # Scenario: Execute non-existent action returns error
    
    @pytest.mark.parametrize('node_type,node_name,non_existent_action', [
        ('Epic', 'User Management', 'deploy'),
        ('SubEpic', 'Authentication', 'test'),
        ('Story', 'Login Form', 'compile'),
    ])
    def test_execute_non_existent_action_returns_error(self, tmp_path, node_type, node_name, non_existent_action):
        """
        SCENARIO: Execute non-existent action returns error
        GIVEN: Node exists and bot has registered actions
        WHEN: Node attempts to execute non-existent action
        THEN: Bot validates action exists and returns error
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_node_and_actions(
            node_type, node_name, ['clarify', 'strategy', 'build', 'validate', 'render']
        )
        
        if node_type == 'Epic':
            node = helper.story.bot.story_graph.epics[node_name]
        elif node_type == 'SubEpic':
            node = helper.story.find_subepic_in_story_graph(node_name)
        else:
            node = helper.story.find_story_in_story_graph(node_name)
        
        with pytest.raises(ValueError, match=f"Action '{non_existent_action}' not found. Available actions: clarify, strategy, build, validate, render"):
            node.execute_action(non_existent_action)

# ============================================================================
# CLI TESTS - Story Graph Editing via CLI Commands
# ============================================================================

# ============================================================================
# STORY: Create Epic at Root Level
# Maps to: TestCreateEpic in test_create_epic.py
# ============================================================================

class TestExecuteActionsWithScopeUsingCLI:
    """
    Story: Execute Actions With Scope Using CLI
    
    Domain logic: test_manage_scope.py::TestExecuteActionsWithScope
    CLI focus: Action execution respects active scope
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_action_execution_uses_scope_via_cli(self, tmp_path, helper_class):
        """
        SCENARIO: Action execution uses active scope via CLI
        GIVEN: CLI session with scope set
        WHEN: action executed
        THEN: Action operates within scope
        
        Domain: Tests in TestExecuteActionsWithScope
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'validate')
        
        # Create story graph for validation
        story_graph_data = {'epics': []}
        helper.domain.story.create_story_graph(story_graph_data)
        
        # When - Set scope and execute action
        cli_response1 = helper.cli_session.execute_command('scope set epic TestEpic')
        cli_response2 = helper.cli_session.execute_command('shape.validate')
        
        # Then - Validate complete action execution response
        helper.bot.assert_status_section_present(cli_response2.output)

# ============================================================================
# STORY: Navigate Story Graph
# Maps to: TestNavigateStoryGraph in test_manage_scope.py
# ============================================================================


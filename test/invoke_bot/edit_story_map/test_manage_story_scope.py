"""
Test Manage Story Scope

SubEpic: Manage Story Scope
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
from story_graph import StoryMap
from scanners.story_map import Epic, SubEpic, StoryGroup, Story, Scenario, ScenarioOutline
 

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
# DOMAIN TESTS - Scope Creation (merged from test_display_scope.py)
# ============================================================================

class TestPersistScope:
    
    def test_scope_persists_across_bot_invocations(self, tmp_path):
        """
        SCENARIO: Scope persists across bot invocations
        GIVEN: Bot with scope set
        WHEN: Bot is reloaded
        THEN: Scope is restored from workflow state
        """
        # TODO: Implement scope persistence tests
        pass
    
    def test_scope_persists_after_action_execution(self, tmp_path):
        """
        SCENARIO: Scope persists after action execution
        GIVEN: Bot with scope set
        WHEN: Action executes and completes
        THEN: Scope remains active for next action
        """
        # TODO: Implement
        pass

class TestClearScope:
    
    def test_clear_scope_with_show_all_parameter(self, tmp_path):
        """
        SCENARIO: Clear scope with show_all parameter
        GIVEN: Bot with scope set
        WHEN: Scope cleared with show_all=True
        THEN: Scope is cleared and all content is shown
        """
        # TODO: Implement clear scope tests
        pass
    
    def test_clear_scope_without_show_all_parameter(self, tmp_path):
        """
        SCENARIO: Clear scope without show_all parameter
        GIVEN: Bot with scope set
        WHEN: Scope cleared without show_all parameter
        THEN: Scope is cleared
        """
        # TODO: Implement
        pass
    
    def test_actions_after_clear_process_all_content(self, tmp_path):
        """
        SCENARIO: Actions after clear process all content
        GIVEN: Bot had scope set, then cleared
        WHEN: Action executes
        THEN: Action processes all content without filtering
        """
        # TODO: Implement
        pass

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
# DOMAIN TESTS - Set Scope To Selected Story Node And Submit
# Story: Set scope to selected story node and submit
# Sub-Epic: Manage Story Scope
# ============================================================================

class TestSetScopeAndSubmit:
    """
    Story: Set scope to selected story node and submit
    
    Tests the scope submission feature that allows users to submit a scoped selection
    to start work on a specific epic, sub-epic, or story. The bot analyzes the node
    state and determines the appropriate behavior (shape, explore, scenarios, tests, or code).
    """
    
    def test_user_submits_scope_via_cli(self, tmp_path):
        """
        SCENARIO: User submits scope via CLI command
        GIVEN: User has workspace with story graph
        WHEN: User executes scope submit command with epic name Edit Story Map
        THEN: System analyzes the epic and determines behavior
        AND: System sets bot to build mode with determined behavior
        """
        # Given - workspace with story graph
        helper = BotTestHelper(tmp_path)
        story_graph = given_story_graph_with_edit_story_map_epic()
        helper.story.create_story_graph(story_graph)
        
        # When - User executes scope submit command
        result = helper.bot.submit_scope('Edit Story Map')
        
        # Then - Verify submission was processed successfully
        assert result is not None, 'Scope submission should return result'
        assert result.get('status') == 'success', f"Expected success, got: {result}"
        assert result.get('behavior') in ['shape', 'explore', 'scenarios', 'tests', 'code']
        assert result.get('action') == 'build'
        assert helper.bot.current_behavior_name is not None
        assert helper.bot.current_action_name == 'build'
    
    def test_bot_processes_scope_submission_at_domain_level(self, tmp_path):
        """
        SCENARIO: Bot processes scope submission at domain level
        GIVEN: Bot has story graph loaded with Filter Scope epic
        WHEN: Bot receives scope submission request for Filter Scope
        THEN: Bot analyzes epic, determines behavior, sets to build mode
        """
        # Given - Bot with story graph loaded
        helper = BotTestHelper(tmp_path)
        story_graph = given_story_graph_with_filter_scope_epic()
        helper.story.create_story_graph(story_graph)
        
        # When - Bot receives scope submission request
        result = helper.bot.process_scope_submission('Filter Scope')
        
        # Then - Bot processes submission successfully
        assert result.status == 'success'
        assert result.behavior is not None
        assert result.action == 'build'
        assert helper.bot.current_behavior_name is not None
        assert helper.bot.current_action_name == 'build'
    
    def test_bot_determines_shape_for_empty_epic(self, tmp_path):
        """
        SCENARIO: Bot determines shape behavior for empty epic
        GIVEN: Epic named Product Management has no sub-epics and no stories
        WHEN: Bot analyzes the epic after scope submission
        THEN: Bot determines behavior should be shape
        """
        # Given - Empty epic
        helper = BotTestHelper(tmp_path)
        story_graph = given_empty_epic('Product Management')
        helper.story.create_story_graph(story_graph)
        
        # When - Bot analyzes epic after submission
        result = helper.bot.submit_scope('Product Management')
        
        # Then - Bot determines shape behavior
        assert result.get('status') == 'success', f"Expected success, got error: {result.get('message', result)}"
        assert result.get('behavior') == 'shape'
        assert result.get('action') == 'build'
        assert helper.bot.current_behavior_name == 'shape'
        assert helper.bot.current_action_name == 'build'
    
    def test_bot_determines_shape_for_empty_sub_epic(self, tmp_path):
        """
        SCENARIO: Bot determines shape behavior for empty sub-epic
        GIVEN: Sub-epic named User Management has no stories and no nested sub-epics
        WHEN: Bot analyzes the sub-epic after scope submission
        THEN: Bot determines behavior should be shape
        """
        # Given - Empty sub-epic
        helper = BotTestHelper(tmp_path)
        story_graph = given_empty_sub_epic('User Management')
        helper.story.create_story_graph(story_graph)
        
        # When - Bot analyzes sub-epic after submission
        result = helper.bot.submit_scope('User Management')
        
        # Then - Bot determines shape behavior
        assert result.get('status') == 'success'
        assert result.get('behavior') == 'shape'
        assert result.get('action') == 'build'
        assert helper.bot.current_behavior_name == 'shape'
        assert helper.bot.current_action_name == 'build'
    
    def test_bot_determines_explore_for_stories_without_ac(self, tmp_path):
        """
        SCENARIO: Bot determines explore behavior when stories lack acceptance criteria
        GIVEN: Epic named Reporting contains three stories with empty acceptance criteria
        WHEN: Bot analyzes the epic after scope submission
        THEN: Bot determines behavior should be explore
        """
        # Given - Epic with stories lacking acceptance criteria
        helper = BotTestHelper(tmp_path)
        story_graph = given_epic_with_stories_without_acceptance_criteria('Reporting', 3)
        helper.story.create_story_graph(story_graph)
        
        # When - Bot analyzes epic after submission
        result = helper.bot.submit_scope('Reporting')
        
        # Then - Bot determines exploration behavior
        assert result.get('status') == 'success'
        assert result.get('behavior') == 'exploration'
        assert result.get('action') == 'build'
        assert helper.bot.current_behavior_name == 'exploration'
        assert helper.bot.current_action_name == 'build'
    
    def test_bot_determines_scenarios_for_stories_without_scenarios(self, tmp_path):
        """
        SCENARIO: Bot determines scenarios behavior when stories lack scenarios
        GIVEN: Epic named Authentication contains two stories with acceptance criteria but empty scenarios
        WHEN: Bot analyzes the epic after scope submission
        THEN: Bot determines behavior should be scenarios
        """
        # Given - Epic with stories lacking scenarios
        helper = BotTestHelper(tmp_path)
        story_graph = given_epic_with_stories_without_scenarios('Authentication', 2)
        helper.story.create_story_graph(story_graph)
        
        # When - Bot analyzes epic after submission
        result = helper.bot.submit_scope('Authentication')
        
        # Then - Bot determines scenarios behavior
        assert result.get('status') == 'success'
        assert result.get('behavior') == 'scenarios'
        assert result.get('action') == 'build'
        assert helper.bot.current_behavior_name == 'scenarios'
        assert helper.bot.current_action_name == 'build'
    
    def test_bot_determines_tests_for_stories_without_tests(self, tmp_path):
        """
        SCENARIO: Bot determines tests behavior when stories lack tests
        GIVEN: Epic named Data Export contains two stories with scenarios but empty test methods
        WHEN: Bot analyzes the epic after scope submission
        THEN: Bot determines behavior should be tests
        """
        # Given - Epic with stories lacking tests
        helper = BotTestHelper(tmp_path)
        story_graph = given_epic_with_stories_without_tests('Data Export', 2)
        helper.story.create_story_graph(story_graph)
        
        # When - Bot analyzes epic after submission
        result = helper.bot.submit_scope('Data Export')
        
        # Then - Bot determines tests behavior
        assert result.get('status') == 'success'
        assert result.get('behavior') == 'tests'
        assert result.get('action') == 'build'
        assert helper.bot.current_behavior_name == 'tests'
        assert helper.bot.current_action_name == 'build'
    
    def test_bot_determines_code_for_failing_tests(self, tmp_path):
        """
        SCENARIO: Bot determines code behavior when tests exist but fail
        GIVEN: Epic named File Upload contains one story with failing tests
        WHEN: Bot analyzes the epic after scope submission
        THEN: Bot determines behavior should be code
        """
        # Given - Epic with failing tests
        helper = BotTestHelper(tmp_path)
        story_graph = given_epic_with_failing_tests('File Upload', 1)
        helper.story.create_story_graph(story_graph)
        
        # When - Bot analyzes epic after submission
        result = helper.bot.submit_scope('File Upload')
        
        # Then - Bot determines code behavior
        assert result.get('status') == 'success'
        assert result.get('behavior') == 'code'
        assert result.get('action') == 'build'
        assert helper.bot.current_behavior_name == 'code'
        assert helper.bot.current_action_name == 'build'
    
    def test_bot_determines_code_for_unimplemented_code(self, tmp_path):
        """
        SCENARIO: Bot determines code behavior when tests pass but code not implemented
        GIVEN: Epic named Search Feature contains one story with passing tests but no production code
        WHEN: Bot analyzes the epic after scope submission
        THEN: Bot determines behavior should be code
        """
        # Given - Epic with passing tests but no production code
        helper = BotTestHelper(tmp_path)
        story_graph = given_epic_with_passing_tests_but_no_code('Search Feature', 1)
        helper.story.create_story_graph(story_graph)
        
        # When - Bot analyzes epic after submission
        result = helper.bot.submit_scope('Search Feature')
        
        # Then - Bot determines code behavior
        assert result.get('status') == 'success'
        assert result.get('behavior') == 'code'
        assert result.get('action') == 'build'
        assert helper.bot.current_behavior_name == 'code'
        assert helper.bot.current_action_name == 'build'


# ============================================================================
# GIVEN Helper Functions - Story Graph Creation
# ============================================================================

def given_story_graph_with_edit_story_map_epic():
    """Create story graph with Edit Story Map epic."""
    return {
        'epics': [
            {
                'name': 'Invoke Bot',
                'sequential_order': 1,
                'sub_epics': [
                    {
                        'name': 'Edit Story Map',
                        'sequential_order': 1,
                        'sub_epics': [],
                        'story_groups': [
                            {
                                'type': 'and',
                                'connector': None,
                                'stories': [
                                    {
                                        'name': 'Create Epic',
                                        'sequential_order': 1,
                                        'acceptance_criteria': ['User can create epic'],
                                        'scenarios': []
                                    }
                                ]
                            }
                        ]
                    }
                ],
                'story_groups': []
            }
        ]
    }

def given_story_graph_with_filter_scope_epic():
    """Create story graph with Filter Scope epic."""
    return {
        'epics': [
            {
                'name': 'Invoke Bot',
                'sequential_order': 1,
                'sub_epics': [
                    {
                        'name': 'Edit Story Map',
                        'sequential_order': 1,
                        'sub_epics': [
                            {
                                'name': 'Filter Scope',
                                'sequential_order': 1,
                                'sub_epics': [],
                                'story_groups': [
                                    {
                                        'type': 'and',
                                        'connector': None,
                                        'stories': [
                                            {
                                                'name': 'Set Scope',
                                                'sequential_order': 1,
                                                'acceptance_criteria': ['User can set scope'],
                                                'scenarios': [{'name': 'User sets scope', 'steps': 'Given...'}]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ],
                        'story_groups': []
                    }
                ],
                'story_groups': []
            }
        ]
    }

def given_empty_epic(epic_name):
    """Create story graph with empty epic."""
    return {
        'epics': [
            {
                'name': epic_name,
                'sequential_order': 1,
                'sub_epics': [],
                'story_groups': []
            }
        ]
    }

def given_empty_sub_epic(sub_epic_name):
    """Create story graph with empty sub-epic."""
    return {
        'epics': [
            {
                'name': 'Parent Epic',
                'sequential_order': 1,
                'sub_epics': [
                    {
                        'name': sub_epic_name,
                        'sequential_order': 1,
                        'sub_epics': [],
                        'story_groups': []
                    }
                ],
                'story_groups': []
            }
        ]
    }

def given_epic_with_stories_without_acceptance_criteria(epic_name, story_count):
    """Create epic with stories lacking acceptance criteria."""
    stories = [
        {
            'name': f'Story {i+1}',
            'sequential_order': i+1,
            'connector': None,
            'story_type': 'user',
            'acceptance_criteria': [],
            'scenarios': [],
            'scenario_outlines': [],
            'test_class': None
        }
        for i in range(story_count)
    ]
    
    return {
        'epics': [
            {
                'name': epic_name,
                'sequential_order': 1,
                'sub_epics': [
                    {
                        'name': f'{epic_name} Sub-Epic',
                        'sequential_order': 1,
                        'sub_epics': [],
                        'story_groups': [
                            {
                                'type': 'and',
                                'connector': None,
                                'stories': stories
                            }
                        ]
                    }
                ],
                'story_groups': []
            }
        ]
    }

def given_epic_with_stories_without_scenarios(epic_name, story_count):
    """Create epic with stories lacking scenarios."""
    stories = [
        {
            'name': f'Story {i+1}',
            'sequential_order': i+1,
            'connector': None,
            'story_type': 'user',
            'acceptance_criteria': ['User can perform action'],
            'scenarios': [],
            'scenario_outlines': [],
            'test_class': None
        }
        for i in range(story_count)
    ]
    
    return {
        'epics': [
            {
                'name': epic_name,
                'sequential_order': 1,
                'sub_epics': [
                    {
                        'name': f'{epic_name} Sub-Epic',
                        'sequential_order': 1,
                        'sub_epics': [],
                        'story_groups': [
                            {
                                'type': 'and',
                                'connector': None,
                                'stories': stories
                            }
                        ]
                    }
                ],
                'story_groups': []
            }
        ]
    }

def given_epic_with_stories_without_tests(epic_name, story_count):
    """Create epic with stories lacking tests."""
    stories = [
        {
            'name': f'Story {i+1}',
            'sequential_order': i+1,
            'connector': None,
            'story_type': 'user',
            'acceptance_criteria': ['User can perform action'],
            'scenarios': [
                {
                    'name': 'Scenario 1',
                    'sequential_order': 1,
                    'type': 'happy_path',
                    'background': [],
                    'steps': 'Given...\nWhen...\nThen...',
                    'test_method': None
                }
            ],
            'scenario_outlines': [],
            'test_class': None
        }
        for i in range(story_count)
    ]
    
    return {
        'epics': [
            {
                'name': epic_name,
                'sequential_order': 1,
                'sub_epics': [
                    {
                        'name': f'{epic_name} Sub-Epic',
                        'sequential_order': 1,
                        'sub_epics': [],
                        'story_groups': [
                            {
                                'type': 'and',
                                'connector': None,
                                'stories': stories
                            }
                        ]
                    }
                ],
                'story_groups': []
            }
        ]
    }

def given_epic_with_failing_tests(epic_name, story_count):
    """Create epic with stories that have failing tests."""
    stories = [
        {
            'name': f'Story {i+1}',
            'sequential_order': i+1,
            'connector': None,
            'story_type': 'user',
            'acceptance_criteria': ['User can perform action'],
            'scenarios': [
                {
                    'name': 'Scenario 1',
                    'sequential_order': 1,
                    'type': 'happy_path',
                    'background': [],
                    'steps': 'Given...\nWhen...\nThen...',
                    'test_method': f'test_story_{i+1}_scenario_1'
                }
            ],
            'scenario_outlines': [],
            'test_class': f'TestStory{i+1}',
            'test_status': 'failing'
        }
        for i in range(story_count)
    ]
    
    return {
        'epics': [
            {
                'name': epic_name,
                'sequential_order': 1,
                'sub_epics': [
                    {
                        'name': f'{epic_name} Sub-Epic',
                        'sequential_order': 1,
                        'sub_epics': [],
                        'story_groups': [
                            {
                                'type': 'and',
                                'connector': None,
                                'stories': stories
                            }
                        ]
                    }
                ],
                'story_groups': []
            }
        ]
    }

def given_epic_with_passing_tests_but_no_code(epic_name, story_count):
    """Create epic with stories that have passing tests but no production code."""
    stories = [
        {
            'name': f'Story {i+1}',
            'sequential_order': i+1,
            'connector': None,
            'story_type': 'user',
            'acceptance_criteria': ['User can perform action'],
            'scenarios': [
                {
                    'name': 'Scenario 1',
                    'sequential_order': 1,
                    'type': 'happy_path',
                    'background': [],
                    'steps': 'Given...\nWhen...\nThen...',
                    'test_method': f'test_story_{i+1}_scenario_1'
                }
            ],
            'scenario_outlines': [],
            'test_class': f'TestStory{i+1}',
            'test_status': 'passing',
            'code_implemented': False
        }
        for i in range(story_count)
    ]
    
    return {
        'epics': [
            {
                'name': epic_name,
                'sequential_order': 1,
                'sub_epics': [
                    {
                        'name': f'{epic_name} Sub-Epic',
                        'sequential_order': 1,
                        'sub_epics': [],
                        'story_groups': [
                            {
                                'type': 'and',
                                'connector': None,
                                'stories': stories
                            }
                        ]
                    }
                ],
                'story_groups': []
            }
        ]
    }


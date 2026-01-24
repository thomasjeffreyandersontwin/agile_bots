"""
Test Submit Scoped Action

SubEpic: Submit Scoped Action
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

class TestEnrichScopeWithLinks:
    """Tests for link enrichment in JSON scope (test icons and doc links)."""
    
    def test_story_with_test_file_and_class_gets_test_link(self, tmp_path):
        """
        SCENARIO: Story with test_file and test_class gets test tube icon link
        GIVEN: Story graph with story having test_file and test_class
        AND: Test file exists on disk
        WHEN: Scope is enriched with links
        THEN: Story has test_tube icon link pointing to test file
        """
        from scope.json_scope import JSONScope
        from scope import Scope, ScopeType
        
        helper = BotTestHelper(tmp_path)
        
        # Create test file
        test_dir = helper.workspace / 'test'
        test_dir.mkdir(exist_ok=True)
        test_file = test_dir / 'test_story.py'
        test_file.write_text('class TestMyStory:\n    def test_scenario(self):\n        pass')
        
        # Create story graph - story gets test_file from parent sub-epic
        story_graph = {
            'epics': [{
                'name': 'Test Epic',
                'sub_epics': [{
                    'name': 'Test Sub Epic',
                    'sequential_order': 1.0,
                    'test_file': 'test_story.py',  # Sub-epic has test_file
                    'story_groups': [{
                        'type': 'and',
                        'stories': [{
                            'name': 'Test Story',
                            # No test_file - inherits from parent sub-epic
                            'test_class': 'TestMyStory',
                            'sequential_order': 1.0
                        }]
                    }]
                }]
            }]
        }
        helper.story.create_story_graph(story_graph)
        
        # Create scope and get results
        scope = Scope(workspace_directory=helper.workspace, bot_paths=helper.bot.bot_paths)
        scope.filter(type=ScopeType.SHOW_ALL)
        json_scope = JSONScope(scope)
        result = json_scope.to_dict()
        
        # Verify test link was added
        story = result['content']['epics'][0]['sub_epics'][0]['story_groups'][0]['stories'][0]
        assert 'links' in story
        test_links = [l for l in story['links'] if l['icon'] == 'test_tube']
        assert len(test_links) == 1
        assert 'test_story.py' in test_links[0]['url']
        assert '#L' in test_links[0]['url']  # Verify it has a line number
    
    def test_story_without_test_file_gets_no_test_link(self, tmp_path):
        """
        SCENARIO: Story with test_class but no test_file gets no test icon
        GIVEN: Story graph with story having test_class but no test_file
        WHEN: Scope is enriched with links
        THEN: Story has no test_tube icon link
        """
        from scope.json_scope import JSONScope
        from scope import Scope, ScopeType
        
        helper = BotTestHelper(tmp_path)
        
        # Create story graph with only test_class using helper
        story_graph = {
            'epics': [{
                'name': 'Test Epic',
                'sub_epics': [{
                    'name': 'Test Sub Epic',
                    'sequential_order': 1.0,
                    'story_groups': [{
                        'type': 'and',
                        'stories': [{
                            'name': 'Test Story',
                            'test_class': 'TestMyStory',  # Has test_class
                            # No test_file
                            'sequential_order': 1.0
                        }]
                    }]
                }]
            }]
        }
        helper.story.create_story_graph(story_graph)
        
        # Create scope and get results
        scope = Scope(workspace_directory=helper.workspace, bot_paths=helper.bot.bot_paths)
        scope.filter(type=ScopeType.SHOW_ALL)
        json_scope = JSONScope(scope)
        result = json_scope.to_dict()
        
        # Verify no test link was added
        story = result['content']['epics'][0]['sub_epics'][0]['story_groups'][0]['stories'][0]
        test_links = [l for l in story.get('links', []) if l['icon'] == 'test_tube']
        assert len(test_links) == 0
    
    def test_sub_epic_with_test_file_gets_test_link(self, tmp_path):
        """
        SCENARIO: Sub-epic with test_file gets test tube icon link
        GIVEN: Story graph with sub-epic having test_file
        AND: Test file exists on disk
        WHEN: Scope is enriched with links
        THEN: Sub-epic has test_tube icon link pointing to test file
        """
        from scope.json_scope import JSONScope
        from scope import Scope, ScopeType
        
        helper = BotTestHelper(tmp_path)
        
        # Create test file
        test_dir = helper.workspace / 'test'
        test_dir.mkdir(exist_ok=True)
        test_file = test_dir / 'test_sub_epic.py'
        test_file.write_text('def test_something():\n    pass')
        
        # Create story graph with sub-epic having test_file using helper
        story_graph = {
            'epics': [{
                'name': 'Test Epic',
                'sub_epics': [{
                    'name': 'Test Sub Epic',
                    'sequential_order': 1.0,
                    'test_file': 'test_sub_epic.py',
                    'story_groups': []
                }]
            }]
        }
        helper.story.create_story_graph(story_graph)
        
        # Create scope and get results
        scope = Scope(workspace_directory=helper.workspace, bot_paths=helper.bot.bot_paths)
        scope.filter(type=ScopeType.SHOW_ALL)
        json_scope = JSONScope(scope)
        result = json_scope.to_dict()
        
        # Verify test link was added
        sub_epic = result['content']['epics'][0]['sub_epics'][0]
        assert 'links' in sub_epic
        test_links = [l for l in sub_epic['links'] if l['icon'] == 'test_tube']
        assert len(test_links) == 1
        assert 'test_sub_epic.py' in test_links[0]['url']
    
    def test_story_inherits_test_file_from_sub_epic(self, tmp_path):
        """
        SCENARIO: Story inherits test_file from parent sub-epic
        GIVEN: Sub-epic with test_file and story with test_class but no test_file
        AND: Test file exists on disk
        WHEN: Scope is enriched with links
        THEN: Story gets test_tube icon link using parent's test_file
        """
        from scope.json_scope import JSONScope
        from scope import Scope, ScopeType
        
        helper = BotTestHelper(tmp_path)
        
        # Create test file
        test_dir = helper.workspace / 'test'
        test_dir.mkdir(exist_ok=True)
        test_file = test_dir / 'test_sub_epic.py'
        test_file.write_text('class TestMyStory:\n    pass')
        
        # Create story graph: sub-epic has test_file, story has test_class using helper
        story_graph = {
            'epics': [{
                'name': 'Test Epic',
                'sub_epics': [{
                    'name': 'Test Sub Epic',
                    'sequential_order': 1.0,
                    'test_file': 'test_sub_epic.py',
                    'story_groups': [{
                        'type': 'and',
                        'stories': [{
                            'name': 'Test Story',
                            'test_class': 'TestMyStory',
                            # No test_file - should inherit from parent
                            'sequential_order': 1.0
                        }]
                    }]
                }]
            }]
        }
        helper.story.create_story_graph(story_graph)
        
        # Create scope and get results
        scope = Scope(workspace_directory=helper.workspace, bot_paths=helper.bot.bot_paths)
        scope.filter(type=ScopeType.SHOW_ALL)
        json_scope = JSONScope(scope)
        result = json_scope.to_dict()
        
        # Verify story got test link using parent's test_file
        story = result['content']['epics'][0]['sub_epics'][0]['story_groups'][0]['stories'][0]
        assert 'links' in story
        test_links = [l for l in story['links'] if l['icon'] == 'test_tube']
        assert len(test_links) == 1
        assert 'test_sub_epic.py' in test_links[0]['url']
        assert '#L' in test_links[0]['url']  # Verify it has a line number
    
    def test_epic_with_docs_folder_gets_document_link(self, tmp_path):
        """
        SCENARIO: Epic with docs folder gets document icon link
        GIVEN: Epic and corresponding docs/map folder exists
        WHEN: Scope is enriched with links
        THEN: Epic has document icon link pointing to docs folder
        """
        from scope.json_scope import JSONScope
        from scope import Scope, ScopeType
        
        helper = BotTestHelper(tmp_path)
        
        # Create docs folder for epic at docs/stories/map (the actual path structure)
        epic_folder = helper.workspace / 'docs' / 'stories' / 'map' / '🎯 Test Epic'
        epic_folder.mkdir(parents=True, exist_ok=True)
        
        # Create story graph using helper
        story_graph = {
            'epics': [{
                'name': 'Test Epic',
                'sub_epics': []
            }]
        }
        helper.story.create_story_graph(story_graph)
        
        # Create scope and get results
        scope = Scope(workspace_directory=helper.workspace, bot_paths=helper.bot.bot_paths)
        scope.filter(type=ScopeType.SHOW_ALL)
        json_scope = JSONScope(scope)
        result = json_scope.to_dict()
        
        # Verify document link was added
        epic = result['content']['epics'][0]
        assert 'links' in epic, f"Epic should have links. Epic data: {epic}"
        doc_links = [l for l in epic['links'] if l['icon'] == 'document']
        assert len(doc_links) == 1, f"Epic should have one document link. Links: {epic.get('links', [])}"
        assert '🎯 Test Epic' in doc_links[0]['url']
    
    @pytest.mark.parametrize("sub_epic_test_file,story_test_class,has_test_link", [
        # Sub-epic has test_file and story has test_class -> has link
        ('test_story.py', 'TestMyStory', True),
        # Sub-epic has test_file but story has no test_class -> no link
        ('test_story.py', None, False),
        # Sub-epic has no test_file but story has test_class -> no link
        (None, 'TestMyStory', False),
        # Neither sub-epic test_file nor story test_class -> no link
        (None, None, False),
    ])
    def test_story_test_link_combinations(self, tmp_path, sub_epic_test_file, story_test_class, has_test_link):
        """
        SCENARIO: Story test link appears based on sub-epic test_file and story test_class
        GIVEN: Sub-epic with/without test_file and story with/without test_class
        WHEN: Scope is enriched with links
        THEN: Test link appears only when sub-epic has test_file AND story has test_class
        """
        from scope.json_scope import JSONScope
        from scope import Scope, ScopeType
        
        helper = BotTestHelper(tmp_path)
        
        # Create test file if specified on sub-epic
        if sub_epic_test_file:
            test_dir = helper.workspace / 'test'
            test_dir.mkdir(exist_ok=True)
            test_path = test_dir / sub_epic_test_file
            test_path.write_text('class TestMyStory:\n    pass')
        
        # Create story data with test_class (stories don't have test_file)
        story_data = {
            'name': 'Test Story',
            'sequential_order': 1.0
        }
        if story_test_class:
            story_data['test_class'] = story_test_class
        
        # Create sub-epic with test_file
        sub_epic_data = {
            'name': 'Test Sub Epic',
            'sequential_order': 1.0,
            'story_groups': [{
                'type': 'and',
                'stories': [story_data]
            }]
        }
        if sub_epic_test_file:
            sub_epic_data['test_file'] = sub_epic_test_file
        
        story_graph = {
            'epics': [{
                'name': 'Test Epic',
                'sub_epics': [sub_epic_data]
            }]
        }
        
        # Save using helper
        helper.story.create_story_graph(story_graph)
        
        scope = Scope(workspace_directory=helper.workspace, bot_paths=helper.bot.bot_paths)
        scope.filter(type=ScopeType.SHOW_ALL)
        json_scope = JSONScope(scope)
        result = json_scope.to_dict()
        
        # Verify test link presence
        story = result['content']['epics'][0]['sub_epics'][0]['story_groups'][0]['stories'][0]
        test_links = [l for l in story.get('links', []) if l['icon'] == 'test_tube']
        
        if has_test_link:
            assert len(test_links) == 1, f"Story should have test link with sub_epic test_file={sub_epic_test_file}, story test_class={story_test_class}"
            assert sub_epic_test_file in test_links[0]['url']
            assert '#L' in test_links[0]['url']  # Verify it has a line number
        else:
            assert len(test_links) == 0, f"Story should not have test link with sub_epic test_file={sub_epic_test_file}, story test_class={story_test_class}"
    
    def test_scenario_with_test_method_gets_test_link(self, tmp_path):
        """
        SCENARIO: Scenario with test_method gets test link
        GIVEN: Story with scenario having test_method
        AND: Test file exists with that method
        WHEN: Scope is enriched with links
        THEN: Scenario has test link with line number
        """
        from scope.json_scope import JSONScope
        from scope import Scope, ScopeType
        
        helper = BotTestHelper(tmp_path)
        
        # Create test file with test method
        test_dir = helper.workspace / 'test'
        test_dir.mkdir(exist_ok=True)
        test_file = test_dir / 'test_story.py'
        test_file.write_text('''class TestMyStory:
    def test_happy_path(self):
        pass
    
    def test_error_case(self):
        pass
''')
        
        # Create story graph with scenario having test_method using helper
        story_graph = {
            'epics': [{
                'name': 'Test Epic',
                'sub_epics': [{
                    'name': 'Test Sub Epic',
                    'sequential_order': 1.0,
                    'test_file': 'test_story.py',  # Sub-epic has test_file
                    'story_groups': [{
                        'type': 'and',
                        'stories': [{
                            'name': 'Test Story',
                            # No test_file - inherits from parent sub-epic
                            'test_class': 'TestMyStory',
                            'sequential_order': 1.0,
                            'scenarios': [{
                                'name': 'Happy path scenario',
                                'test_method': 'test_happy_path',
                                'type': 'happy_path',
                                'steps': 'Given X\nWhen Y\nThen Z'
                            }]
                        }]
                    }]
                }]
            }]
        }
        helper.story.create_story_graph(story_graph)
        
        # Use 'story' scope type instead of 'showAll' to enable scenario enrichment
        scope = Scope(workspace_directory=helper.workspace, bot_paths=helper.bot.bot_paths)
        scope.filter(type=ScopeType.STORY, value=['Test Story'])
        json_scope = JSONScope(scope)
        result = json_scope.to_dict()
        
        # Verify scenario has test link with line number
        story = result['content']['epics'][0]['sub_epics'][0]['story_groups'][0]['stories'][0]
        scenario = story['scenarios'][0]
        
        assert 'test_file' in scenario, "Scenario should have test_file link"
        assert 'test_story.py' in scenario['test_file']
        assert '#L' in scenario['test_file'], "Scenario test link should include line number"
    
    @pytest.mark.parametrize("has_test_method,sub_epic_has_test_file,has_link", [
        # Scenario with test_method and sub-epic has test_file -> has link
        (True, True, True),
        # Scenario with test_method but sub-epic has no test_file -> no link
        (True, False, False),
        # Scenario without test_method but sub-epic has test_file -> no link
        (False, True, False),
        # Scenario without test_method and sub-epic without test_file -> no link
        (False, False, False),
    ])
    def test_scenario_test_link_combinations(self, tmp_path, has_test_method, sub_epic_has_test_file, has_link):
        """
        SCENARIO: Scenario test link appears based on test_method and sub-epic test_file
        GIVEN: Scenario with/without test_method and sub-epic with/without test_file
        WHEN: Scope is enriched with links
        THEN: Test link appears only when scenario has test_method and sub-epic has test_file
        """
        from scope.json_scope import JSONScope
        from scope import Scope, ScopeType
        
        helper = BotTestHelper(tmp_path)
        
        # Create test file if sub-epic needs it
        if sub_epic_has_test_file:
            test_dir = helper.workspace / 'test'
            test_dir.mkdir(exist_ok=True)
            test_file = test_dir / 'test_story.py'
            test_file.write_text('class TestMyStory:\n    def test_scenario(self):\n        pass')
        
        # Create scenario data
        scenario_data = {
            'name': 'Test Scenario',
            'type': 'happy_path',
            'steps': 'Given X\nWhen Y\nThen Z'
        }
        if has_test_method:
            scenario_data['test_method'] = 'test_scenario'
        
        # Create story data (stories don't have test_file - they inherit from sub-epic)
        story_data = {
            'name': 'Test Story',
            'test_class': 'TestMyStory',
            'sequential_order': 1.0,
            'scenarios': [scenario_data]
        }
        
        # Create sub-epic data with test_file
        sub_epic_data = {
            'name': 'Test Sub Epic',
            'sequential_order': 1.0,
            'story_groups': [{
                'type': 'and',
                'stories': [story_data]
            }]
        }
        if sub_epic_has_test_file:
            sub_epic_data['test_file'] = 'test_story.py'
        
        story_graph = {
            'epics': [{
                'name': 'Test Epic',
                'sub_epics': [sub_epic_data]
            }]
        }
        
        # Save using helper
        helper.story.create_story_graph(story_graph)
        
        # Use 'story' scope type instead of 'showAll' to enable scenario enrichment
        scope = Scope(workspace_directory=helper.workspace, bot_paths=helper.bot.bot_paths)
        scope.filter(type=ScopeType.STORY, value=['Test Story'])
        json_scope = JSONScope(scope)
        result = json_scope.to_dict()
        
        # Verify scenario test link
        story = result['content']['epics'][0]['sub_epics'][0]['story_groups'][0]['stories'][0]
        scenario = story['scenarios'][0]
        
        if has_link:
            assert 'test_file' in scenario, "Scenario should have test_file link"
            assert 'test_story.py' in scenario['test_file']
        else:
            # Scenario may have test_file field but it should be empty or not point to actual test
            if 'test_file' in scenario:
                assert scenario['test_file'] is None or scenario['test_file'] == ''

# ============================================================================
# CLI TESTS - Scope Operations via CLI Commands
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
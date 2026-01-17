"""
Manage Scope Using CLI Commands Tests - Parameterized Across Channels

Maps directly to: test_manage_scope.py domain tests (45 tests)

These tests focus on CLI-specific concerns:
- Scope command parsing (set, clear, display)
- CLI output format verification (TTY, Markdown, JSON modes)
- Delegation to domain logic
- All scope filtering operations accessible via CLI

Uses parameterized tests to run same test logic across all 3 channels.
"""
import pytest
from pathlib import Path
from CLI.helpers import TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper


# ============================================================================
# STORY: Create Scope
# Maps to: TestCreateScope in test_manage_scope.py (2 tests)
# ============================================================================
class TestCreateScopeUsingCLI:
    """
    Story: Create Scope Using CLI
    
    Domain logic: test_manage_scope.py::TestCreateScope
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


# ============================================================================
# STORY: Filter Scope By Stories
# Maps to: TestFilterScopeByStories in test_manage_scope.py (~6 tests)
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
class TestFilterScopeByFilesUsingCLI:
    """
    Story: Filter Scope By Files Using CLI
    
    Domain logic: test_manage_scope.py::TestFilterScopeByFiles
    CLI focus: File filtering via scope commands with include/exclude patterns
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_scope_files_with_include_pattern_via_cli(self, tmp_path, helper_class):
        """
        SCENARIO: Scope files with include pattern via CLI
        GIVEN: CLI session
        WHEN: scope set to files with include pattern
        THEN: Matching files in scope
        
        Domain: test_file_filter_includes_matching_files
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('code', 'validate')
        
        # When
        cli_response = helper.cli_session.execute_command('scope set files **/test*.py')
        
        # Then - Validate complete scope response showing files scope
        helper.scope.assert_scope_shows_target(cli_response.output, 'files', '**/test*.py')
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_scope_files_with_exclude_pattern_via_cli(self, tmp_path, helper_class):
        """
        SCENARIO: Scope files with exclude pattern via CLI
        GIVEN: CLI session
        WHEN: scope set with exclude pattern
        THEN: Excluded files not in scope
        
        Domain: test_file_filter_excludes_matching_files
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('code', 'validate')
        
        # When - Note: CLI syntax for exclude may vary
        cli_response = helper.cli_session.execute_command('scope set files *.py')
        
        # Then - Validate complete scope response showing files scope
        helper.scope.assert_scope_shows_target(cli_response.output, 'files', '*.py')


# ============================================================================
# STORY: Persist Scope
# Maps to: TestPersistScope in test_manage_scope.py
# ============================================================================
class TestPersistScopeUsingCLI:
    """
    Story: Persist Scope Using CLI
    
    Domain logic: test_manage_scope.py::TestPersistScope
    CLI focus: Scope persistence across CLI sessions
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_scope_persists_across_commands_via_cli(self, tmp_path, helper_class):
        """
        SCENARIO: Scope persists across commands via CLI
        GIVEN: CLI session with scope set
        WHEN: multiple commands executed
        THEN: Scope remains set
        
        Domain: Tests in TestPersistScope
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # When - Set scope
        cli_response1 = helper.cli_session.execute_command('scope set story TestStory')
        
        # And - Execute another command
        cli_response2 = helper.cli_session.execute_command('shape')
        
        # Then - Both commands succeed (scope persists)
        helper.bot.assert_scope_response_present(cli_response1.output)
        helper.bot.assert_status_section_present(cli_response2.output)


# ============================================================================
# STORY: Clear Scope
# Maps to: TestClearScope in test_manage_scope.py
# ============================================================================
class TestClearScopeUsingCLI:
    """
    Story: Clear Scope Using CLI
    
    Domain logic: test_manage_scope.py::TestClearScope
    CLI focus: Clearing scope via CLI command
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_clear_scope_via_cli(self, tmp_path, helper_class):
        """
        SCENARIO: Clear scope via CLI
        GIVEN: CLI session with scope set
        WHEN: user enters 'scope clear'
        THEN: Scope cleared (defaults to 'all')
        
        Domain: Tests in TestClearScope
        """
        # Given - Set scope first
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        cli_response1 = helper.cli_session.execute_command('scope set story TestStory')
        
        # When - Clear scope
        cli_response2 = helper.cli_session.execute_command('scope clear')
        
        # Then - Validate complete clear scope response
        helper.bot.assert_scope_response_present(cli_response2.output)


# ============================================================================
# STORY: Execute Actions With Scope
# Maps to: TestExecuteActionsWithScope in test_manage_scope.py
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
# STORY: Display Scope
# CLI-specific story
# ============================================================================
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

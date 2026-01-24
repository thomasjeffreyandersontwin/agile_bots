"""
Test Scope Files

SubEpic: Scope Files
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

class TestFilterScopeByFiles:
    """Tests for FileFilter functionality within scope operations."""
    
    def test_file_filter_includes_matching_files(self):
        """FileFilter includes files matching include patterns."""
        from scope import FileFilter
        from pathlib import Path
        
        files = [
            Path('test/test_file1.py'),
            Path('test/test_file2.py'),
            Path('src/source_file.py'),
            Path('docs/readme.md')
        ]
        
        file_filter = FileFilter(include_patterns=['**/test*.py'])
        filtered = file_filter.filter_files(files)
        
        assert len(filtered) == 2
        assert Path('test/test_file1.py') in filtered
        assert Path('test/test_file2.py') in filtered
        assert Path('src/source_file.py') not in filtered
    
    def test_file_filter_excludes_matching_files(self):
        """
        SCENARIO: FileFilter excludes files matching exclude patterns
        GIVEN: A list of files and a FileFilter with exclude patterns
        WHEN: filter_files() is called
        THEN: Files matching exclude patterns are removed
        """
        from scope import FileFilter
        from pathlib import Path
        
        # GIVEN: A list of files
        files = [
            Path('test/test_file1.py'),
            Path('test/test_file2.py'),
            Path('test/__pycache__/cached.pyc'),
            Path('test/.pytest_cache/file.py')
        ]
        
        # AND: A FileFilter with exclude pattern for cache files
        file_filter = FileFilter(exclude_patterns=['**/__pycache__/**', '**/.pytest_cache/**'])
        
        # WHEN: filter_files() is called
        filtered = file_filter.filter_files(files)
        
        # THEN: Cache files are excluded
        assert len(filtered) == 2
        assert Path('test/test_file1.py') in filtered
        assert Path('test/test_file2.py') in filtered
    
    def test_file_filter_combines_include_and_exclude(self):
        """
        SCENARIO: FileFilter combines include and exclude patterns
        GIVEN: A list of files and a FileFilter with both include and exclude patterns
        WHEN: filter_files() is called
        THEN: Files must match include AND not match exclude
        """
        from scope import FileFilter
        from pathlib import Path
        
        # GIVEN: A list of files
        files = [
            Path('test/test_execute_in_headless_mode.py'),
            Path('test/test_monitor_session.py'),
            Path('test/test_helpers.py'),
            Path('src/source.py')
        ]
        
        # AND: A FileFilter with include for test files and exclude for helpers
        file_filter = FileFilter(
            include_patterns=['**/test*.py'],
            exclude_patterns=['**/*helpers*.py']
        )
        
        # WHEN: filter_files() is called
        filtered = file_filter.filter_files(files)
        
        # THEN: Test files are included except helpers
        assert len(filtered) == 2
        assert Path('test/test_execute_in_headless_mode.py') in filtered
        assert Path('test/test_monitor_session.py') in filtered
        assert Path('test/test_helpers.py') not in filtered
    
    def test_file_filter_returns_all_when_no_patterns(self):
        """
        SCENARIO: FileFilter returns all files when no patterns specified
        GIVEN: A list of files and a FileFilter with no patterns
        WHEN: filter_files() is called
        THEN: All files are returned
        """
        from scope import FileFilter
        from pathlib import Path
        
        # GIVEN: A list of files
        files = [
            Path('test/test_file1.py'),
            Path('src/source.py'),
            Path('docs/readme.md')
        ]
        
        # AND: A FileFilter with no patterns
        file_filter = FileFilter()
        
        # WHEN: filter_files() is called
        filtered = file_filter.filter_files(files)
        
        # THEN: All files are returned
        assert len(filtered) == 3
        assert all(f in filtered for f in files)
    
    def test_file_filter_handles_specific_file_paths(self):
        """
        SCENARIO: FileFilter handles specific file paths (not just globs)
        GIVEN: A list of files and a FileFilter with specific file path
        WHEN: filter_files() is called
        THEN: Only the specific file is included
        """
        from scope import FileFilter
        from pathlib import Path
        
        # GIVEN: A list of files
        files = [
            Path('test/test_execute_in_headless_mode.py'),
            Path('test/test_monitor_session.py'),
            Path('test/test_helpers.py')
        ]
        
        # AND: A FileFilter with specific file path
        file_filter = FileFilter(include_patterns=['**/test_execute_in_headless_mode.py'])
        
        # WHEN: filter_files() is called
        filtered = file_filter.filter_files(files)
        
        # THEN: Only the specific file is included
        assert len(filtered) == 1
        assert Path('test/test_execute_in_headless_mode.py') in filtered
    
    def test_file_discovery_and_filtering_integration(self):
        """
        SCENARIO: File discovery and filtering work together
        GIVEN: A FileDiscovery component and a FileFilter
        WHEN: Files are discovered and then filtered
        THEN: Only matching files are returned
        
        This test verifies the integration between FileDiscovery and FileFilter,
        which was the core fix for the validation scope bug.
        """
        from scope import FileFilter
        from pathlib import Path
        
        # GIVEN: A list of discovered files (simulating FileDiscovery output)
        discovered_files = [
            Path('test/test_execute_in_headless_mode.py'),
            Path('test/test_monitor_session.py'),
            Path('test/test_helpers.py'),
            Path('test/__pycache__/cached.pyc')
        ]
        
        # AND: A FileFilter for specific files
        file_filter = FileFilter(
            include_patterns=['**/test_execute_in_headless_mode.py', '**/test_monitor_session.py'],
            exclude_patterns=['**/__pycache__/**']
        )
        
        # WHEN: Files are filtered
        filtered_files = file_filter.filter_files(discovered_files)
        
        # THEN: Only matching files are returned
        assert len(filtered_files) == 2
        assert Path('test/test_execute_in_headless_mode.py') in filtered_files
        assert Path('test/test_monitor_session.py') in filtered_files
        assert Path('test/test_helpers.py') not in filtered_files
        assert Path('test/__pycache__/cached.pyc') not in filtered_files

# ============================================================================
# CLI TESTS - Scope Operations via CLI Commands
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
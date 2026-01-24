"""
Build Test Helper
Handles build action, story graphs, templates, configs + build-specific instruction assertions
"""
import json
from pathlib import Path
from helpers.base_helper import BaseHelper


class BuildTestHelper(BaseHelper):
    """Helper for build action, story graphs, and templates testing"""
    
    def assert_build_scope_contains(self, build_scope, expected_key: str, expected_value):
        """Assert BuildScope contains expected key-value pair.
        
        Args:
            build_scope: BuildScope instance
            expected_key: Key to check in build_scope.scope
            expected_value: Expected value for the key
        """
        assert expected_key in build_scope.scope, \
            f"Expected key '{expected_key}' not found in build_scope.scope. Keys: {list(build_scope.scope.keys())}"
        assert build_scope.scope[expected_key] == expected_value, \
            f"Expected build_scope.scope['{expected_key}'] == {expected_value}, got {build_scope.scope[expected_key]}"
    
    def assert_build_scope_matches(self, build_scope, expected_scope_contains: dict):
        """Assert BuildScope contains all expected key-value pairs.
        
        Args:
            build_scope: BuildScope instance
            expected_scope_contains: Dict of expected key-value pairs
        """
        for key, value in expected_scope_contains.items():
            self.assert_build_scope_contains(build_scope, key, value)
    
    def assert_build_story_graph_instructions(self, instructions):
        """Assert BuildStoryGraphAction injected all required fields.
        
        Args:
            instructions: Instructions object from BuildStoryGraphAction
        """
        # Check base instructions exist
        base_instructions = instructions.get('base_instructions', [])
        assert base_instructions, "base_instructions should be present"
        
        # Check BuildStoryGraphAction-specific fields
        assert instructions.get('scope') is not None, "scope should be set"
        assert instructions.get('scope_story_names') is not None, "scope_story_names should be set"
        assert instructions.get('story_graph_template') is not None, "story_graph_template should be set"
        assert instructions.get('story_graph_config') is not None, "story_graph_config should be set"
        assert instructions.get('existing_file') is not None, "existing_file should be set"
        
        # Check that either update_mode or create_mode is set
        has_update = instructions.get('update_mode') or instructions.get('update_instructions')
        has_create = instructions.get('create_mode') or instructions.get('create_instructions')
        assert has_update or has_create, "Either update_mode or create_mode should be set"
        
        # Check rules are injected
        assert instructions.get('rules') is not None, "rules should be injected"
    
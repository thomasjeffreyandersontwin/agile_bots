"""
Scope Test Helper
Handles scope filtering and assertions
"""
from helpers.base_helper import BaseHelper


class ScopeTestHelper(BaseHelper):
    """Helper for scope filtering and testing"""
    
    def filter_story_graph(self, scope_kind: str, scope_type: str, scope_value=None, behavior_name: str = None, story_graph: dict = None):
        """Filter a story graph using build/validate/action scopes."""
        graph = story_graph or self.parent.story.sample_story_graph()
        parameters = {'scope': {'type': scope_type}}
        if scope_value is not None:
            parameters['scope']['value'] = scope_value

        if scope_kind == 'build':
            from scope.action_scope import ActionScope
            return ActionScope(parameters, self.parent.bot.bot_paths).filter_story_graph(graph)
        if scope_kind == 'validate':
            from actions.validate.validation_scope import ValidationScope
            return ValidationScope(parameters, self.parent.bot.bot_paths, behavior_name).filter_story_graph(graph)
        if scope_kind in {'action', 'render'}:
            from scope.action_scope import ActionScope
            return ActionScope(parameters, self.parent.bot.bot_paths).filter_story_graph(graph)

        raise ValueError(f"Unsupported scope_kind '{scope_kind}'")
    
    def filter_story_graph_legacy(self, scope_type: str, scope_value, story_graph: dict) -> dict:
        """Filter story graph using ScopingParameter (legacy method)."""
        from scope.scoping_parameter import ScopingParameter
        scope = {'type': scope_type}
        if scope_value is not None:
            scope['value'] = scope_value
        scoping_param = ScopingParameter(scope)
        return scoping_param.filter_story_graph(story_graph)
    
    def assert_scope_is_set(self, scope_type: str, scope_value: list):
        """Assert bot scope is set with specified type and value."""
        scope = self.parent.bot.scope()
        assert scope.type.value == scope_type, f"Expected scope type '{scope_type}', got '{scope.type.value}'"
        assert scope.value == scope_value, f"Expected scope value {scope_value}, got {scope.value}"
    
    def assert_scope_is_cleared(self):
        """Assert bot scope is cleared (not active)."""
        scope = self.parent.bot.scope()
        assert scope.type.value == 'all' and len(scope.value) == 0
    
    def assert_story_graph_contains_epic(self, filtered_graph: dict, epic_name: str):
        """Assert filtered story graph contains epic."""
        epic_names = [epic.get('name') for epic in filtered_graph.get('epics', [])]
        assert epic_name in epic_names, \
            f"Expected epic '{epic_name}' not found in filtered graph. Found: {epic_names}"
    
    def assert_story_graph_contains_story(self, filtered_graph: dict, story_name: str):
        """Assert filtered story graph contains story."""
        story_names = []
        for epic in filtered_graph.get('epics', []):
            for sub_epic in epic.get('sub_epics', []):
                for story_group in sub_epic.get('story_groups', []):
                    for story in story_group.get('stories', []):
                        if isinstance(story, dict):
                            story_names.append(story.get('name'))
                        else:
                            story_names.append(story)
        assert story_name in story_names, \
            f"Expected story '{story_name}' not found in filtered graph. Found: {story_names}"
    
    def assert_story_graph_contains_increment(self, filtered_graph: dict, increment_name: str):
        """Assert filtered story graph contains increment."""
        increment_names = [inc.get('name') for inc in filtered_graph.get('increments', [])]
        assert increment_name in increment_names, \
            f"Expected increment '{increment_name}' not found in filtered graph. Found: {increment_names}"
    
    def assert_story_graph_contains_all_epics(self, filtered_graph: dict, expected_count: int):
        """Assert filtered story graph contains expected number of epics."""
        actual_count = len(filtered_graph.get('epics', []))
        assert actual_count == expected_count, \
            f"Expected {expected_count} epics, got {actual_count}"
    
    def assert_story_graph_contains_all_increments(self, filtered_graph: dict, expected_count: int):
        """Assert filtered story graph contains expected number of increments."""
        actual_count = len(filtered_graph.get('increments', []))
        assert actual_count == expected_count, \
            f"Expected {expected_count} increments, got {actual_count}"
    
    def assert_story_has_test_link(self, story: dict):
        """Assert story has test_tube icon link."""
        assert 'links' in story, "Story has no links array"
        test_links = [l for l in story['links'] if l.get('icon') == 'test_tube']
        assert len(test_links) > 0, f"Story '{story.get('name')}' has no test_tube link"
        return test_links[0]
    
    def assert_story_has_no_test_link(self, story: dict):
        """Assert story has no test_tube icon link."""
        test_links = [l for l in story.get('links', []) if l.get('icon') == 'test_tube']
        assert len(test_links) == 0, f"Story '{story.get('name')}' unexpectedly has test_tube link: {test_links}"
    
    def assert_sub_epic_has_test_link(self, sub_epic: dict):
        """Assert sub-epic has test_tube icon link."""
        assert 'links' in sub_epic, "Sub-epic has no links array"
        test_links = [l for l in sub_epic['links'] if l.get('icon') == 'test_tube']
        assert len(test_links) > 0, f"Sub-epic '{sub_epic.get('name')}' has no test_tube link"
        return test_links[0]
    
    def assert_epic_has_document_link(self, epic: dict):
        """Assert epic has document icon link."""
        assert 'links' in epic, "Epic has no links array"
        doc_links = [l for l in epic['links'] if l.get('icon') == 'document']
        assert len(doc_links) > 0, f"Epic '{epic.get('name')}' has no document link"
        return doc_links[0]

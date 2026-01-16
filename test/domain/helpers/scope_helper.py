"""
Scope Test Helper
Handles scope filtering and assertions
"""
from .base_helper import BaseHelper


class ScopeTestHelper(BaseHelper):
    """Helper for scope filtering and testing"""
    
    def filter_story_graph(self, scope_kind: str, scope_type: str, scope_value=None, behavior_name: str = None, story_graph: dict = None):
        """Filter a story graph using build/validate/action scopes."""
        graph = story_graph or self.parent.story.sample_story_graph()
        parameters = {'scope': {'type': scope_type}}
        if scope_value is not None:
            parameters['scope']['value'] = scope_value

        if scope_kind == 'build':
            from agile_bots.src.scope.action_scope import ActionScope
            return ActionScope(parameters, self.parent.bot.bot_paths).filter_story_graph(graph)
        if scope_kind == 'validate':
            from agile_bots.src.actions.validate.validation_scope import ValidationScope
            return ValidationScope(parameters, self.parent.bot.bot_paths, behavior_name).filter_story_graph(graph)
        if scope_kind in {'action', 'render'}:
            from agile_bots.src.scope.action_scope import ActionScope
            return ActionScope(parameters, self.parent.bot.bot_paths).filter_story_graph(graph)

        raise ValueError(f"Unsupported scope_kind '{scope_kind}'")
    
    def filter_story_graph_legacy(self, scope_type: str, scope_value, story_graph: dict) -> dict:
        """Filter story graph using ScopingParameter (legacy method)."""
        from agile_bots.src.scope.scoping_parameter import ScopingParameter
        scope = {'type': scope_type}
        if scope_value is not None:
            scope['value'] = scope_value
        scoping_param = ScopingParameter(scope)
        return scoping_param.filter_story_graph(story_graph)
    
    def assert_scope_is_set(self, scope_type: str, scope_value: list):
        """Assert bot scope is set with specified type and value."""
        assert self.parent.bot.scope.type == scope_type
        assert self.parent.bot.scope.value == scope_value
        assert self.parent.bot.scope.is_active()
    
    def assert_scope_is_cleared(self):
        """Assert bot scope is cleared (not active)."""
        assert not self.parent.bot.scope.is_active()
        assert self.parent.bot.scope.type is None
    
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

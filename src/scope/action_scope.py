from pathlib import Path
from typing import Dict, Any, List, Optional, Set, TYPE_CHECKING
from bot_path import BotPath
from scope.scoping_parameter import ScopingParameter
from story_graph.nodes import StoryMap, Story

if TYPE_CHECKING:
    from actions.action_context import ScopeActionContext

class ActionScope:

    def __init__(self, parameters: Dict[str, Any], bot_paths: Optional[BotPath]=None):
        self._parameters = parameters or {}
        self._bot_paths = bot_paths
        self._scope_config: Dict[str, Any] = {}
        self._build_scope()
    
    @classmethod
    def from_context(cls, context: 'ScopeActionContext', bot_paths: Optional[BotPath] = None) -> 'ActionScope':
        params = {}
        if context.scope:
            params['scope'] = context.scope.to_dict()
        
        return cls(params, bot_paths)

    def _handle_scope_parameter(self, scope_value: Any) -> None:
        if not isinstance(scope_value, dict):
            return
        
        scope_type = scope_value.get('type')
        scope_val = scope_value.get('value')
        
        if scope_type == 'all':
            self._scope_config['all'] = True
            return
        
        if scope_type == 'story':
            self._scope_config['story_names'] = scope_val if isinstance(scope_val, list) else [scope_val]
            return
        
        if scope_type == 'epic':
            self._scope_config['epic_names'] = scope_val if isinstance(scope_val, list) else [scope_val]
            return
        
        if scope_type == 'increment':
            self._handle_increment_scope(scope_val)

    def _handle_increment_scope(self, scope_val: Any) -> None:
        if not scope_val:
            return
        
        if isinstance(scope_val, int):
            self._scope_config['increment_priorities'] = [scope_val]
            return
        
        if isinstance(scope_val, str):
            self._scope_config['increment_names'] = [scope_val]
            return
        
        if isinstance(scope_val, list) and len(scope_val) > 0:
            if isinstance(scope_val[0], int):
                self._scope_config['increment_priorities'] = scope_val
            else:
                self._scope_config['increment_names'] = scope_val

    def _build_scope(self):
        if 'scope' in self._parameters:
            self._handle_scope_parameter(self._parameters['scope'])
        for key, value in self._parameters.items():
            if value is None or key == 'scope':
                continue
            self._handle_custom_parameter(key, value)
        
        if not self._scope_config:
            self._scope_config['all'] = True

    def _handle_custom_parameter(self, key: str, value: Any):
        self._scope_config[key] = value

    @property
    def scope(self) -> Dict[str, Any]:
        return self._scope_config

    def get_story_names(self, story_graph: Dict[str, Any]) -> Optional[Set[str]]:
        if self._scope_config.get('all') is True or not self._scope_config:
            return None
        
        story_map = StoryMap(story_graph)
        story_names = set()
        
        self._collect_story_names_from_scope(story_names)
        self._collect_story_names_from_epics(story_map, story_names)
        self._collect_story_names_from_increments(story_graph, story_names)
        
        return story_names if story_names else None

    def _collect_story_names_from_scope(self, story_names: Set[str]) -> None:
        if 'story_names' not in self._scope_config:
            return
        requested_names = self._scope_config['story_names']
        if isinstance(requested_names, list):
            story_names.update(requested_names)
        elif isinstance(requested_names, str):
            story_names.add(requested_names)

    def _collect_story_names_from_epics(self, story_map: StoryMap, story_names: Set[str]) -> None:
        if 'epic_names' not in self._scope_config:
            return
        epic_names = self._scope_config['epic_names']
        epic_names_list = epic_names if isinstance(epic_names, list) else [epic_names]
        for epic_name in epic_names_list:
            epic = story_map.find_epic_by_name(epic_name)
            if epic:
                story_names.update(s.name for s in epic.all_stories)

    def _collect_story_names_from_increments(self, story_graph: Dict[str, Any], story_names: Set[str]) -> None:
        if 'increment_priorities' in self._scope_config:
            priorities = self._scope_config['increment_priorities']
            priorities_list = priorities if isinstance(priorities, list) else [priorities]
            for priority in priorities_list:
                story_names.update(self._find_increment_stories_by_priority(story_graph, priority))
        
        if 'increment_names' in self._scope_config:
            names = self._scope_config['increment_names']
            names_list = names if isinstance(names, list) else [names]
            for name in names_list:
                story_names.update(self._find_increment_stories_by_name(story_graph, name))

    def _find_increment_stories_by_priority(self, story_graph: Dict[str, Any], priority: int) -> Set[str]:
        increments = story_graph.get('increments', [])
        for increment in increments:
            if increment.get('priority') == priority:
                return self._extract_story_names_from_increment(increment)
        return set()

    def _find_increment_stories_by_name(self, story_graph: Dict[str, Any], increment_name: str) -> Set[str]:
        increments = story_graph.get('increments', [])
        for increment in increments:
            if increment.get('name') == increment_name:
                return self._extract_story_names_from_increment(increment)
        return set()

    def _extract_story_names_from_increment(self, increment: Dict[str, Any]) -> Set[str]:
        story_names = set()
        stories = increment.get('stories', [])
        for story in stories:
            if isinstance(story, dict):
                story_names.add(story['name'])
            elif isinstance(story, str):
                story_names.add(story)
        return story_names

    def filter_story_graph(self, story_graph: Dict[str, Any]) -> Dict[str, Any]:
        if 'scope' not in self._parameters:
            return story_graph
        scope_param = ScopingParameter(self._parameters['scope'])
        return scope_param.filter_story_graph(story_graph)
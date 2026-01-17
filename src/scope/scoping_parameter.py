from typing import Dict, Any, List, Optional, Set

class ScopingParameter:
    def __init__(self, scope: Dict[str, Any]):
        self._scope_type = scope.get('type')
        self._scope_value = scope.get('value')

    def filter_story_graph(self, story_graph: Dict[str, Any]) -> Dict[str, Any]:
        if self._is_all_scope():
            return story_graph
        
        if self._is_story_scope():
            self._filter_by_story_names(story_graph, self._scope_value)
            return story_graph
        
        if self._is_epic_scope():
            self._filter_by_epic_names(story_graph, self._scope_value)
            return story_graph
        
        if self._is_increment_scope():
            self._filter_by_increment(story_graph, self._scope_value)
            return story_graph
        
        return story_graph

    def _is_all_scope(self) -> bool:
        return self._scope_type == 'all' or not self._scope_type

    def _is_story_scope(self) -> bool:
        return self._scope_type == 'story'

    def _is_epic_scope(self) -> bool:
        return self._scope_type == 'epic'

    def _is_increment_scope(self) -> bool:
        return self._scope_type == 'increment'

    def _filter_by_story_names(self, story_graph: Dict[str, Any], story_names: Any) -> None:
        story_name_set = self._to_string_set(story_names)
        story_graph['epics'] = self._filter_epics_by_story_names(
            story_graph.get('epics', []), story_name_set)
        story_graph['increments'] = self._filter_increments_by_story_names(
            story_graph.get('increments', []), story_name_set)

    def _filter_by_epic_names(self, story_graph: Dict[str, Any], epic_names: Any) -> None:
        epic_name_set = self._to_string_set(epic_names)
        story_graph['epics'] = self._filter_epics_by_names(
            story_graph.get('epics', []), epic_name_set)
        story_graph['increments'] = self._filter_increments_by_epic_names(
            story_graph.get('increments', []), epic_name_set)

    def _filter_by_increment(self, story_graph: Dict[str, Any], increment_value: Any) -> None:
        if self._is_priority_list(increment_value):
            self._filter_by_increment_priorities(story_graph, increment_value)
        else:
            self._filter_by_increment_names(story_graph, increment_value)

    def _filter_by_increment_priorities(self, story_graph: Dict[str, Any], priorities: List[int]) -> None:
        priority_set = self._to_int_set(priorities)
        matching_story_names = self._extract_stories_from_matching_increments(
            story_graph.get('increments', []), priority_set)
        story_graph['epics'] = self._filter_epics_by_story_names(
            story_graph.get('epics', []), matching_story_names)
        story_graph['increments'] = self._filter_increments_by_priorities(
            story_graph.get('increments', []), priority_set)

    def _filter_by_increment_names(self, story_graph: Dict[str, Any], increment_names: Any) -> None:
        name_set = self._to_string_set(increment_names)
        matching_story_names = self._extract_stories_from_matching_increments(
            story_graph.get('increments', []), name_set)
        story_graph['epics'] = self._filter_epics_by_story_names(
            story_graph.get('epics', []), matching_story_names)
        story_graph['increments'] = self._filter_increments_by_names(
            story_graph.get('increments', []), name_set)

    def _to_string_set(self, value: Any) -> Set[str]:
        return self._to_set(value)

    def _to_int_set(self, value: Any) -> Set[int]:
        return self._to_set(value)

    def _to_set(self, value: Any) -> Set[Any]:
        if isinstance(value, list):
            return set(value)
        return {value}

    def _is_priority_list(self, value: Any) -> bool:
        if not value or not isinstance(value, list) or len(value) == 0:
            return False
        return isinstance(value[0], int)

    def _filter_epics_by_story_names(self, epics: List[Dict[str, Any]], story_name_set: Set[str]) -> List[Dict[str, Any]]:
        filtered = []
        for epic in epics:
            filtered_epic = self._filter_epic_by_story_names(epic, story_name_set)
            if filtered_epic:
                filtered.append(filtered_epic)
        return filtered

    def _filter_epic_by_story_names(self, epic: Dict[str, Any], story_name_set: Set[str]) -> Optional[Dict[str, Any]]:
        epic['sub_epics'] = self._filter_sub_epics_by_story_names(
            epic.get('sub_epics', []), story_name_set)
        if 'story_groups' in epic:
            epic['story_groups'] = self._filter_story_groups_by_names(
                epic.get('story_groups', []), story_name_set)
        if self._epic_has_content(epic):
            return epic
        return None

    def _filter_sub_epics_by_story_names(self, sub_epics: List[Dict[str, Any]], story_name_set: Set[str]) -> List[Dict[str, Any]]:
        filtered = []
        for sub_epic in sub_epics:
            filtered_sub_epic = self._filter_sub_epic_by_story_names(sub_epic, story_name_set)
            if filtered_sub_epic:
                filtered.append(filtered_sub_epic)
        return filtered

    def _filter_sub_epic_by_story_names(self, sub_epic: Dict[str, Any], story_name_set: Set[str]) -> Optional[Dict[str, Any]]:
        if 'story_groups' in sub_epic:
            sub_epic['story_groups'] = self._filter_story_groups_by_names(
                sub_epic.get('story_groups', []), story_name_set)
        if 'sub_epics' in sub_epic:
            sub_epic['sub_epics'] = self._filter_sub_epics_by_story_names(
                sub_epic.get('sub_epics', []), story_name_set)
        if self._sub_epic_has_content(sub_epic):
            return sub_epic
        return None

    def _filter_story_groups_by_names(self, story_groups: List[Dict[str, Any]], story_name_set: Set[str]) -> List[Dict[str, Any]]:
        filtered = []
        for group in story_groups:
            filtered_stories = self._filter_stories_by_names(group.get('stories', []), story_name_set)
            if filtered_stories:
                group['stories'] = filtered_stories
                filtered.append(group)
        return filtered

    def _filter_stories_by_names(self, stories: List[Any], story_name_set: Set[str]) -> List[Any]:
        filtered = []
        for story in stories:
            if self._story_matches_name(story, story_name_set):
                filtered.append(story)
        return filtered

    def _story_matches_name(self, story: Any, story_name_set: Set[str]) -> bool:
        if isinstance(story, dict):
            return story.get('name') in story_name_set
        return story in story_name_set

    def _epic_has_content(self, epic: Dict[str, Any]) -> bool:
        return bool(epic.get('sub_epics') or epic.get('story_groups'))

    def _sub_epic_has_content(self, sub_epic: Dict[str, Any]) -> bool:
        return bool(sub_epic.get('story_groups') or sub_epic.get('sub_epics'))

    def _filter_epics_by_names(self, epics: List[Dict[str, Any]], epic_name_set: Set[str]) -> List[Dict[str, Any]]:
        return [epic for epic in epics if epic.get('name') in epic_name_set]

    def _filter_increments_by_epic_names(self, increments: List[Dict[str, Any]], epic_name_set: Set[str]) -> List[Dict[str, Any]]:
        filtered = []
        for increment in increments:
            filtered_increment = self._filter_increment_by_epic_names(increment, epic_name_set)
            if filtered_increment:
                filtered.append(filtered_increment)
        return filtered

    def _filter_increment_by_epic_names(self, increment: Dict[str, Any], epic_name_set: Set[str]) -> Optional[Dict[str, Any]]:
        increment['epics'] = [
            epic for epic in increment.get('epics', [])
            if epic.get('name') in epic_name_set
        ]
        if increment.get('epics'):
            return increment
        return None

    def _filter_increments_by_story_names(self, increments: List[Dict[str, Any]], story_name_set: Set[str]) -> List[Dict[str, Any]]:
        filtered = []
        for increment in increments:
            filtered_increment = self._filter_increment_by_story_names(increment, story_name_set)
            if filtered_increment:
                filtered.append(filtered_increment)
        return filtered

    def _filter_increment_by_story_names(self, increment: Dict[str, Any], story_name_set: Set[str]) -> Optional[Dict[str, Any]]:
        increment['epics'] = self._filter_increment_epics_by_story_names(
            increment.get('epics', []), story_name_set)
        if 'stories' in increment:
            increment['stories'] = self._filter_stories_by_names(
                increment.get('stories', []), story_name_set)
        if self._increment_has_content(increment):
            return increment
        return None

    def _filter_increment_epics_by_story_names(self, epics: List[Dict[str, Any]], story_name_set: Set[str]) -> List[Dict[str, Any]]:
        filtered = []
        for epic in epics:
            filtered_epic = self._filter_increment_epic_by_story_names(epic, story_name_set)
            if filtered_epic:
                filtered.append(filtered_epic)
        return filtered

    def _filter_increment_epic_by_story_names(self, epic: Dict[str, Any], story_name_set: Set[str]) -> Optional[Dict[str, Any]]:
        epic['sub_epics'] = self._filter_increment_sub_epics_by_story_names(
            epic.get('sub_epics', []), story_name_set)
        
        if epic.get('sub_epics'):
            return epic
        return None

    def _filter_increment_sub_epics_by_story_names(self, sub_epics: List[Dict[str, Any]], story_name_set: Set[str]) -> List[Dict[str, Any]]:
        filtered = []
        for sub_epic in sub_epics:
            filtered_sub_epic = self._filter_increment_sub_epic_by_story_names(sub_epic, story_name_set)
            if filtered_sub_epic:
                filtered.append(filtered_sub_epic)
        return filtered
    
    def _filter_increment_sub_epic_by_story_names(self, sub_epic: Dict[str, Any], story_name_set: Set[str]) -> Optional[Dict[str, Any]]:
        sub_epic['stories'] = self._filter_stories_by_names(
            sub_epic.get('stories', []), story_name_set)
        
        sub_epic['story_groups'] = self._filter_story_groups_by_names(
            sub_epic.get('story_groups', []), story_name_set)
        
        if sub_epic.get('stories') or sub_epic.get('story_groups'):
            return sub_epic
        return None

    def _increment_has_content(self, increment: Dict[str, Any]) -> bool:
        return bool(increment.get('epics') or increment.get('stories'))

    def _filter_increments_by_priorities(self, increments: List[Dict[str, Any]], priority_set: Set[int]) -> List[Dict[str, Any]]:
        return [increment for increment in increments if self._matches_priority(increment, priority_set)]

    def _filter_increments_by_names(self, increments: List[Dict[str, Any]], name_set: Set[str]) -> List[Dict[str, Any]]:
        return [increment for increment in increments if self._matches_name(increment, name_set)]

    def _matches_priority(self, increment: Dict[str, Any], priority_set: Set[int]) -> bool:
        inc_priority = increment.get('priority')
        if isinstance(inc_priority, str):
            priority_map = {'NOW': 1, 'LATER': 2, 'SOON': 1, 'NEXT': 2}
            inc_priority = priority_map.get(inc_priority, 999)
        return inc_priority in priority_set

    def _matches_name(self, increment: Dict[str, Any], name_set: Set[str]) -> bool:
        return increment.get('name') in name_set

    def _extract_stories_from_matching_increments(
        self, increments: List[Dict[str, Any]], match_set: Set[Any]) -> Set[str]:
        story_names = set()
        is_priority_match = False
        if match_set:
            first_elem = next(iter(match_set))
            is_priority_match = isinstance(first_elem, int)
        
        for increment in increments:
            if is_priority_match:
                if self._matches_priority(increment, match_set):
                    story_names.update(self._extract_story_names_from_increment(increment))
            else:
                if self._matches_name(increment, match_set):
                    story_names.update(self._extract_story_names_from_increment(increment))
        return story_names

    def _extract_story_names_from_increment(self, increment: Dict[str, Any]) -> Set[str]:
        story_names = set()
        self._add_direct_stories(increment, story_names)
        self._add_epic_stories(increment, story_names)
        return story_names
    
    def _add_direct_stories(self, increment: Dict[str, Any], story_names: Set[str]) -> None:
        for story in increment.get('stories', []):
            self._add_story_name(story, story_names)
    
    def _add_epic_stories(self, increment: Dict[str, Any], story_names: Set[str]) -> None:
        for epic in increment.get('epics', []):
            for sub_epic in epic.get('sub_epics', []):
                for story in sub_epic.get('stories', []):
                    self._add_story_name(story, story_names)
                
                for story_group in sub_epic.get('story_groups', []):
                    for story in story_group.get('stories', []):
                        self._add_story_name(story, story_names)
    
    def _add_story_name(self, story: Any, story_names: Set[str]) -> None:
        if isinstance(story, dict):
            story_names.add(story.get('name'))
        elif isinstance(story, str):
            story_names.add(story)


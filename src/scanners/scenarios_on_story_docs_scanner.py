
from typing import List, Dict, Any, Optional, Set
from story_scanner import StoryScanner
from story_map import StoryNode, Story, StoryMap
from scanners.violation import Violation

def _get_story_names_from_scope(story_graph: Dict[str, Any]) -> Set[str]:
    scope_config = story_graph.get('_validation_scope', {})
    
    if scope_config.get('all') is True:
        return None
    
    if not scope_config:
        return None
    
    story_map = StoryMap(story_graph)
    story_names = set()
    
    if 'story_names' in scope_config:
        story_names_list = scope_config['story_names']
        if isinstance(story_names_list, list):
            story_names.update(story_names_list)
        elif isinstance(story_names_list, str):
            story_names.add(story_names_list)
    
    if 'epic_names' in scope_config:
        epic_names_list = scope_config['epic_names']
        epic_names_list = epic_names_list if isinstance(epic_names_list, list) else [epic_names_list]
        for epic_name in epic_names_list:
            epic = story_map.find_epic_by_name(epic_name)
            if epic:
                story_names.update(s.name for s in epic.all_stories)
    
    if 'increment_priorities' in scope_config:
        priorities = scope_config['increment_priorities']
        priorities = priorities if isinstance(priorities, list) else [priorities]
        for priority in priorities:
            story_names.update(_get_increment_story_names(story_graph, priority))
    
    if 'story_names' in scope_config or 'increment_priorities' in scope_config or 'epic_names' in scope_config:
        return story_names
    
    return None

def _get_increment_story_names(story_graph: Dict[str, Any], priority: int) -> Set[str]:
    increments = story_graph.get('increments', [])
    for increment in increments:
        inc_priority = increment.get('priority', 999)
        if isinstance(inc_priority, str):
            priority_map = {'NOW': 1, 'LATER': 2, 'SOON': 1, 'NEXT': 2}
            inc_priority = priority_map.get(inc_priority.upper(), 999)
        if inc_priority == priority:
            return _extract_story_names_from_increment(increment)
    return set()

def _extract_story_names_from_increment(increment_data: Dict[str, Any]) -> Set[str]:
    story_names = set()
    for story in increment_data.get('stories', []):
        if isinstance(story, dict) and 'name' in story:
            story_names.add(story['name'])
        elif isinstance(story, str):
            story_names.add(story)
    for epic in increment_data.get('epics', []):
        story_names.update(_extract_story_names_from_epic(epic))
    return story_names

def _extract_story_names_from_epic(epic_data: Dict[str, Any]) -> Set[str]:
    story_names = set()
    for story in epic_data.get('stories', []):
        if isinstance(story, dict) and 'name' in story:
            story_names.add(story['name'])
        elif isinstance(story, str):
            story_names.add(story)
    for story_group in epic_data.get('story_groups', []):
        for story in story_group.get('stories', []):
            if isinstance(story, dict) and 'name' in story:
                story_names.add(story['name'])
            elif isinstance(story, str):
                story_names.add(story)
    for sub_epic in epic_data.get('sub_epics', []):
        story_names.update(_extract_story_names_from_epic(sub_epic))
    return story_names

class ScenariosOnStoryDocsScanner(StoryScanner):
    
    def __init__(self):
        super().__init__()
        self._in_scope_story_names: Optional[Set[str]] = None
    
    def scan(
        self, 
        story_graph: Dict[str, Any], 
        rule_obj: Any = None,
        test_files: Optional[List['Path']] = None,
        code_files: Optional[List['Path']] = None,
        on_file_scanned: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        self._in_scope_story_names = _get_story_names_from_scope(story_graph)
        
        return super().scan(story_graph, rule_obj, test_files=test_files, code_files=code_files)
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, Story):
            if self._in_scope_story_names is not None:
                if node.name not in self._in_scope_story_names:
                    return violations
            
            story_data = node.data
            scenarios = story_data.get('scenarios', [])
            scenario_outlines = story_data.get('scenario_outlines', [])
            
            has_scenarios = scenarios and len(scenarios) > 0
            has_scenario_outlines = scenario_outlines and len(scenario_outlines) > 0
            
            if not has_scenarios and not has_scenario_outlines:
                location = node.map_location()
                violation = Violation(
                    rule=rule_obj,
                    violation_message=f'Story "{node.name}" has no scenarios or scenario_outlines in story-graph.json - scenarios should be in JSON (scenarios or scenario_outlines fields)',
                    location=location,
                    severity='error'
                ).to_dict()
                violations.append(violation)
        
        return violations

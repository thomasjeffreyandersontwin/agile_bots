from typing import List, Dict, Any, Optional
from story_scanner import StoryScanner
from story_map import StoryNode, Epic, SubEpic, Story
from scanners.violation import Violation

class ExhaustiveDecompositionScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, Epic):
            violation = self._check_epic_has_sub_epics_or_stories(node)
            if violation:
                violations.append(violation)
        
        elif isinstance(node, SubEpic):
            violation = self._check_sub_epic_has_stories(node)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_epic_has_sub_epics_or_stories(self, epic: Epic) -> Optional[Dict[str, Any]]:
        has_sub_epics = len(epic.data.get('sub_epics', [])) > 0
        has_story_groups = len(epic.data.get('story_groups', [])) > 0
        
        if not has_sub_epics and not has_story_groups:
            location = epic.map_location()
            return Violation(
                rule=self.rule,
                violation_message=f'Epic "{epic.name}" must have sub-epics or story groups (exhaustive decomposition)',
                location=location,
                severity='error'
            ).to_dict()
        
        return None
    
    def _check_sub_epic_has_stories(self, sub_epic: SubEpic) -> Optional[Dict[str, Any]]:
        has_nested_sub_epics = len(sub_epic.data.get('sub_epics', [])) > 0
        has_story_groups = len(sub_epic.data.get('story_groups', [])) > 0
        
        if not has_nested_sub_epics and not has_story_groups:
            location = sub_epic.map_location()
            return Violation(
                rule=self.rule,
                violation_message=f'Sub-epic "{sub_epic.name}" must have nested sub-epics or story groups (exhaustive decomposition)',
                location=location,
                severity='error'
            ).to_dict()
        
        return None


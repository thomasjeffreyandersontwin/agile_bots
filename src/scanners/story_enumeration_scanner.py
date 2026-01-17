
from typing import List, Dict, Any, Optional
from story_scanner import StoryScanner
from story_map import StoryNode, Epic, SubEpic
from scanners.violation import Violation
import re

class StoryEnumerationScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, Epic):
            epic_data = node.data
            
            estimated_stories = epic_data.get('estimated_stories')
            if estimated_stories:
                if isinstance(estimated_stories, str) and '~' in str(estimated_stories):
                    location = node.map_location('estimated_stories')
                    violation = Violation(
                        rule=self.rule,
                        violation_message=f'Epic "{node.name}" uses "~{estimated_stories}" notation - all stories must be explicitly enumerated, not estimated',
                        location=location,
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
            
            sub_epics = epic_data.get('sub_epics', [])
            for sub_epic_idx, sub_epic_data in enumerate(sub_epics):
                violation = self._check_sub_epic_stories(sub_epic_data, node, sub_epic_idx)
                if violation:
                    violations.append(violation)
        
        return violations
    
    def _check_sub_epic_stories(self, sub_epic_data: Dict[str, Any], epic_node: StoryNode, sub_epic_idx: int) -> Optional[Dict[str, Any]]:
        sub_epic_name = sub_epic_data.get('name', '')
        
        description = sub_epic_data.get('description', '')
        if '~' in description and re.search(r'~\d+\s+stories?', description, re.IGNORECASE):
            location = f"{epic_node.map_location()}.sub_epics[{sub_epic_idx}]"
            return Violation(
                rule=self.rule,
                violation_message=f'Sub-epic "{sub_epic_name}" uses "~X stories" notation in description - all stories must be explicitly enumerated',
                location=location,
                severity='error'
            ).to_dict()
        
        story_groups = sub_epic_data.get('story_groups', [])
        if not story_groups or len(story_groups) == 0:
            location = f"{epic_node.map_location()}.sub_epics[{sub_epic_idx}]"
            return Violation(
                rule=self.rule,
                violation_message=f'Sub-epic "{sub_epic_name}" has no story_groups - all stories must be explicitly enumerated',
                location=location,
                severity='error'
            ).to_dict()
        
        return None


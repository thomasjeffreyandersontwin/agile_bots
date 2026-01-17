from typing import List, Dict, Any, Optional
from story_scanner import StoryScanner
from story_map import StoryNode, Epic, SubEpic, Story
from scanners.violation import Violation
import re

class StorySizingScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, SubEpic):
            violation = self._check_sub_epic_story_count(node, rule_obj)
            if violation:
                violations.append(violation)
        
        elif isinstance(node, Story):
            violation = self._check_story_acceptance_criteria_count(node, rule_obj)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_sub_epic_story_count(self, sub_epic: SubEpic, rule_obj: Any) -> Optional[Dict[str, Any]]:
        story_groups = sub_epic.data.get('story_groups', [])
        
        if not story_groups:
            return None
        
        total_stories = 0
        for story_group in story_groups:
            stories = story_group.get('stories', [])
            total_stories += len(stories)
        
        if total_stories == 0:
            return None
        
        count = total_stories
        severity, message = self._get_size_violation(count, 'stories')
        
        if severity:
            location = sub_epic.map_location()
            return Violation(
                rule=rule_obj,
                violation_message=f'Sub-epic "{sub_epic.name}" has {count} {message}',
                location=location,
                severity=severity
            ).to_dict()
        
        return None
    
    def _check_story_acceptance_criteria_count(self, story: Story, rule_obj: Any) -> Optional[Dict[str, Any]]:
        acceptance_criteria = story.data.get('acceptance_criteria', [])
        
        if not acceptance_criteria:
            return None
        
        count = self._count_when_then_and(acceptance_criteria)
        
        if count == 0:
            return None
        
        severity, message = self._get_size_violation(count, 'acceptance criteria')
        
        if severity:
            location = story.map_location('acceptance_criteria')
            return Violation(
                rule=rule_obj,
                violation_message=f'Story "{story.name}" has {count} {message}',
                location=location,
                severity=severity
            ).to_dict()
        
        return None
    
    def _count_when_then_and(self, acceptance_criteria: List) -> int:
        combined_text = ' '.join([self._get_ac_text(ac) for ac in acceptance_criteria])
        
        text = re.sub(r'\(AC\)\s*', '', combined_text, flags=re.IGNORECASE)
        
        when_count = len(re.findall(r'\bWHEN\b', text, re.IGNORECASE))
        and_count = len(re.findall(r'\bAND\b', text, re.IGNORECASE))
        
        return when_count + and_count
    
    def _get_ac_text(self, ac: Any) -> str:
        if isinstance(ac, dict):
            return ac.get('criterion', '') or ac.get('description', '') or str(ac)
        return str(ac)
    
    def _get_size_violation(self, count: int, item_type: str) -> tuple[Optional[str], str]:
        if 4 <= count <= 10:
            return None, f'{count} {item_type} (perfect)'
        elif count == 3 or count == 11:
            return 'warning', f'{count} {item_type} (should be 4-10)'
        elif count <= 2 or count >= 12:
            return 'error', f'{count} {item_type} (should be 4-10)'
        else:
            return 'warning', f'{count} {item_type} (should be 4-10)'

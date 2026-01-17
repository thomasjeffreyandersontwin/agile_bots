
from typing import List, Dict, Any, Optional
from pathlib import Path
from story_scanner import StoryScanner
from story_map import StoryNode, Epic, SubEpic, Story
from scanners.violation import Violation
import re

class IncrementFolderStructureScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, Epic):
            epic_name = node.name
            if not epic_name:
                return violations
            
            has_stories_with_scenarios = self._epic_has_stories_with_scenarios(node)
            
            if has_stories_with_scenarios:
                violation = self._check_epic_folder_structure(node)
                if violation:
                    violations.append(violation)
        
        return violations
    
    def _epic_has_stories_with_scenarios(self, epic: Epic) -> bool:
        for child in epic.children:
            if isinstance(child, Story):
                story_data = child.data
                scenarios = story_data.get('scenarios', [])
                if scenarios:
                    return True
        return False
    
    def _check_epic_folder_structure(self, node: StoryNode) -> Optional[Dict[str, Any]]:
        epic_name = node.name
        expected_folder = f"🎯 {epic_name}"
        
        
        if not epic_name.startswith('🎯'):
            pass
        
        return None


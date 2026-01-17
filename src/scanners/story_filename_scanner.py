
from typing import List, Dict, Any, Optional
from pathlib import Path
from story_scanner import StoryScanner
from story_map import StoryNode, Story
from scanners.violation import Violation
import re

class StoryFilenameScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, Story):
            story_name = node.name
            if not story_name:
                return violations
            
            
            violation = self._check_actor_in_story_name(node)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_actor_in_story_name(self, node: StoryNode) -> Optional[Dict[str, Any]]:
        name = node.name
        actor_prefixes = [
            'AI Chat', 'Router', 'Bot Behavior', 'GatherContextAction',
            'Agent', 'System', 'User', 'Admin', 'Customer'
        ]
        
        for prefix in actor_prefixes:
            if story_name.startswith(prefix + ' '):
                location = node.map_location()
                return Violation(
                    rule=self.rule,
                    violation_message=f'Story name "{story_name}" starts with actor prefix "{prefix}" - actor information should be in description/AC, not in story name/filename',
                    location=location,
                    severity='error'
                ).to_dict()
        
        return None


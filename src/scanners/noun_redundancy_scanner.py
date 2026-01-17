
from typing import List, Dict, Any
from story_scanner import StoryScanner
from story_map import StoryNode
from scanners.violation import Violation
import re

class NounRedundancyScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations = []
        
        if not hasattr(node, 'name') or not node.name:
            return violations
        
        name = node.name
        
        words = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]+\b', name)
        
        if len(words) >= 2:
            pass
        
        if re.search(r'\d+|System|Component|Module|Manager|Handler', name, re.IGNORECASE):
            base_name = re.sub(r'\s+(System|Component|Module|Manager|Handler|\d+)$', '', name, flags=re.IGNORECASE)
            if base_name and base_name != name:
                violation = Violation(
                    rule=self.rule,
                    violation_message=f'Story element "{name}" may have redundant noun - consider integrating with related concepts instead of using qualifiers',
                    location=node.name,
                    severity='warning'
                ).to_dict()
                violations.append(violation)
        
        return violations



from typing import List, Dict, Any
from story_scanner import StoryScanner
from story_map import StoryNode, Story
from scanners.violation import Violation
import re

class ImplementationDetailsScanner(StoryScanner):
    
    IMPLEMENTATION_VERBS = [
        'serialize', 'deserialize', 'convert', 'transform', 'format',
        'calculate', 'compute', 'generate', 'create',
        'apply', 'set', 'configure',
        'save', 'write', 'store'
    ]
    
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations = []
        
        if not isinstance(node, Story):
            return violations
        
        if not hasattr(node, 'name') or not node.name:
            return violations
        
        name_lower = node.name.lower()
        
        for verb in self.IMPLEMENTATION_VERBS:
            pattern = rf'\b{verb}\b'
            if re.search(pattern, name_lower):
                words = name_lower.split()
                if verb in words[0] or (len(words) > 1 and verb in words[0:2]):
                    violation = Violation(
                        rule=self.rule,
                        violation_message=f'Story "{node.name}" appears to be an implementation operation - should be a step within a story that describes user/system outcome',
                        location=node.name,
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations


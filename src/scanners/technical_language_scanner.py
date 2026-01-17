
from typing import List, Dict, Any
from story_scanner import StoryScanner
from story_map import StoryNode
from scanners.violation import Violation
import re

class TechnicalLanguageScanner(StoryScanner):
    
    TECHNICAL_VERBS = [
        'implement', 'create', 'refactor', 'optimize', 'fix', 'build', 'set up',
        'query', 'call', 'update', 'configure', 'serialize', 'deserialize',
        'convert', 'transform', 'generate', 'calculate', 'compute'
    ]
    
    TECHNICAL_PHRASES = [
        'query database', 'call api', 'update table', 'database schema',
        'api endpoints', 'query performance', 'authentication code',
        'configuration', 'xml', 'json', 'serialize', 'deserialize'
    ]
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not hasattr(node, 'name') or not node.name:
            return violations
        
        name_lower = node.name.lower()
        
        for verb in self.TECHNICAL_VERBS:
            if verb in name_lower:
                violation = Violation(
                    rule=rule_obj,
                    violation_message=f'Story element "{node.name}" uses technical implementation verb "{verb}" - use business language focusing on user experience',
                    location=node.name,
                    severity='error'
                ).to_dict()
                violations.append(violation)
                break
        
        for phrase in self.TECHNICAL_PHRASES:
            if phrase in name_lower:
                violation = Violation(
                    rule=rule_obj,
                    violation_message=f'Story element "{node.name}" uses technical implementation phrase "{phrase}" - focus on what user experiences, not how it\'s implemented',
                    location=node.name,
                    severity='error'
                ).to_dict()
                violations.append(violation)
                break
        
        return violations


from typing import List, Dict, Any, Optional
import re
from story_scanner import StoryScanner
from story_map import StoryNode, Epic, SubEpic, Story
from scanners.violation import Violation

class SpecificityScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations = []
        if not node.name:
            return violations
        
        node_type = self._get_node_type(node)
        
        violation = self._check_too_generic(node, node_type)
        if violation:
            violations.append(violation)
        
        violation = self._check_too_specific(node, node_type)
        if violation:
            violations.append(violation)
        
        return violations
    
    def _get_node_type(self, node: StoryNode) -> str:
        name = node.name
        if isinstance(node, Epic):
            return 'epic'
        elif isinstance(node, SubEpic):
            return 'sub_epic'
        elif isinstance(node, Story):
            return 'story'
        return 'unknown'
    
    def _check_too_generic(self, node: StoryNode, node_type: str) -> Optional[Dict[str, Any]]:
        name = node.name
        name_lower = name.lower()
        words = name_lower.split()
        
        if len(words) < 3:
            if len(words) == 2:
                location = node.map_location()
                return Violation(
                    rule=self.rule,
                    violation_message=f'{node_type.capitalize()} name "{name}" is too generic - add context (e.g., "Process Order Payment" not "Process Payment")',
                    location=location,
                    severity='error'
                ).to_dict()
        
        generic_patterns = [
            r'^(process|authorize|validate|refund|expose|provide)\s+\w+$',
            r'^(process|authorize|validate|refund|expose|provide)\s+\w+\s+\w+$'
        ]
        
        for pattern in generic_patterns:
            if re.match(pattern, name_lower):
                location = node.map_location()
                return Violation(
                    rule=self.rule,
                    violation_message=f'{node_type.capitalize()} name "{name}" is too generic - add specific context (e.g., "Process Order Payment" not "Process Payment")',
                    location=location,
                    severity='error'
                ).to_dict()
        
        return None
    
    def _check_too_specific(self, node: StoryNode, node_type: str) -> Optional[Dict[str, Any]]:
        name = node.name
        id_patterns = [
            r'#\d+',
            r'\d{4,}',
            r'\$\d+\.\d+',
            r'order\s+#?\d+',
            r'card\s+number\s+\d',
            r'\d{4}[- ]\d{4}[- ]\d{4}[- ]\d{4}',
        ]
        
        for pattern in id_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                location = node.map_location()
                return Violation(
                    rule=self.rule,
                    violation_message=f'{node_type.capitalize()} name "{name}" is too specific - remove IDs, numbers, or detailed context (e.g., "Process Order Payment" not "User processes payment for order #12345")',
                    location=location,
                    severity='error'
                ).to_dict()
        
        if 'for order' in name.lower() or 'for order #' in name.lower():
            location = node.map_location()
            return Violation(
                rule=self.rule,
                violation_message=f'{node_type.capitalize()} name "{name}" is too specific - remove order references (e.g., "Process Order Payment" not "Process payment for order #12345")',
                location=location,
                severity='error'
            ).to_dict()
        
        if 'when ' in name.lower() and len(name.split()) > 6:
            location = node.map_location()
            return Violation(
                rule=self.rule,
                violation_message=f'{node_type.capitalize()} name "{name}" is too specific - remove temporal context (e.g., "Process Order Payment" not "Process payment when customer completes checkout")',
                location=location,
                severity='error'
            ).to_dict()
        
        return None
    
    def scan_domain_concept(self, node: Any) -> List[Dict[str, Any]]:
        return []


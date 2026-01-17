from typing import List, Dict, Any, Optional
from story_scanner import StoryScanner
from scanners.story_map import StoryNode, Epic, SubEpic, Story
from scanners.violation import Violation

class CommunicationVerbScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations = []
        if not node.name:
            return violations
        
        node_type = self._get_node_type(node)
        
        violation = self._check_communication_verbs(node, node_type)
        if violation:
            violations.append(violation)
        
        violation = self._check_enablement_verbs(node, node_type)
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
    
    def _check_communication_verbs(self, node: StoryNode, node_type: str) -> Optional[Dict[str, Any]]:
        communication_verbs = ['showing', 'displaying', 'visualizing', 'presenting', 'rendering']
        return self._check_verb_usage(
            node, 
            node_type, 
            communication_verbs, 
            'communication',
            'Creates Animation" not "Showing Animation'
        )
    
    def _check_enablement_verbs(self, node: StoryNode, node_type: str) -> Optional[Dict[str, Any]]:
        enablement_verbs = ['providing', 'enabling', 'allowing', 'supporting', 'facilitating']
        return self._check_verb_usage(
            node, 
            node_type, 
            enablement_verbs, 
            'enablement',
            'Creates Configuration" not "Providing Configuration'
        )
    
    def _check_verb_usage(
        self, 
        node: StoryNode, 
        node_type: str, 
        verb_list: List[str], 
        verb_category: str,
        example: str
    ) -> Optional[Dict[str, Any]]:
        name = node.name
        name_lower = name.lower()
        words = name_lower.split()
        
        for word in words:
            if word in verb_list:
                location = node.map_location()
                return Violation(
                    rule=self.rule,
                    violation_message=f'{node_type.capitalize()} name "{name}" uses {verb_category} verb "{word}" - use outcome verbs instead (e.g., "{example}")',
                    location=location,
                    severity='error'
                ).to_dict()
        
        return None


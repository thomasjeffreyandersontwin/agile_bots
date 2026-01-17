from typing import List, Dict, Any, Optional
from story_scanner import StoryScanner
from story_map import StoryNode, Epic, SubEpic, Story
from scanners.violation import Violation

class GenericCapabilityScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        name = node.name
        
        if not name:
            return violations
        
        node_type = self._get_node_type(node)
        
        violation = self._check_capability_verbs(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_passive_states(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        violation = self._check_generic_technical_verbs(name, node, node_type, rule_obj)
        if violation:
            violations.append(violation)
        
        return violations
    
    def _get_node_type(self, node: StoryNode) -> str:
        if isinstance(node, Epic):
            return 'epic'
        elif isinstance(node, SubEpic):
            return 'sub_epic'
        elif isinstance(node, Story):
            return 'story'
        return 'unknown'
    
    def _check_verb_pattern(
        self, 
        name: str, 
        node: StoryNode, 
        node_type: str, 
        rule_obj: Any,
        verb_list: List[str],
        verb_category: str,
        message_template: str
    ) -> Optional[Dict[str, Any]]:
        name_lower = name.lower()
        words = name_lower.split()
        
        if words and words[0] in verb_list:
            location = node.map_location()
            return Violation(
                rule=rule_obj,
                violation_message=message_template.format(
                    node_type=node_type.capitalize(),
                    name=name,
                    verb=words[0],
                    category=verb_category
                ),
                location=location,
                severity='error'
            ).to_dict()
        
        return None
    
    def _check_capability_verbs(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        capability_verbs = ['exposes', 'provides', 'contains', 'represents', 'implements', 'supports']
        message = '{node_type} name "{name}" uses capability verb "{verb}" - describe what system DOES (behaviors), not what system IS (capabilities). Use specific actions with actors (e.g., "User invokes tool" not "Exposes tool")'
        return self._check_verb_pattern(name, node, node_type, rule_obj, capability_verbs, 'capability', message)
    
    def _check_passive_states(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        passive_patterns = ['tracks', 'maintains', 'stores', 'holds', 'keeps']
        message = '{node_type} name "{name}" uses passive state verb "{verb}" - use active behaviors instead (e.g., "User updates order count" not "Tracks order count")'
        return self._check_verb_pattern(name, node, node_type, rule_obj, passive_patterns, 'passive state', message)
    
    def _check_generic_technical_verbs(self, name: str, node: StoryNode, node_type: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        generic_technical_verbs = ['invokes', 'invoke', 'calls', 'call', 'executes', 'execute', 'triggers', 'trigger']
        technical_nouns = ['api', 'endpoint', 'service', 'method', 'function', 'handler', 'route', 'url']
        
        name_lower = name.lower()
        words = name_lower.split()
        
        if not words:
            return None
        
        first_word = words[0]
        if first_word in generic_technical_verbs:
            remaining_text = ' '.join(words[1:])
            has_technical_noun = any(tech_noun in remaining_text for tech_noun in technical_nouns)
            
            if has_technical_noun:
                location = node.map_location()
                return Violation(
                    rule=rule_obj,
                    violation_message=f'{node_type.capitalize()} name "{name}" uses generic technical verb "{first_word}" without describing outcome - describe what actually happens, not the technical mechanism (e.g., "Processes Payment" not "Invokes Payment API")',
                    location=location,
                    severity='error'
                ).to_dict()
        
        return None


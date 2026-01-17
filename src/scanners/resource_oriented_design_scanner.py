
from typing import List, Dict, Any, Optional
from domain_scanner import DomainScanner
from domain_concept_node import DomainConceptNode
from scanners.violation import Violation
from vocabulary_helper import VocabularyHelper

class ResourceOrientedDesignScanner(DomainScanner):
    
    def scan_domain_concept(self, node: DomainConceptNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        is_agent, base_verb, suffix = VocabularyHelper.is_agent_noun(node.name)
        
        if is_agent:
            suggested_name = node.name[:-len(suffix)]
            if not suggested_name:
                suggested_name = "[ResourceName]"
            
            violations.append(
                Violation(
                    rule=rule_obj,
                    violation_message=f'Domain concept "{node.name}" is an agent noun (doer of action) derived from verb "{base_verb}". Name concepts after resources (what they ARE), not actions (what they DO). Consider: "{suggested_name}" as the resource.',
                    location=node.map_location('name'),
                    line_number=None,
                    severity='error'
                ).to_dict()
            )
        
        return violations

        return violations

        return violations


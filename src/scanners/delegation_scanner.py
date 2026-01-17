
from typing import List, Dict, Any, Optional
from domain_scanner import DomainScanner
from domain_concept_node import DomainConceptNode
from scanners.violation import Violation

class DelegationScanner(DomainScanner):
    
    def scan_domain_concept(self, node: DomainConceptNode) -> List[Dict[str, Any]]:
        violations = []
        
        for i, responsibility_data in enumerate(node.responsibilities):
            responsibility_name = responsibility_data.get('name', '')
            collaborators = responsibility_data.get('collaborators', [])
            resp_lower = responsibility_name.lower()
            
            if 'find' in resp_lower and 'by' in resp_lower:
                if not self._is_collection_class(node.name):
                    violations.append(
                        Violation(
                            rule=self.rule,
                            violation_message=f'Responsibility "{responsibility_name}" may be doing what a collection class should do. Consider delegating to collection class.',
                            location=node.map_location(f'responsibilities[{i}].name'),
                            line_number=None,
                            severity='info'
                        ).to_dict()
                    )
        
        return violations
    
    def _is_collection_class(self, name: str) -> bool:
        name_lower = name.lower()
        return (name_lower.endswith('s') and len(name_lower) > 3) or 'collection' in name_lower



from typing import List, Dict, Any, Optional
from domain_scanner import DomainScanner
from domain_concept_node import DomainConceptNode
from scanners.violation import Violation

class CodeRepresentationScanner(DomainScanner):
    
    ABSTRACT_PATTERNS = [
        'concept',
        'insight',
        'pattern',
        'knowledge',
        'abstract',
    ]
    
    def scan_domain_concept(self, node: DomainConceptNode) -> List[Dict[str, Any]]:
        violations = []
        
        node_name_lower = node.name.lower()
        for pattern in self.ABSTRACT_PATTERNS:
            if pattern in node_name_lower:
                violations.append(
                    Violation(
                        rule=self.rule,
                        violation_message=f'Domain concept "{node.name}" uses abstract terminology. Domain models should represent code closely - refactor code if needed.',
                        location=node.map_location('name'),
                        line_number=None,
                        severity='info'
                    ).to_dict()
                )
                break
        
        for i, responsibility_data in enumerate(node.responsibilities):
            responsibility_name = responsibility_data.get('name', '')
            collaborators = responsibility_data.get('collaborators', [])
            
            for collab in collaborators:
                collab_lower = collab.strip().lower()
                for pattern in self.ABSTRACT_PATTERNS:
                    if pattern in collab_lower:
                        violations.append(
                            Violation(
                                rule=self.rule,
                                violation_message=f'Responsibility "{responsibility_name}" uses abstract collaborator "{collab.strip()}". Use concrete domain concepts that exist in code.',
                                location=node.map_location(f'responsibilities[{i}].collaborators'),
                                line_number=None,
                                severity='info'
                            ).to_dict()
                        )
                        break
        
        return violations


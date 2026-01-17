
from typing import List, Dict, Any, Optional
import re
from domain_scanner import DomainScanner
from domain_concept_node import DomainConceptNode
from scanners.violation import Violation

class PropertyEncapsulationScanner(DomainScanner):
    
    EXPOSED_STATE_PATTERNS = [
        r'\blist\b',
        r'\barray\b',
        r'\bdictionary\b',
        r'\bdict\b',
        r'\bset\s+',
        r'\bmodify\s+',
        r'\bupdate\s+.*list',
        r'\bexpose\s+',
    ]
    
    CALCULATE_PATTERNS = [
        r'^calculate\s+',
        r'^compute\s+',
        r'^derive\s+',
    ]
    
    def scan_domain_concept(self, node: DomainConceptNode) -> List[Dict[str, Any]]:
        violations = []
        
        for i, responsibility_data in enumerate(node.responsibilities):
            responsibility_name = responsibility_data.get('name', '')
            resp_lower = responsibility_name.lower()
            
            for pattern in self.EXPOSED_STATE_PATTERNS:
                if re.search(pattern, resp_lower):
                    violations.append(
                        Violation(
                            rule=self.rule,
                            violation_message=f'Responsibility "{responsibility_name}" exposes internal structure. Use property encapsulation instead (e.g., "Get holdings: Holdings" not "Get holdings list: List").',
                            location=node.map_location(f'responsibilities[{i}].name'),
                            line_number=None,
                            severity='warning'
                        ).to_dict()
                    )
                    break
            
            for pattern in self.CALCULATE_PATTERNS:
                if re.search(pattern, resp_lower):
                    violations.append(
                        Violation(
                            rule=self.rule,
                            violation_message=f'Responsibility "{responsibility_name}" uses calculate/compute instead of property. Use "Get X" instead of "Calculate X" to hide calculation timing.',
                            location=node.map_location(f'responsibilities[{i}].name'),
                            line_number=None,
                            severity='warning'
                        ).to_dict()
                    )
                    break
        
        return violations


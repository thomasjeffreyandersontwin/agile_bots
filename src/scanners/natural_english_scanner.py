
from typing import List, Dict, Any, Optional
import re
from domain_scanner import DomainScanner
from domain_concept_node import DomainConceptNode
from scanners.violation import Violation

class NaturalEnglishScanner(DomainScanner):
    
    TECHNICAL_NOTATION_PATTERNS = [
        r'\[0\.\.1\]',
        r'\[1\.\.\*\]',
        r'\[0\.\.\*\]',
        r'\[0\.\.\]',
        r'\[1\.\.\]',
        r'\[0,1\]',
        r'\[1,\*\]',
        r'\[0,\*\]',
        r'\[0\.\.n\]',
        r'\[1\.\.n\]',
    ]
    
    def scan_domain_concept(self, node: DomainConceptNode) -> List[Dict[str, Any]]:
        violations = []
        
        for i, responsibility_data in enumerate(node.responsibilities):
            responsibility_name = responsibility_data.get('name', '')
            for pattern in self.TECHNICAL_NOTATION_PATTERNS:
                if re.search(pattern, responsibility_name):
                    violations.append(
                        Violation(
                            rule=self.rule,
                            violation_message=f'Responsibility "{responsibility_name}" uses technical notation. Use natural English instead (e.g., "Get portfolio" not "Get portfolio [0..1]").',
                            location=node.map_location(f'responsibilities[{i}].name'),
                            line_number=None,
                            severity='warning'
                        ).to_dict()
                    )
                    break
        
        return violations


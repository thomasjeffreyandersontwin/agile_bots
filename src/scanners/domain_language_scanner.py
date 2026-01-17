
from typing import List, Dict, Any, Optional
import re
from domain_scanner import DomainScanner
from domain_concept_node import DomainConceptNode
from scanners.violation import Violation

class DomainLanguageScanner(DomainScanner):
    
    GENERIC_TERMS = [
        r'\bdata\b',
        r'\bconfig\b',
        r'\bparameter\b',
        r'\bresult\b',
        r'\bvalue\b',
    ]
    
    GENERATE_PATTERNS = [
        r'^generate\s+',
        r'^calculate\s+',
    ]
    
    def scan_domain_concept(self, node: DomainConceptNode) -> List[Dict[str, Any]]:
        violations = []
        
        node_name_lower = node.name.lower()
        for term in ['data', 'config', 'parameter', 'result']:
            if term in node_name_lower and not self._is_domain_specific(node.name):
                violations.append(
                    Violation(
                        rule=self.rule,
                        violation_message=f'Domain concept "{node.name}" uses generic term "{term}". Use domain-specific language instead (e.g., "PortfolioData" → "Portfolio", "TargetConfig" → "TargetAllocation").',
                        location=node.map_location('name'),
                        line_number=None,
                        severity='warning'
                    ).to_dict()
                )
        
        for i, responsibility_data in enumerate(node.responsibilities):
            responsibility_name = responsibility_data.get('name', '')
            collaborators = responsibility_data.get('collaborators', [])
            resp_lower = responsibility_name.lower()
            
            for collab in collaborators:
                collab_lower = collab.lower()
                for term in self.GENERIC_TERMS:
                    if term in collab_lower and not self._is_domain_specific(collab):
                        violations.append(
                            Violation(
                                rule=self.rule,
                                violation_message=f'Responsibility "{responsibility_name}" uses generic collaborator "{collab}". Use domain-specific language instead.',
                                location=node.map_location(f'responsibilities[{i}].collaborators'),
                                line_number=None,
                                severity='warning'
                            ).to_dict()
                        )
                        break
            
            for pattern in self.GENERATE_PATTERNS:
                if re.search(pattern, resp_lower):
                    violations.append(
                        Violation(
                            rule=self.rule,
                            violation_message=f'Responsibility "{responsibility_name}" uses generate/calculate. Use property instead (e.g., "Get recommended trades" not "Generate recommendation").',
                            location=node.map_location(f'responsibilities[{i}].name'),
                            line_number=None,
                            severity='warning'
                        ).to_dict()
                    )
                    break
        
        return violations
    
    def _is_domain_specific(self, name: str) -> bool:
        return len(name.split()) > 1 or name.lower() not in ['data', 'config', 'parameter', 'result']


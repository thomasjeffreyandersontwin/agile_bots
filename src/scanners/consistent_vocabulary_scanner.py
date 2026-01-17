
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
from test_scanner import TestScanner
from scanners.violation import Violation

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from collections import defaultdict

class ConsistentVocabularyScanner(TestScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        domain_terms = self._extract_domain_terms(story_graph)
        
        violations.extend(self._check_vocabulary_consistency(content, domain_terms, file_path))
        
        return violations
    
    def _extract_domain_terms(self, story_graph: Dict[str, Any]) -> List[str]:
        terms = []
        epics = story_graph.get('epics', [])
        for epic in epics:
            epic_name = epic.get('name', '')
            if epic_name:
                terms.extend(epic_name.lower().split())
            
            sub_epics = epic.get('sub_epics', [])
            for sub_epic in sub_epics:
                sub_epic_name = sub_epic.get('name', '')
                if sub_epic_name:
                    terms.extend(sub_epic_name.lower().split())
        
        return list(set(terms))
    
    def _check_vocabulary_consistency(self, content: str, domain_terms: List[str], file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        content_lower = content.lower()
        
        synonym_map = {
            'data': ['info', 'information', 'content'],
            'user': ['person', 'customer', 'client'],
            'system': ['application', 'app', 'service'],
        }
        
        for domain_term, synonyms in synonym_map.items():
            if domain_term in domain_terms:
                for synonym in synonyms:
                    if synonym in content_lower and domain_term not in content_lower:
                        violation = Violation(
                            rule=self.rule,
                            violation_message=f'Test uses "{synonym}" instead of domain term "{domain_term}" - use consistent vocabulary',
                            location=str(file_path),
                            severity='warning'
                        ).to_dict()
                        violations.append(violation)
                        break
        
        return violations


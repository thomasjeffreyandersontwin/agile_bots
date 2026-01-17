
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import re
from test_scanner import TestScanner
from scanners.violation import Violation

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from .resources.ast_elements import Functions

class ExactVariableNamesScanner(TestScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        domain_concepts = self._extract_domain_concepts(story_graph)
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            if function.node.name.startswith('test_'):
                violations.extend(self._check_variable_names(function.node, domain_concepts, file_path))
        
        return violations
    
    def _extract_domain_concepts(self, story_graph: Dict[str, Any]) -> List[str]:
        concepts = []
        epics = story_graph.get('epics', [])
        for epic in epics:
            domain_concepts_list = epic.get('domain_concepts', [])
            for concept in domain_concepts_list:
                if isinstance(concept, dict):
                    concept_name = concept.get('name', '')
                    if concept_name:
                        concepts.append(concept_name.lower())
        return concepts
    
    def _check_variable_names(self, test_node: ast.FunctionDef, domain_concepts: List[str], file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        for node in ast.walk(test_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        
                        if var_name in ['data', 'result', 'value', 'item', 'obj', 'thing']:
                            line_number = target.lineno if hasattr(target, 'lineno') else None
                            violation = Violation(
                                rule=self.rule,
                                violation_message=f'Variable "{target.id}" uses generic name - use exact domain concept name from scenario.AC',
                                location=str(file_path),
                                line_number=line_number,
                                severity='warning'
                            ).to_dict()
                            violations.append(violation)
        
        return violations


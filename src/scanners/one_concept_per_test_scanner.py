
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
import logging
from test_scanner import TestScanner
from scanners.violation import Violation
from .resources.ast_elements import Functions

logger = logging.getLogger(__name__)

class OneConceptPerTestScanner(TestScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            if function.node.name.startswith('test_'):
                violation = self._check_one_concept(function.node, file_path, content, rule_obj)
                if violation:
                    violations.append(violation)
        
        return violations
    
    def _check_one_concept(self, test_node: ast.FunctionDef, file_path: Path, content: str, rule_obj: Any) -> Optional[Dict[str, Any]]:
        violations = []
        
        test_name = test_node.name.lower()
        multi_concept_patterns = [
            r'\b(and|or|then|also|plus)\b',
            r'_(and|or|then|also|plus)_',
        ]
        
        for pattern in multi_concept_patterns:
            if re.search(pattern, test_name):
                words = test_name.split('_')
                if len(words) > 8:
                    line_number = test_node.lineno if hasattr(test_node, 'lineno') else None
                    violations.append(Violation(
                        rule=rule_obj,
                        violation_message=f'Test "{test_node.name}" appears to test multiple concepts - split into separate tests, one concept per test',
                        location=str(file_path),
                        line_number=line_number,
                        severity='warning'
                    ).to_dict())
                    break
        
        concepts = self._detect_multiple_concepts(test_node, content)
        if len(concepts) > 1:
            line_number = test_node.lineno if hasattr(test_node, 'lineno') else None
            violations.append(Violation(
                rule=rule_obj,
                violation_message=(
                    f'Test "{test_node.name}" tests multiple concepts detected: {", ".join(concepts)}. '
                    f'Split into separate tests, one concept per test.'
                ),
                location=str(file_path),
                line_number=line_number,
                severity='warning'
            ).to_dict())
        
        scenario = self._extract_scenario(test_node)
        if scenario and self._has_multiple_scenarios(scenario):
            line_number = test_node.lineno if hasattr(test_node, 'lineno') else None
            violations.append(Violation(
                rule=rule_obj,
                violation_message=(
                    f'Test "{test_node.name}" docstring contains multiple scenarios. '
                    f'Each test should focus on a single scenario.'
                ),
                location=str(file_path),
                line_number=line_number,
                severity='info'
            ).to_dict())
        
        assertion_groups = self._group_assertions(test_node)
        if len(assertion_groups) > 3:
            line_number = test_node.lineno if hasattr(test_node, 'lineno') else None
            violations.append(Violation(
                rule=rule_obj,
                violation_message=(
                    f'Test "{test_node.name}" has {len(assertion_groups)} distinct assertion groups - '
                    f'suggests multiple concepts being tested. Split into separate tests.'
                ),
                location=str(file_path),
                line_number=line_number,
                severity='info'
            ).to_dict())
        
        return violations[0] if violations else None
    
    def _detect_multiple_concepts(self, test_node: ast.FunctionDef, content: str) -> List[str]:
        concepts = []
        
        has_setup = False
        has_action = False
        has_validation = False
        has_cleanup = False
        
        for stmt in test_node.body:
            if isinstance(stmt, ast.Assign):
                has_setup = True
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                func_name = self._get_call_name(stmt.value)
                if func_name:
                    if func_name.startswith('given_') or func_name.startswith('when_'):
                        has_setup = True
                    elif func_name.startswith('then_') or func_name.startswith('verify_'):
                        has_validation = True
            elif isinstance(stmt, ast.Assert):
                has_validation = True
        
        if has_setup:
            concepts.append('Setup')
        if has_action:
            concepts.append('Action')
        if has_validation:
            concepts.append('Validation')
        if has_cleanup:
            concepts.append('Cleanup')
        
        
        return concepts
    
    def _get_call_name(self, call_node: ast.Call) -> Optional[str]:
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            return call_node.func.attr
        return None
    
    def _extract_scenario(self, test_node: ast.FunctionDef) -> Optional[str]:
        if not test_node.body:
            return None
        
        first_stmt = test_node.body[0]
        if isinstance(first_stmt, ast.Expr):
            if isinstance(first_stmt.value, ast.Constant) and isinstance(first_stmt.value.value, str):
                return first_stmt.value.value
            elif hasattr(ast, 'Str') and isinstance(first_stmt.value, ast.Str):
                return first_stmt.value.s
        
        return None
    
    def _has_multiple_scenarios(self, scenario: str) -> bool:
        scenario_count = scenario.lower().count('scenario:')
        given_count = scenario.lower().count('given:')
        
        return scenario_count > 1 or given_count > 3
    
    def _group_assertions(self, test_node: ast.FunctionDef) -> List[List[ast.Assert]]:
        assertions = []
        for node in ast.walk(test_node):
            if isinstance(node, ast.Assert):
                assertions.append(node)
        
        if len(assertions) <= 1:
            return [assertions] if assertions else []
        
        groups = []
        current_group = [assertions[0]]
        
        for i in range(1, len(assertions)):
            if hasattr(assertions[i], 'lineno') and hasattr(assertions[i-1], 'lineno'):
                if assertions[i].lineno - assertions[i-1].lineno <= 5:
                    current_group.append(assertions[i])
                else:
                    groups.append(current_group)
                    current_group = [assertions[i]]
            else:
                current_group.append(assertions[i])
        
        if current_group:
            groups.append(current_group)
        
        return groups


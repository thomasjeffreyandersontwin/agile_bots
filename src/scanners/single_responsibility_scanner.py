
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
import logging
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation
from complexity_metrics import ComplexityMetrics
from .resources.ast_elements import Functions

logger = logging.getLogger(__name__)

class SingleResponsibilityScanner(CodeScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            violation = self._check_function_sr(function.node, file_path, rule_obj)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_function_sr(self, func_node: ast.FunctionDef, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        func_name = func_node.name.lower()
        
        if func_name.startswith(('given_', 'when_', 'then_', 'test_')):
            return None
        
        violations = []
        
        name_violation = self._check_name_patterns(func_node, file_path, rule_obj)
        if name_violation:
            violations.append(name_violation)
        
        
        return violations[0] if violations else None
    
    def _check_name_patterns(self, func_node: ast.FunctionDef, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        func_name = func_node.name.lower()
        
        action_verbs = [
            'validate', 'save', 'load', 'process', 'send', 'create', 'update', 'delete',
            'calculate', 'compute', 'transform', 'convert', 'parse', 'format', 'render',
            'execute', 'run', 'invoke', 'call', 'fetch', 'retrieve', 'store', 'write',
            'read', 'parse', 'build', 'generate', 'compile', 'extract', 'merge', 'split'
        ]
        
        verbs_pattern = '|'.join(action_verbs)
        for verb in action_verbs:
            pattern = rf'\b{verb}_and_({verbs_pattern})\b'
            if re.search(pattern, func_name):
                line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
                try:
                    content = file_path.read_text(encoding='utf-8')
                    return self._create_violation_with_snippet(
                        rule_obj=rule_obj,
                        violation_message=f'Function "{func_node.name}" appears to have multiple responsibilities - split into separate functions',
                        file_path=file_path,
                        line_number=line_number,
                        severity='warning',
                        content=content,
                        ast_node=func_node,
                        max_lines=5
                    )
                except Exception:
                    return Violation(
                        rule=rule_obj,
                        violation_message=f'Function "{func_node.name}" appears to have multiple responsibilities - split into separate functions',
                        location=str(file_path),
                        line_number=line_number,
                        severity='warning'
                    ).to_dict()
        
        camel_case_pattern = r'([a-z]+)And([A-Z][a-z]+)'
        match = re.search(camel_case_pattern, func_node.name)
        if match:
            verb1 = match.group(1).lower()
            verb2 = match.group(2).lower()
            if verb1 in action_verbs and verb2 in action_verbs:
                line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
                try:
                    content = file_path.read_text(encoding='utf-8')
                    return self._create_violation_with_snippet(
                        rule_obj=rule_obj,
                        violation_message=f'Function "{func_node.name}" appears to have multiple responsibilities - split into separate functions',
                        file_path=file_path,
                        line_number=line_number,
                        severity='warning',
                        content=content,
                        ast_node=func_node,
                        max_lines=5
                    )
                except Exception:
                    return Violation(
                        rule=rule_obj,
                        violation_message=f'Function "{func_node.name}" appears to have multiple responsibilities - split into separate functions',
                        location=str(file_path),
                        line_number=line_number,
                        severity='warning'
                    ).to_dict()
        
        return None


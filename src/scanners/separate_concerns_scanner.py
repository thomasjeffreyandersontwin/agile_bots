
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
import logging
from scanners.code_scanner import CodeScanner
from .resources.ast_elements import Functions

logger = logging.getLogger(__name__)

class SeparateConcernsScanner(CodeScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            violation = self._check_mixed_concerns(function.node, content, file_path, rule_obj)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_mixed_concerns(self, func_node: ast.FunctionDef, content: str, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        from complexity_metrics import ComplexityMetrics
        
        responsibilities = ComplexityMetrics.detect_responsibilities(func_node)
        
        if len(responsibilities) <= 1:
            return None
        
        line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
        
        incompatible_pairs = [
            ('I/O', 'Computation'),
            ('I/O', 'Transformation'),
            ('Validation', 'Transformation'),
            ('StateManagement', 'Computation'),
        ]
        
        responsibility_set = set(responsibilities)
        for resp1, resp2 in incompatible_pairs:
            if resp1 in responsibility_set and resp2 in responsibility_set:
                violation_message = (
                    f'Function "{func_node.name}" mixes incompatible responsibilities: {", ".join(responsibilities)}. '
                    f'Separate {resp1} from {resp2} - pure logic should be separate from side effects.'
                )
                return self._create_violation_with_snippet(
                    rule_obj=rule_obj,
                    violation_message=violation_message,
                    file_path=file_path,
                    line_number=line_number,
                    severity='error',
                    content=content,
                    ast_node=func_node
                )
        
        if len(responsibilities) > 2:
            violation_message = (
                f'Function "{func_node.name}" has multiple responsibilities: {", ".join(responsibilities)}. '
                f'Consider splitting into separate functions, each with a single responsibility.'
            )
            return self._create_violation_with_snippet(
                rule_obj=rule_obj,
                violation_message=violation_message,
                file_path=file_path,
                line_number=line_number,
                severity='warning',
                content=content,
                ast_node=func_node
            )
        
        return None


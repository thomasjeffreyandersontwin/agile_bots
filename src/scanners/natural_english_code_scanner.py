
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import re
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from scanners.violation import Violation
from .resources.ast_elements import Functions

class NaturalEnglishCodeScanner(CodeScanner):
    
    TECHNICAL_NOTATION_PATTERNS = [
        r'_0_1$',
        r'_1_star$',
        r'_optional$',
        r'_nullable$',
    ]
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            violation = self._check_natural_english(function.node, file_path, content)
            if violation:
                violations.append(violation)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                violation = self._check_variable_name(node, file_path, content)
                if violation:
                    violations.append(violation)
        
        return violations
    
    def _check_natural_english(self, func_node: ast.FunctionDef, file_path: Path, content: str) -> Optional[Dict[str, Any]]:
        func_name = func_node.name
        
        for pattern in self.TECHNICAL_NOTATION_PATTERNS:
            if re.search(pattern, func_name):
                return self._create_violation_with_snippet(
                    violation_message=f'Function "{func_name}" uses technical notation. Use natural English instead (e.g., "may_find" not "find_optional").',
                    file_path=file_path,
                    line_number=func_node.lineno,
                    severity='warning',
                    content=content,
                    ast_node=func_node
                )
        
        return None
    
    def _check_variable_name(self, name_node: ast.Name, file_path: Path, content: str) -> Optional[Dict[str, Any]]:
        var_name = name_node.id
        
        for pattern in self.TECHNICAL_NOTATION_PATTERNS:
            if re.search(pattern, var_name):
                return self._create_violation_with_snippet(
                    violation_message=f'Variable "{var_name}" uses technical notation. Use natural English instead.',
                    file_path=file_path,
                    line_number=name_node.lineno if hasattr(name_node, 'lineno') else None,
                    severity='info',
                    content=content,
                    ast_node=name_node
                )
        
        return None


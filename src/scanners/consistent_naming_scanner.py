
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import logging
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from scanners.violation import Violation
from collections import defaultdict
from .resources.ast_elements import Functions, Classes

logger = logging.getLogger(__name__)

class ConsistentNamingScanner(CodeScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        function_names = []
        class_names = []
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            if not (function.node.name.startswith('_') and function.node.name != '__init__'):
                function_names.append(function.node.name)
        
        classes = Classes(tree)
        for cls in classes.get_many_classes:
            class_names.append(cls.node.name)
        
        violations.extend(self._check_naming_consistency(function_names, class_names, file_path))
        
        return violations
    
    def _check_naming_consistency(self, function_names: List[str], class_names: List[str], file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        if not function_names:
            return violations
        
        has_snake_case = any('_' in name for name in function_names)
        has_camel_case = any(name[0].isupper() and '_' not in name for name in function_names if name)
        
        camel_case_count = sum(1 for name in function_names if name and name[0].isupper() and '_' not in name)
        
        if has_snake_case and camel_case_count > 1:
            violation = Violation(
                rule=self.rule,
                violation_message=f'File mixes snake_case and camelCase naming conventions ({camel_case_count} camelCase functions) - use consistent naming style (snake_case for functions)',
                location=str(file_path),
                severity='warning'
            ).to_dict()
            violations.append(violation)
        
        return violations


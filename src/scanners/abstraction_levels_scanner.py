
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import re
import logging
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from .resources.ast_elements import Functions

logger = logging.getLogger(__name__)

class AbstractionLevelsScanner(CodeScanner):
    
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
            violation = self._check_mixed_abstraction_levels(function.node, content, file_path)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_mixed_abstraction_levels(self, func_node: ast.FunctionDef, content: str, file_path: Path) -> Optional[Dict[str, Any]]:
        func_source = ast.get_source_segment(content, func_node) or ''
        func_source_lower = func_source.lower()
        
        has_high_level = any(keyword in func_source_lower for keyword in ['process', 'handle', 'orchestrate', 'coordinate', 'manage'])
        
        has_low_level = any(keyword in func_source_lower for keyword in ['sql', 'query', 'select', 'insert', 'update', 'delete', 'file', 'open', 'close', 'read', 'write'])
        
        if has_high_level and has_low_level:
            line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
            return self._create_violation_with_snippet(
                                violation_message=f'Function "{func_node.name}" mixes high-level operations with low-level details - extract low-level details to separate functions',
                file_path=file_path,
                line_number=line_number,
                severity='warning',
                content=content,
                ast_node=func_node
            )
        
        return None



from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import logging
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from scanners.violation import Violation
from .complexity_metrics import ComplexityMetrics
from .resources.ast_elements import Classes

logger = logging.getLogger(__name__)

class ClassSizeScanner(CodeScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        classes = Classes(tree)
        for cls in classes.get_many_classes:
            violation = self._check_class_size(cls.node, file_path, self.rule, content)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_class_size(self, class_node: ast.ClassDef, file_path: Path, content: str) -> Optional[Dict[str, Any]]:
        violations = []
        
        if hasattr(class_node, 'end_lineno') and class_node.end_lineno:
            class_size = class_node.end_lineno - class_node.lineno + 1
        else:
            class_size = len(class_node.body) * 10
        
        if class_size > 300:
            line_number = class_node.lineno if hasattr(class_node, 'lineno') else None
            violations.append(self._create_violation_with_snippet(
                violation_message=f'Class "{class_node.name}" is {class_size} lines - should be under 300 lines (extract related methods into separate classes)',
                file_path=file_path,
                line_number=line_number,
                severity='warning',
                content=content,
                ast_node=class_node,
                max_lines=10
            ))
        
        
        
        return violations[0] if violations else None


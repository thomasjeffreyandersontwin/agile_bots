
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import re
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from scanners.violation import Violation
from .resources.ast_elements import Classes

class DomainGroupingCodeScanner(CodeScanner):
    
    TECHNICAL_LAYER_PATTERNS = [
        r'\blayer\b',
        r'\btier\b',
        r'\bservice\b',
        r'\brepository\b',
        r'\bdto\b',
    ]
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        if not file_path.exists():
            return violations
        
        file_path_str = str(file_path)
        for pattern in self.TECHNICAL_LAYER_PATTERNS:
            if re.search(pattern, file_path_str, re.IGNORECASE):
                violations.append(
                    Violation(
                        rule=self.rule,
                        violation_message=f'File path "{file_path}" uses technical layer terminology. Organize by domain area instead.',
                        location=str(file_path),
                        line_number=None,
                        severity='info'
                    ).to_dict()
                )
                break
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        classes = Classes(tree)
        for cls in classes.get_many_classes:
            violation = self._check_class_name(cls.node, file_path)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_class_name(self, class_node: ast.ClassDef, file_path: Path) -> Optional[Dict[str, Any]]:
        class_name_lower = class_node.name.lower()
        
        for pattern in self.TECHNICAL_LAYER_PATTERNS:
            if re.search(pattern, class_name_lower):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    return self._create_violation_with_snippet(
                                                violation_message=f'Class "{class_node.name}" uses technical layer terminology. Group by domain area instead.',
                        file_path=file_path,
                        line_number=class_node.lineno,
                        severity='info',
                        content=content,
                        ast_node=class_node,
                        max_lines=5
                    )
                except Exception:
                    return Violation(
                        rule=self.rule,
                        violation_message=f'Class "{class_node.name}" uses technical layer terminology. Group by domain area instead.',
                        location=str(file_path),
                        line_number=class_node.lineno,
                        severity='info'
                    ).to_dict()
        
        return None


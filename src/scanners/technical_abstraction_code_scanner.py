"""Scanner for validating avoidance of technical abstractions in code."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation
from .resources.ast_elements import Classes
from vocabulary_helper import VocabularyHelper

class TechnicalAbstractionCodeScanner(CodeScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        classes = Classes(tree)
        for cls in classes.get_many_classes:
            violation = self._check_technical_abstraction(cls.node, file_path, rule_obj)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_technical_abstraction(self, class_node: ast.ClassDef, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        class_name = class_node.name
        
        is_agent, base_verb, suffix = VocabularyHelper.is_agent_noun(class_name)
        if is_agent and base_verb in ['save', 'load', 'store']:
            try:
                content = file_path.read_text(encoding='utf-8')
                return self._create_violation_with_snippet(
                    rule_obj=rule_obj,
                    violation_message=f'Class "{class_name}" separates technical abstraction. Keep technical details (saving, loading) as part of domain concepts instead.',
                    file_path=file_path,
                    line_number=class_node.lineno,
                    severity='warning',
                    content=content,
                    ast_node=class_node,
                    max_lines=5
                )
            except Exception:
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Class "{class_name}" separates technical abstraction. Keep technical details (saving, loading) as part of domain concepts instead.',
                    location=str(file_path),
                    line_number=class_node.lineno,
                    severity='warning'
                ).to_dict()
        
        return None

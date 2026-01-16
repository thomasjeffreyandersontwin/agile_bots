
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from .resources.scan import Scan
    from .resources.scope import Scope
    from .resources.violation import Violation
    from agile_bots.src.actions.rules.rule import Rule
    from .resources.block import Block
    from .resources.file import File

class Scanner(ABC):
    
    def scan(
        self, 
        story_graph: Dict[str, Any], 
        rule_obj: Any = None,
        test_files: Optional[List['Path']] = None,
        code_files: Optional[List['Path']] = None,
        on_file_scanned: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        violations = []
        
        all_files = []
        if test_files:
            all_files.extend(test_files)
        if code_files:
            all_files.extend(code_files)
        
        for file_path in all_files:
            if file_path and file_path.exists() and file_path.is_file():
                file_violations = self.scan_file(file_path, rule_obj, story_graph)
                file_violations_list = file_violations if isinstance(file_violations, list) else [file_violations] if file_violations else []
                
                if file_violations_list:
                    violations.extend(file_violations_list)
                
                if on_file_scanned:
                    on_file_scanned(file_path, file_violations_list, rule_obj)
        
        return violations
    
    def _empty_violation_list(self) -> List[Dict[str, Any]]:
        return []
    
    def scan_file(
        self,
        file_path: 'Path',
        rule_obj: Any = None,
        story_graph: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        return self._empty_violation_list()
    
    def scan_cross_file(
        self,
        rule_obj: Any = None,
        test_files: Optional[List['Path']] = None,
        code_files: Optional[List['Path']] = None,
        all_test_files: Optional[List['Path']] = None,
        all_code_files: Optional[List['Path']] = None,
        status_writer: Optional[Any] = None,
        max_cross_file_comparisons: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        return self._empty_violation_list()
    
    def _is_test_file(self, file_path: 'Path') -> bool:
        if not file_path:
            return False
        
        path_str = str(file_path).lower()
        file_name = file_path.name.lower()
        
        if '/test' in path_str or '/tests' in path_str or '\\test' in path_str or '\\tests' in path_str:
            return True
        
        if file_name.startswith('test_') or file_name == 'conftest.py':
            return True
        
        return False
    
    
    def performs_scan_for_one_rule(
        self,
        scan: 'Scan',
        scope: 'Scope',
        rule: 'Rule'
    ) -> List['Violation']:
        violations = []
        
        for file in scope.files:
            if not file.parse_safely():
                continue
            
            for block in file.blocks:
                block_violations = self._scan_block(block, rule, scan)
                violations.extend(block_violations)
        
        return violations
    
    def _scan_block(
        self,
        block: 'Block',
        rule: 'Rule',
        scan: 'Scan'
    ) -> List['Violation']:
        return self._empty_violation_list()
    
    def associated_with_rule(self, rule: 'Rule') -> bool:
        return True
    
    
    def checks_file_naming(self, file: 'File', file_naming_checker) -> List['Violation']:
        return file.check_file_naming(file_naming_checker)
    
    def checks_class_naming(self, block: 'Block', class_naming_checker) -> List['Violation']:
        return block.check_class_naming(class_naming_checker)
    
    def checks_method_naming(self, block: 'Block', method_naming_checker) -> List['Violation']:
        return block.check_method_naming(method_naming_checker)
    
    def analyzes_code_structure(
        self,
        block: 'Block',
        code_structure_analyzer,
        pattern_collection = None
    ) -> List['Violation']:
        return block.analyze_structure(code_structure_analyzer)
    
    def examines_ast_for_violations(
        self,
        block: 'Block',
        code_structure_analyzer
    ) -> List['Violation']:
        return block.analyze_structure(code_structure_analyzer)
    
    def identifies_code_patterns(
        self,
        block: 'Block',
        pattern_collection,
        code_structure_analyzer
    ) -> List['Violation']:
        violations = []
        if pattern_collection and pattern_collection.matches_text(block.content):
            pass
        return violations


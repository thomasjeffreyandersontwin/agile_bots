
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from .resources.scan import Scan
    from .resources.scope import Scope
    from .resources.violation import Violation
    from actions.rules.rule import Rule
    from .resources.block import Block
    from .resources.file import File
    from .resources.scan_context import ScanContext, FileScanContext, ScanFilesContext, CrossFileScanContext

class Scanner(ABC):
    
    def __init__(self, rule: 'Rule'):
        self.rule = rule
    
    def scan_with_context(self, context: 'ScanFilesContext') -> List[Dict[str, Any]]:
        from .resources.scan_context import FileScanContext
        
        violations = []
        all_files = context.files.all_files
        
        for file_path in all_files:
            if file_path and file_path.exists() and file_path.is_file():
                file_context = FileScanContext(
                    story_graph=context.story_graph,
                    file_path=file_path
                )
                file_violations = self.scan_file_with_context(file_context)
                file_violations_list = file_violations if isinstance(file_violations, list) else [file_violations] if file_violations else []
                
                if file_violations_list:
                    violations.extend(file_violations_list)
                
                if context.on_file_scanned:
                    context.on_file_scanned(file_path, file_violations_list, self.rule)
        
        return violations
    
    def _empty_violation_list(self) -> List[Dict[str, Any]]:
        return []
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        if not context.exists:
            return self._empty_violation_list()
        return self._empty_violation_list()
    
    def scan_cross_file_with_context(self, context: 'CrossFileScanContext') -> List[Dict[str, Any]]:
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

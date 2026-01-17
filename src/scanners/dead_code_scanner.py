
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
import ast
import logging
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation

logger = logging.getLogger(__name__)

class DeadCodeScanner(CodeScanner):
    
    def scan(
        self, 
        story_graph: Dict[str, Any] = None,
        test_files: Optional[List[Path]] = None,
        code_files: Optional[List[Path]] = None,
        on_file_scanned: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        violations = []
        
        all_files = []
        if code_files:
            all_files.extend(code_files)
        if test_files:
            all_files.extend(test_files)
        
        if not all_files:
            return violations
        
        definitions = {}
        usages = set()
        
        for file_path in all_files:
            if not file_path.exists() or not file_path.is_file():
                continue
            
            try:
                file_defs, file_usages = self._analyze_file(file_path)
                
                for name, (line_num, node_type) in file_defs.items():
                    qualified_name = f"{file_path.stem}.{name}"
                    definitions[qualified_name] = (file_path, line_num, node_type, name)
                    if name not in definitions:
                        definitions[name] = (file_path, line_num, node_type, name)
                
                usages.update(file_usages)
                
            except Exception as e:
                logger.debug(f"Error analyzing {file_path}: {e}")
                continue
        
        for qualified_name, (file_path, line_num, node_type, simple_name) in definitions.items():
            if '.' in qualified_name and simple_name in usages:
                continue
            
            if self._is_test_file(file_path):
                continue
            
            if simple_name in usages or qualified_name in usages:
                continue
            
            if self._is_entry_point_or_special(simple_name, node_type):
                continue
            
            violation = Violation(
                rule=self.rule,
                violation_message=f"Unused {node_type} '{simple_name}' - consider removing dead code",
                location=str(file_path),
                line_number=line_num,
                severity='warning'
            ).to_dict()
            violations.append(violation)
            
            if on_file_scanned:
                on_file_scanned(file_path, [violation])
        
        return violations
    
    def scan_file(
        self,
        file_path: Path = None,
        story_graph: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        private_defs, private_usages = self._analyze_private_members(tree)
        
        for method_name, (line_num, class_name) in private_defs.items():
            if method_name not in private_usages:
                if method_name.startswith('__') and method_name.endswith('__'):
                    continue
                
                violation = self._create_violation_with_snippet(
                                        violation_message=f"Private method '{method_name}' in class '{class_name}' is never called - consider removing dead code",
                    file_path=file_path,
                    line_number=line_num,
                    severity='warning',
                    content=content,
                    start_line=line_num
                )
                violations.append(violation)
        
        return violations
    
    def _analyze_file(self, file_path: Path) -> Tuple[Dict[str, Tuple[int, str]], Set[str]]:
        definitions = {}
        usages = set()
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError) as e:
            logger.debug(f"Skipping {file_path}: {e}")
            return definitions, usages
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                definitions[node.name] = (node.lineno, 'function')
            elif isinstance(node, ast.AsyncFunctionDef):
                definitions[node.name] = (node.lineno, 'async function')
            elif isinstance(node, ast.ClassDef):
                definitions[node.name] = (node.lineno, 'class')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                usages.add(node.id)
            elif isinstance(node, ast.Attribute):
                usages.add(node.attr)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    usages.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    usages.add(node.func.attr)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    usages.add(alias.asname if alias.asname else alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    usages.add(alias.asname if alias.asname else alias.name)
        
        return definitions, usages
    
    def _analyze_private_members(self, tree: ast.AST) -> Tuple[Dict[str, Tuple[int, str]], Set[str]]:
        private_defs = {}
        private_usages = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if item.name.startswith('_') and not item.name.startswith('__'):
                            private_defs[item.name] = (item.lineno, class_name)
                
                for item in ast.walk(node):
                    if isinstance(item, ast.Attribute):
                        if isinstance(item.value, ast.Name) and item.value.id == 'self':
                            private_usages.add(item.attr)
                    elif isinstance(item, ast.Call):
                        if isinstance(item.func, ast.Attribute):
                            if isinstance(item.func.value, ast.Name) and item.func.value.id == 'self':
                                private_usages.add(item.func.attr)
        
        return private_defs, private_usages
    
    def _is_entry_point_or_special(self, name: str, node_type: str) -> bool:
        
        entry_points = {
            'main', 'cli', 'app', 'run', 'start', 'execute',
            'handle', 'process', 'serve', 'listen'
        }
        if name in entry_points or name.startswith('main'):
            return True
        
        if name.startswith('__') and name.endswith('__'):
            return True
        
        if name.startswith('test_') or name.startswith('Test'):
            return True
        
        if name.startswith('create_') or name.startswith('build_') or name.startswith('make_'):
            return True
        
        if name.endswith('_handler') or name.endswith('Handler'):
            return True
        
        if node_type == 'class':
            if not name.startswith('_'):
                return True
        
        if node_type in ('function', 'async function'):
            if not name.startswith('_'):
                internal_patterns = ['helper', 'util', 'internal', 'legacy']
                name_lower = name.lower()
                if not any(p in name_lower for p in internal_patterns):
                    return True
        
        return False
    
    def scan_cross_file(
        self = None,
        test_files: Optional[List[Path]] = None,
        code_files: Optional[List[Path]] = None,
        all_test_files: Optional[List[Path]] = None,
        all_code_files: Optional[List[Path]] = None,
        status_writer: Optional[Any] = None,
        max_cross_file_comparisons: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        all_code = all_code_files if all_code_files else code_files or []
        all_tests = all_test_files if all_test_files else test_files or []
        
        return self.scan(
            story_graph={},
                        test_files=all_tests,
            code_files=all_code,
            on_file_scanned=None
        )

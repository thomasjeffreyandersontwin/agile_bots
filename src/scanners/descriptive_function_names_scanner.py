
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import re
from test_scanner import TestScanner
from scanners.violation import Violation

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from .resources.ast_elements import Functions

class DescriptiveFunctionNamesScanner(TestScanner):
    
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
            if not function.node.name.startswith('test_'):
                violation = self._check_descriptive_name(function.node, file_path)
                if violation:
                    violations.append(violation)
        
        return violations
    
    def _check_descriptive_name(self, func_node: ast.FunctionDef, file_path: Path) -> Optional[Dict[str, Any]]:
        func_name_lower = func_node.name.lower()
        func_name_original = func_node.name
        
        acceptable_domain_terms = {
            'scan',
            'scan_test_file',
            'scan_cross_file',
            'parse',
            'render',
            'build',
            'load',
            'save',
            'read',
            'write',
            'get',
            'set',
            'has',
            'is',
            'can',
        }
        
        if func_name_lower in acceptable_domain_terms:
            return None
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            content = None
        
        vague_names = ['setup', 'do', 'handle', 'process', 'run', 'main', 'helper', 'util', 'func']
        if func_name_lower in vague_names or len(func_name_lower) < 5:
            line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
            if content:
                return self._create_violation_with_snippet(
                                        violation_message=f'Helper function "{func_node.name}" uses vague/abbreviated name - use descriptive name that reveals purpose',
                    file_path=file_path,
                    line_number=line_number,
                    severity='error',
                    content=content,
                    ast_node=func_node,
                    max_lines=3
                )
            else:
                return Violation(
                    rule=self.rule,
                    violation_message=f'Helper function "{func_node.name}" uses vague/abbreviated name - use descriptive name that reveals purpose',
                    location=str(file_path),
                    line_number=line_number,
                    severity='error'
                ).to_dict()
        
        acceptable_abbrevs = {
            'init', 'config', 'json', 'cli', 'mcp', 'dir', 'sync', 'var', 'obj', 
            'param', 'req', 'resp', 'url', 'api', 'http', 'html', 'xml', 'yaml',
            'id', 'db', 'sql', 'ui', 'ux', 'io', 'os', 'env', 'tmp', 'log'
        }
        
        words_lower = func_name_lower.split('_')
        words_original = func_name_original.split('_')
        
        cryptic_acronyms = set()
        
        for word_lower, word_original in zip(words_lower, words_original):
            if word_original.isupper() and len(word_original) >= 2:
                well_known_acronyms = {'mcp', 'json', 'cli', 'api', 'http', 'html', 'xml', 'yaml', 'sql', 'ui', 'ux', 'io', 'os', 'id', 'db'}
                if word_lower not in well_known_acronyms:
                    cryptic_acronyms.add(word_original)
            
            if len(word_lower) <= 3 and word_lower not in acceptable_abbrevs:
                cryptic_short = ['cfg', 'mgr', 'acct', 'addr', 'cnt', 'cntr', 'ctrl', 'def', 'doc', 'err', 'exc', 'fn', 'fnc', 'hdlr', 'idx', 'len', 'loc', 'max', 'min', 'num', 'opt', 'prm', 'ptr', 'ref', 'ret', 'src', 'str', 'tmp', 'val', 'wrt']
                if word_lower in cryptic_short:
                    cryptic_acronyms.add(word_lower)
        
        if cryptic_acronyms:
            line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
            if content:
                return self._create_violation_with_snippet(
                                        violation_message=f'Helper function "{func_node.name}" contains cryptic abbreviations or acronyms ({", ".join(cryptic_acronyms)}) - use full descriptive words',
                    file_path=file_path,
                    line_number=line_number,
                    severity='warning',
                    content=content,
                    ast_node=func_node,
                    max_lines=3
                )
            else:
                return Violation(
                    rule=self.rule,
                    violation_message=f'Helper function "{func_node.name}" contains cryptic abbreviations or acronyms ({", ".join(cryptic_acronyms)}) - use full descriptive words',
                    location=str(file_path),
                    line_number=line_number,
                    severity='warning'
                ).to_dict()
        
        return None


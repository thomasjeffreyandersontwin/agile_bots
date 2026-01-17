"""Base TestScanner class for validating test files."""

from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING
from pathlib import Path
import ast
from scanners.scanner import Scanner
from scanners.violation import Violation

if TYPE_CHECKING:
    from scanners.resources.scan_context import ScanFilesContext, FileScanContext, CrossFileScanContext
    from actions.rules.rule import Rule


class TestScanner(Scanner):
    
    def __init__(self, rule: 'Rule'):
        super().__init__(rule)
    
    def _empty_violation_list(self) -> List[Dict[str, Any]]:
        return []
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        if not context.exists:
            return self._empty_violation_list()
        return self._empty_violation_list()
    
    def _parse_test_file(self, test_file_path: Path) -> Optional[Tuple[str, ast.AST]]:
        if not test_file_path.exists():
            return None
        
        try:
            content = test_file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(test_file_path))
            return (content, tree)
        except (SyntaxError, UnicodeDecodeError):
            return None
    
    def _read_and_parse_file(self, file_path: Path) -> Optional[Tuple[str, List[str], ast.AST]]:
        import logging
        logger = logging.getLogger(__name__)
        
        if not file_path.exists():
            return None
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            tree = ast.parse(content, filename=str(file_path))
            return (content, lines, tree)
        except (SyntaxError, UnicodeDecodeError) as e:
            logger.debug(f'Skipping file {file_path} due to {type(e).__name__}: {e}')
            return None
    
    def _get_all_test_files_parsed(
        self, 
        test_files: Optional[List[Path]]
    ) -> List[Tuple[Path, str, ast.AST]]:
        parsed_files = []
        if test_files:
            for test_file_path in test_files:
                parsed = self._parse_test_file(test_file_path)
                if parsed:
                    content, tree = parsed
                    parsed_files.append((test_file_path, content, tree))
        return parsed_files

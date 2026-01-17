
from typing import List, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import logging

if TYPE_CHECKING:
    from line import Line
    from block import Block
    from scope import Scope
    from violation import Violation

logger = logging.getLogger(__name__)

class File:
    
    def __init__(self, path: Path, scope: 'Scope'):
        self._path = path
        self._scope = scope
        self._lines: List['Line'] = []
        self._blocks: List['Block'] = []
        self._content: Optional[str] = None
        self._ast: Optional[ast.AST] = None
        self._block_extractor = None
    
    @property
    def path(self) -> Path:
        return self._path
    
    @property
    def scope(self) -> 'Scope':
        return self._scope
    
    @property
    def lines(self) -> List['Line']:
        if not self._lines and self._content:
            from line import Line
            self._lines = [
                Line(self, i + 1, line_content)
                for i, line_content in enumerate(self._content.splitlines(keepends=True))
            ]
        return self._lines
    
    @property
    def blocks(self) -> List['Block']:
        if not self._blocks:
            self._extract_blocks()
        return self._blocks
    
    @property
    def content(self) -> Optional[str]:
        if self._content is None:
            self._load_content()
        return self._content
    
    def parse_safely(self) -> bool:
        try:
            if self._content is None:
                self._load_content()
            
            if self._path.suffix == '.py' and self._content:
                self._ast = ast.parse(self._content, filename=str(self._path))
                return True
        except (SyntaxError, UnicodeDecodeError) as e:
            logger.debug(f'Skipping file {self._path} due to {type(e).__name__}: {e}')
            return False
        except Exception as e:
            logger.warning(f'Error parsing file {self._path}: {e}')
            return False
        
        return False
    
    def parse_python_file(self) -> Optional[ast.AST]:
        if self.parse_safely():
            return self._ast
        return None
    
    def is_test_file(self) -> bool:
        path_str = str(self._path).lower()
        file_name = self._path.name.lower()
        
        if '/test' in path_str or '/tests' in path_str or '\\test' in path_str or '\\tests' in path_str:
            return True
        
        if file_name.startswith('test_') or file_name == 'conftest.py':
            return True
        
        return False
    
    def check_file_naming(self, file_naming_checker) -> List['Violation']:
        return file_naming_checker.check_file_name_matches_sub_epic(self) + \
               file_naming_checker.validate_file_naming_conventions(self)
    
    def _load_content(self):
        try:
            with open(self._path, 'r', encoding='utf-8') as f:
                self._content = f.read()
        except Exception as e:
            logger.warning(f'Error loading file {self._path}: {e}')
            self._content = ''
    
    def _extract_blocks(self):
        from block_extractor import BlockExtractor
        
        if self._block_extractor is None:
            self._block_extractor = BlockExtractor()
        
        self._blocks = self._block_extractor.extract_blocks_from_file(self)
        self._scope._blocks.extend(self._blocks)


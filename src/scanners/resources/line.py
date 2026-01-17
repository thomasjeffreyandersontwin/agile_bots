
from typing import Optional

class Line:
    
    def __init__(self, file: 'File', number: int, content: str):
        self._file = file
        self._number = number
        self._content = content
    
    @property
    def file(self) -> 'File':
        return self._file
    
    @property
    def number(self) -> int:
        return self._number
    
    @property
    def content(self) -> str:
        return self._content
    
    def extract_from_ast_node(self, node) -> Optional[int]:
        return getattr(node, 'lineno', None)
    
    def extract_from_position(self, position: int) -> int:
        content_before = self._file.content[:position] if hasattr(self._file, 'content') else ''
        return content_before.count('\n') + 1


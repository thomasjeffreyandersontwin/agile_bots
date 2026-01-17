
from typing import List
import ast
import logging
from file import File
from block import Block

logger = logging.getLogger(__name__)

class BlockExtractor:
    
    def extract_blocks_from_file(self, file: File) -> List[Block]:
        blocks = []
        
        ast_tree = file.parse_python_file()
        if not ast_tree:
            return blocks
        
        for node in ast.walk(ast_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                block = self._create_block_from_node(file, node)
                if block:
                    blocks.append(block)
        
        return blocks
    
    def identifies_code_blocks(self, file: File) -> List[Block]:
        return self.extract_blocks_from_file(file)
    
    def _create_block_from_node(self, file: File, node: ast.AST) -> Block:
        start_line = getattr(node, 'lineno', 1)
        end_line = self._get_end_line(node, file.content if file.content else '')
        
        content = self._get_node_source(node, file.content if file.content else '')
        
        return Block(file, content, start_line, end_line)
    
    def _get_end_line(self, node: ast.AST, content: str) -> int:
        if hasattr(node, 'end_lineno') and node.end_lineno:
            return node.end_lineno
        
        start_line = getattr(node, 'lineno', 1)
        logger.debug(f'Node missing end_lineno at line {start_line}')
        return start_line
    
    def _get_node_source(self, node: ast.AST, content: str) -> str:
        if not content:
            return ''
        
        if hasattr(ast, 'unparse'):
            try:
                return ast.unparse(node)
            except Exception as e:
                logger.debug(f'Could not unparse AST node at line {getattr(node, "lineno", "unknown")}: {type(e).__name__}: {e}')
                return ''
        
        logger.debug(f'ast.unparse not available')
        return ''


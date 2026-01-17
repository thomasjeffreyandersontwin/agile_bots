import ast
from typing import List, Optional
from abc import ABC

class ASTElement(ABC):
    
    def __init__(self, node: ast.AST):
        self._node = node
    
    @property
    def line_number(self) -> int:
        return self._node.lineno
    
    @property
    def node(self) -> ast.AST:
        return self._node

class Function(ASTElement):
    
    @property
    def name(self) -> str:
        return self._node.name
    
    @property
    def body_lines(self) -> int:
        if not self._node.body:
            return 0
        first_line = self._node.body[0].lineno
        last_line = max(stmt.lineno for stmt in ast.walk(self._node) if hasattr(stmt, 'lineno'))
        return last_line - first_line + 1
    
    @property
    def is_test_function(self) -> bool:
        return self.name.startswith('test_')

class Functions:
    
    def __init__(self, ast_node: ast.AST):
        self._ast_node = ast_node
        self._elements: Optional[List[Function]] = None
    
    @property
    def get_many_functions(self) -> List[Function]:
        if self._elements is None:
            self._elements = self._extract_functions()
        return self._elements
    
    def _extract_functions(self) -> List[Function]:
        functions = []
        for node in ast.walk(self._ast_node):
            if isinstance(node, ast.FunctionDef):
                functions.append(Function(node))
        return functions

class Class(ASTElement):
    
    @property
    def name(self) -> str:
        return self._node.name
    
    @property
    def methods(self) -> List[Function]:
        methods = []
        for node in self._node.body:
            if isinstance(node, ast.FunctionDef):
                methods.append(Function(node))
        return methods
    
    @property
    def is_test_class(self) -> bool:
        return self.name.startswith('Test')

class Classes:
    
    def __init__(self, ast_node: ast.AST):
        self._ast_node = ast_node
        self._elements: Optional[List[Class]] = None
    
    @property
    def get_many_classes(self) -> List[Class]:
        if self._elements is None:
            self._elements = self._extract_classes()
        return self._elements
    
    def _extract_classes(self) -> List[Class]:
        classes = []
        for node in ast.walk(self._ast_node):
            if isinstance(node, ast.ClassDef):
                classes.append(Class(node))
        return classes

class IfStatement(ASTElement):
    
    @property
    def has_else_clause(self) -> bool:
        return len(self._node.orelse) > 0
    
    @property
    def is_guard_clause(self) -> bool:
        if not self._node.body:
            return False
        for stmt in self._node.body:
            if isinstance(stmt, ast.Return):
                return True
        return False

class IfStatements:
    
    def __init__(self, ast_node: ast.AST):
        self._ast_node = ast_node
        self._elements: Optional[List[IfStatement]] = None
    
    @property
    def get_many_if_statements(self) -> List[IfStatement]:
        if self._elements is None:
            self._elements = self._extract_if_statements()
        return self._elements
    
    def _extract_if_statements(self) -> List[IfStatement]:
        if_statements = []
        for node in ast.walk(self._ast_node):
            if isinstance(node, ast.If):
                if_statements.append(IfStatement(node))
        return if_statements

class TryBlock(ASTElement):
    
    @property
    def exception_handlers(self) -> List[ast.ExceptHandler]:
        return self._node.handlers
    
    @property
    def has_bare_except(self) -> bool:
        for handler in self._node.handlers:
            if handler.type is None:
                return True
        return False
    
    @property
    def has_finally(self) -> bool:
        return len(self._node.finalbody) > 0

class TryBlocks:
    
    def __init__(self, ast_node: ast.AST):
        self._ast_node = ast_node
        self._elements: Optional[List[TryBlock]] = None
    
    @property
    def get_many_try_blocks(self) -> List[TryBlock]:
        if self._elements is None:
            self._elements = self._extract_try_blocks()
        return self._elements
    
    def _extract_try_blocks(self) -> List[TryBlock]:
        try_blocks = []
        for node in ast.walk(self._ast_node):
            if isinstance(node, ast.Try):
                try_blocks.append(TryBlock(node))
        return try_blocks

class Import(ASTElement):
    
    @property
    def is_from_import(self) -> bool:
        return isinstance(self._node, ast.ImportFrom)
    
    @property
    def module_name(self) -> str:
        if isinstance(self._node, ast.ImportFrom):
            return self._node.module or ''
        elif isinstance(self._node, ast.Import):
            if self._node.names:
                return self._node.names[0].name
        return ''

class Imports:
    
    def __init__(self, ast_node: ast.AST):
        self._ast_node = ast_node
        self._elements: Optional[List[Import]] = None
    
    @property
    def get_many_imports(self) -> List[Import]:
        if self._elements is None:
            self._elements = self._extract_imports()
        return self._elements
    
    def _extract_imports(self) -> List[Import]:
        imports = []
        for node in ast.walk(self._ast_node):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(Import(node))
        return imports


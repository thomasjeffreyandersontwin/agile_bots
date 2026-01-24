from pathlib import Path
import json
import sys
import ast
from typing import Dict, Any, Optional

def read_json_file(file_path: Path) -> Dict[str, Any]:
    if not file_path.exists():
        raise FileNotFoundError(f'File not found: {file_path}')
    return json.loads(file_path.read_text(encoding='utf-8-sig'))

def parse_command_text(text: str) -> tuple[str, str]:
    """Parse command text into verb and arguments.
    
    Args:
        text: Command text to parse (e.g., "scope --filter=story")
        
    Returns:
        Tuple of (verb, args) where verb is lowercase and args is the rest
    """
    parts = text.split(maxsplit=1)
    verb = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    return verb, args

class TerminalFormatter:
    RESET = '\x1b[0m'
    BLACK = '\x1b[30m'
    RED = '\x1b[31m'
    GREEN = '\x1b[32m'
    YELLOW = '\x1b[33m'
    BLUE = '\x1b[34m'
    MAGENTA = '\x1b[35m'
    CYAN = '\x1b[36m'
    WHITE = '\x1b[37m'
    BRIGHT_BLACK = '\x1b[90m'
    BRIGHT_RED = '\x1b[91m'
    BRIGHT_GREEN = '\x1b[92m'
    BRIGHT_YELLOW = '\x1b[93m'
    BRIGHT_BLUE = '\x1b[94m'
    BRIGHT_MAGENTA = '\x1b[95m'
    BRIGHT_CYAN = '\x1b[96m'
    BRIGHT_WHITE = '\x1b[97m'
    BOLD = '\x1b[1m'
    DIM = '\x1b[2m'
    UNDERLINE = '\x1b[4m'

    def __init__(self, enabled: Optional[bool]=None):
        should_enable = enabled if enabled is not None else self._supports_color()
        if not should_enable:
            self._disable_colors()

    @staticmethod
    def _supports_color() -> bool:
        if sys.platform == 'win32':
            return True
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    def _disable_colors(self):
        for attr in dir(self):
            if not attr.startswith('_') and attr.isupper():
                setattr(self, attr, '')

    def format(self, text: str, *styles: str) -> str:
        style_codes = ''.join((getattr(self, style, '') for style in styles))
        return f'{style_codes}{text}{self.RESET}'

    def header(self, text: str) -> str:
        return self.format(text, 'BOLD', 'CYAN')

    def command(self, text: str) -> str:
        return self.format(text, 'BOLD', 'GREEN')

    def label(self, text: str) -> str:
        return self.format(text, 'DIM')

    def success(self, text: str) -> str:
        return self.format(text, 'GREEN')

    def error(self, text: str) -> str:
        return self.format(text, 'RED')

    def warning(self, text: str) -> str:
        return self.format(text, 'YELLOW')

    def info(self, text: str) -> str:
        return self.format(text, 'BLUE')

    def separator(self, char: str='=', length: int=70) -> str:
        return self.format(char * length, 'BRIGHT_BLACK')
_default_formatter = None

def get_formatter(enabled: Optional[bool]=None) -> TerminalFormatter:
    global _default_formatter
    if _default_formatter is None or enabled is not None:
        _default_formatter = TerminalFormatter(enabled=enabled)
    return _default_formatter

def build_test_file_link(test_file: str, workspace_directory: Path, story_file_path: Optional[Path] = None) -> str:
    if not test_file:
        return ""
    try:
        from bot.workspace import get_python_workspace_root
        workspace_root = get_python_workspace_root()
        test_file_path = workspace_root / 'test' / test_file
        if not test_file_path.exists():
            return ""
        
        if story_file_path:
            rel_path = test_file_path.relative_to(workspace_root)
            rel_path_str = '/' + str(rel_path).replace('\\', '/')
            return f" | [Test]({rel_path_str})"
        
        rel_path = test_file_path.relative_to(workspace_root)
        rel_path_str = str(rel_path).replace('\\', '/')
        return f" | [Test]({rel_path_str})"
    except (ValueError, AttributeError):
        test_file_path = workspace_directory / 'test' / test_file
        if not test_file_path.exists():
            return ""
        from actions.validate.file_link_builder import FileLinkBuilder
        link_builder = FileLinkBuilder(workspace_directory)
        file_uri = link_builder.get_file_uri(str(test_file_path))
        return f" | [Test]({file_uri})"

def build_test_class_link(test_file: str, test_class: str, workspace_directory: Path, story_file_path: Optional[Path] = None) -> str:
    if not test_file or not test_class or test_class == '?':
        return ""
    
    try:
        from bot.workspace import get_python_workspace_root
        workspace_root = get_python_workspace_root()
        test_file_path = workspace_root / 'test' / test_file
        if not test_file_path.exists():
            return ""
        
        line_number = find_test_class_line(test_file_path, test_class)
        actual_file_path = test_file_path
        
        # If not found in Python file, try corresponding JS file
        if not line_number:
            js_file_path = get_js_test_file_path(test_file_path)
            if js_file_path:
                line_number = find_js_test_class_line(js_file_path, test_class)
                if line_number:
                    actual_file_path = js_file_path
        
        if not line_number:
            return ""
        
        if story_file_path:
            rel_path = actual_file_path.relative_to(workspace_root)
            rel_path_str = '/' + str(rel_path).replace('\\', '/')
            return f" | [Test]({rel_path_str}#L{line_number})"
        
        rel_path = actual_file_path.relative_to(workspace_root)
        rel_path_str = str(rel_path).replace('\\', '/')
        return f" | [Test]({rel_path_str}#L{line_number})"
    except (ValueError, AttributeError):
        test_file_path = workspace_directory / 'test' / test_file
        if not test_file_path.exists():
            return ""
        
        line_number = find_test_class_line(test_file_path, test_class)
        actual_file_path = test_file_path
        
        # If not found in Python file, try corresponding JS file
        if not line_number:
            js_file_path = get_js_test_file_path(test_file_path)
            if js_file_path:
                line_number = find_js_test_class_line(js_file_path, test_class)
                if line_number:
                    actual_file_path = js_file_path
        
        if not line_number:
            return ""
        
        try:
            from bot.workspace import get_python_workspace_root
            workspace_root = get_python_workspace_root()
            rel_path = actual_file_path.relative_to(workspace_root)
            rel_path_str = str(rel_path).replace('\\', '/')
            return f" | [Test]({rel_path_str}#L{line_number})"
        except (ValueError, AttributeError):
            from actions.validate.file_link_builder import FileLinkBuilder
            link_builder = FileLinkBuilder(workspace_directory)
            file_uri = link_builder.get_file_uri(str(actual_file_path), line_number)
            return f" | [Test]({file_uri})"

def build_test_method_link(test_file: str, test_method: str, workspace_directory: Path, story_file_path: Optional[Path] = None) -> str:
    if not test_file or not test_method or test_method == '?':
        return ""
    
    try:
        from bot.workspace import get_python_workspace_root
        workspace_root = get_python_workspace_root()
        test_file_path = workspace_root / 'test' / test_file
        if not test_file_path.exists():
            return ""
        
        line_number = find_test_method_line(test_file_path, test_method)
        actual_file_path = test_file_path
        
        # If not found in Python file, try corresponding JS file
        if not line_number:
            js_file_path = get_js_test_file_path(test_file_path)
            if js_file_path:
                line_number = find_js_test_method_line(js_file_path, test_method)
                if line_number:
                    actual_file_path = js_file_path
        
        if not line_number:
            return ""
        
        if story_file_path:
            rel_path = actual_file_path.relative_to(workspace_root)
            rel_path_str = '/' + str(rel_path).replace('\\', '/')
            return f" | [Test]({rel_path_str}#L{line_number})"
        
        rel_path = actual_file_path.relative_to(workspace_root)
        rel_path_str = str(rel_path).replace('\\', '/')
        return f" | [Test]({rel_path_str}#L{line_number})"
    except (ValueError, AttributeError):
        test_file_path = workspace_directory / 'test' / test_file
        if not test_file_path.exists():
            return ""
        
        line_number = find_test_method_line(test_file_path, test_method)
        actual_file_path = test_file_path
        
        # If not found in Python file, try corresponding JS file
        if not line_number:
            js_file_path = get_js_test_file_path(test_file_path)
            if js_file_path:
                line_number = find_js_test_method_line(js_file_path, test_method)
                if line_number:
                    actual_file_path = js_file_path
        
        if not line_number:
            return ""
        
        try:
            from bot.workspace import get_python_workspace_root
            workspace_root = get_python_workspace_root()
            rel_path = actual_file_path.relative_to(workspace_root)
            rel_path_str = str(rel_path).replace('\\', '/')
            return f" | [Test]({rel_path_str}#L{line_number})"
        except (ValueError, AttributeError):
            from actions.validate.file_link_builder import FileLinkBuilder
            link_builder = FileLinkBuilder(workspace_directory)
            file_uri = link_builder.get_file_uri(str(actual_file_path), line_number)
            return f" | [Test]({file_uri})"

def _find_ast_node_line(file_path: Path, node_name: str, node_type: type) -> Optional[int]:
    """Generic helper to find AST node line number by name and type.
    
    Args:
        file_path: Path to Python file to parse
        node_name: Name of the node to find
        node_type: Type of AST node to look for (ast.ClassDef, ast.FunctionDef, etc.)
        
    Returns:
        Line number where node is defined, or None if not found
    """
    if not file_path.exists() or not node_name or node_name == '?':
        return None
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content, filename=str(file_path))
        for node in ast.walk(tree):
            if isinstance(node, node_type) and node.name == node_name:
                return node.lineno
    except SyntaxError:
        return None
    except Exception:
        return None
    return None

def find_test_class_line(test_file_path: Path, test_class_name: str) -> Optional[int]:
    """Find line number where a test class is defined."""
    return _find_ast_node_line(test_file_path, test_class_name, ast.ClassDef)

def find_test_method_line(test_file_path: Path, test_method_name: str) -> Optional[int]:
    """Find line number where a test method/function is defined."""
    return _find_ast_node_line(test_file_path, test_method_name, ast.FunctionDef)

import re

def find_js_test_class_line(test_file_path: Path, test_class_name: str) -> Optional[int]:
    """Find line number where a JavaScript test class is defined.
    
    Looks for patterns like: test('TestClassName', ...)
    """
    if not test_file_path.exists() or not test_class_name or test_class_name == '?':
        return None
    try:
        content = test_file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        # Look for test('TestClassName', ...) pattern
        pattern = re.compile(rf"test\s*\(\s*['\"]({re.escape(test_class_name)})['\"]")
        for i, line in enumerate(lines, 1):
            if pattern.search(line):
                return i
    except Exception:
        return None
    return None

def find_js_test_method_line(test_file_path: Path, test_method_name: str) -> Optional[int]:
    """Find line number where a JavaScript test method is defined.
    
    Looks for patterns like: await t.test('test_method_name', ...) or t.test('test_method_name', ...)
    """
    if not test_file_path.exists() or not test_method_name or test_method_name == '?':
        return None
    try:
        content = test_file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        # Look for t.test('test_method_name', ...) or await t.test('test_method_name', ...) pattern
        pattern = re.compile(rf"(?:await\s+)?t\.test\s*\(\s*['\"]({re.escape(test_method_name)})['\"]")
        for i, line in enumerate(lines, 1):
            if pattern.search(line):
                return i
    except Exception:
        return None
    return None

def get_js_test_file_path(py_test_file_path: Path) -> Optional[Path]:
    """Get the corresponding JavaScript test file for a Python test file.
    
    Example: test_edit_story_nodes.py -> test_edit_story_nodes.js
    """
    if not py_test_file_path.suffix == '.py':
        return None
    js_path = py_test_file_path.with_suffix('.js')
    if js_path.exists():
        return js_path
    return None

def find_js_file_with_test_class(py_test_file_path: Path, test_class_name: str) -> tuple[Optional[Path], Optional[int]]:
    """Search all JS files in the same directory for a test class.
    
    Returns tuple of (js_file_path, line_number) or (None, None) if not found.
    """
    if not py_test_file_path.exists():
        return None, None
    
    test_dir = py_test_file_path.parent
    
    # First try the same-named JS file
    js_path = py_test_file_path.with_suffix('.js')
    if js_path.exists():
        line_number = find_js_test_class_line(js_path, test_class_name)
        if line_number:
            return js_path, line_number
    
    # Search all other JS files in the same directory
    for js_file in test_dir.glob('*.js'):
        if js_file == js_path:
            continue  # Already checked this one
        line_number = find_js_test_class_line(js_file, test_class_name)
        if line_number:
            return js_file, line_number
    
    return None, None

def find_js_file_with_test_method(py_test_file_path: Path, test_method_name: str) -> tuple[Optional[Path], Optional[int]]:
    """Search all JS files in the same directory for a test method.
    
    Returns tuple of (js_file_path, line_number) or (None, None) if not found.
    """
    if not py_test_file_path.exists():
        return None, None
    
    test_dir = py_test_file_path.parent
    
    # First try the same-named JS file
    js_path = py_test_file_path.with_suffix('.js')
    if js_path.exists():
        line_number = find_js_test_method_line(js_path, test_method_name)
        if line_number:
            return js_path, line_number
    
    # Search all other JS files in the same directory
    for js_file in test_dir.glob('*.js'):
        if js_file == js_path:
            continue  # Already checked this one
        line_number = find_js_test_method_line(js_file, test_method_name)
        if line_number:
            return js_file, line_number
    
    return None, None
"""Utility for moving test classes between test files when stories move between sub-epics."""

import ast
import re
from pathlib import Path
from typing import Optional
from datetime import datetime

def _log(message: str):
    """Write log message to file."""
    log_file = Path(__file__).parent.parent.parent / 'logs' / 'test_class_mover.log'
    log_file.parent.mkdir(exist_ok=True)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().isoformat()} {message}\n")


class TestClassMover:
    """Handles extraction and movement of test classes between files."""
    
    @staticmethod
    def extract_class(file_path: Path, class_name: str) -> Optional[str]:
        """Extract a test class from a Python file.
        
        Args:
            file_path: Path to the source test file
            class_name: Name of the class to extract
            
        Returns:
            The class code as a string, or None if not found
        """
        _log(f"[TestClassMover] Extracting class '{class_name}' from {file_path}")
        
        if not file_path.exists():
            _log(f"[TestClassMover] Source file does not exist: {file_path}")
            return None
            
        content = file_path.read_text(encoding='utf-8')
        
        # Parse the file
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            _log(f"[TestClassMover] Syntax error parsing {file_path}: {e}")
            return None
        
        # Find the class node
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                # Get the source lines
                lines = content.splitlines(keepends=True)
                start_line = node.lineno - 1  # AST uses 1-based line numbers
                
                # Find end line by looking for next class or end of file
                end_line = len(lines)
                for next_node in tree.body:
                    if isinstance(next_node, ast.ClassDef) and next_node.lineno > node.lineno:
                        end_line = next_node.lineno - 1
                        break
                
                # Extract the class code
                class_code = ''.join(lines[start_line:end_line])
                _log(f"[TestClassMover] Successfully extracted class '{class_name}' ({end_line - start_line} lines)")
                return class_code
        
        _log(f"[TestClassMover] Class '{class_name}' not found in {file_path}")
        return None
    
    @staticmethod
    def remove_class(file_path: Path, class_name: str) -> bool:
        """Remove a test class from a Python file.
        
        Args:
            file_path: Path to the source test file
            class_name: Name of the class to remove
            
        Returns:
            True if class was found and removed, False otherwise
        """
        _log(f"[TestClassMover] Removing class '{class_name}' from {file_path}")
        
        if not file_path.exists():
            _log(f"[TestClassMover] File does not exist: {file_path}")
            return False
            
        content = file_path.read_text(encoding='utf-8')
        
        # Parse the file
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            _log(f"[TestClassMover] Syntax error parsing {file_path}: {e}")
            return False
        
        # Find the class node
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                # Get the source lines
                lines = content.splitlines(keepends=True)
                start_line = node.lineno - 1
                
                # Find end line
                end_line = len(lines)
                for next_node in tree.body:
                    if isinstance(next_node, ast.ClassDef) and next_node.lineno > node.lineno:
                        end_line = next_node.lineno - 1
                        break
                
                # Remove the class (keep content before and after)
                new_content = ''.join(lines[:start_line]) + ''.join(lines[end_line:])
                
                # Clean up extra blank lines (max 2 consecutive)
                new_content = re.sub(r'\n{3,}', '\n\n', new_content)
                
                file_path.write_text(new_content, encoding='utf-8')
                _log(f"[TestClassMover] Successfully removed class '{class_name}' from {file_path}")
                return True
        
        _log(f"[TestClassMover] Class '{class_name}' not found in {file_path}")
        return False
    
    @staticmethod
    def add_class(file_path: Path, class_code: str) -> bool:
        """Add a test class to a Python file.
        
        Args:
            file_path: Path to the target test file
            class_code: The class code to add
            
        Returns:
            True if class was added successfully
        """
        _log(f"[TestClassMover] Adding class to {file_path}")
        
        if not file_path.exists():
            _log(f"[TestClassMover] Target file does not exist: {file_path}")
            return False
            
        content = file_path.read_text(encoding='utf-8')
        
        # Ensure there's proper spacing before the new class
        if content and not content.endswith('\n\n'):
            if content.endswith('\n'):
                content += '\n'
            else:
                content += '\n\n'
        
        # Add the class code
        content += class_code
        
        # Ensure file ends with newline
        if not content.endswith('\n'):
            content += '\n'
        
        file_path.write_text(content, encoding='utf-8')
        _log(f"[TestClassMover] Successfully added class to {file_path}")
        return True
    
    @staticmethod
    def move_class(source_file: Path, target_file: Path, class_name: str) -> bool:
        """Move a test class from source file to target file.
        
        Args:
            source_file: Path to the source test file
            target_file: Path to the target test file
            class_name: Name of the class to move
            
        Returns:
            True if class was moved successfully, False otherwise
        """
        _log(f"[TestClassMover] ========================================")
        _log(f"[TestClassMover] MOVING TEST CLASS: {class_name}")
        _log(f"[TestClassMover] FROM: {source_file}")
        _log(f"[TestClassMover] TO:   {target_file}")
        _log(f"[TestClassMover] ========================================")
        
        # Extract the class from source
        class_code = TestClassMover.extract_class(source_file, class_name)
        if not class_code:
            _log(f"[TestClassMover] Failed to extract class '{class_name}'")
            return False
        
        # Add to target
        if not TestClassMover.add_class(target_file, class_code):
            _log(f"[TestClassMover] Failed to add class to target file")
            return False
        
        # Remove from source
        if not TestClassMover.remove_class(source_file, class_name):
            # Rollback: remove from target since we couldn't remove from source
            _log(f"[TestClassMover] Failed to remove class from source, rolling back")
            TestClassMover.remove_class(target_file, class_name)
            return False
        
        _log(f"[TestClassMover] Successfully moved class '{class_name}'")
        _log(f"[TestClassMover] ========================================")
        return True
    
    @staticmethod
    def get_test_file_for_subepic(subepic: 'SubEpic') -> Optional[Path]:
        """Get the test file path for a SubEpic.
        
        Args:
            subepic: The SubEpic node
            
        Returns:
            Path to the test file, or None if not found
        """
        if not hasattr(subepic, 'test_file') or not subepic.test_file:
            return None
        
        # Get bot directory
        if not subepic._bot or not hasattr(subepic._bot, 'bot_paths'):
            return None
        
        workspace_dir = Path(subepic._bot.bot_paths.workspace_directory)
        test_file_path = workspace_dir / subepic.test_file
        
        return test_file_path if test_file_path.exists() else None

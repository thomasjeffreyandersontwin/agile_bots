"""Parameter objects for scanner execution.

This module consolidates scanner parameters to avoid excessive parameter passing.
These context objects can be used instead of long parameter lists.

Hierarchy:
- ScanContext: Base context with rule and story graph context
  - FileScanContext: Single file scanning context
  - CrossFileScanContext: Cross-file scanning context with all files

Usage with existing ScanConfig:
    The ScanConfig class (in rules/scan_config.py) is used at the Rule level
    to configure overall validation. These context classes are used at the
    Scanner level for individual scan operations.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from rules.rule import Rule


@dataclass
class ScanContext:
    """Base context for all scanner operations.
    
    Contains the common context needed by all scan methods:
    - rule_obj: The rule being validated
    - story_graph: The story graph containing domain context
    
    This replaces the pattern of passing rule_obj and story_graph
    as separate parameters.
    """
    rule_obj: Any = None
    story_graph: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.story_graph is None:
            self.story_graph = {}


@dataclass
class FileCollection:
    """A collection of files to scan, separated by type.
    
    This represents a set of files that can be scanned, with separate
    lists for test files and source code files.
    """
    test_files: List[Path] = field(default_factory=list)
    code_files: List[Path] = field(default_factory=list)
    
    @property
    def all_files(self) -> List[Path]:
        """Get all files as a single list."""
        return list(self.test_files) + list(self.code_files)
    
    @property
    def has_files(self) -> bool:
        """Check if there are any files to scan."""
        return bool(self.test_files or self.code_files)
    
    def __len__(self) -> int:
        return len(self.test_files) + len(self.code_files)


@dataclass
class FileScanContext(ScanContext):
    """Context for scanning a single file.
    
    Extends ScanContext with the specific file to scan.
    Used by scan_file() method.
    """
    file_path: Optional[Path] = None
    
    @property
    def exists(self) -> bool:
        """Check if the file exists."""
        return self.file_path is not None and self.file_path.exists()
    
    @property
    def is_test_file(self) -> bool:
        """Check if this is a test file based on path patterns."""
        if not self.file_path:
            return False
        
        path_str = str(self.file_path).lower()
        file_name = self.file_path.name.lower()
        
        if '/test' in path_str or '/tests' in path_str or '\\test' in path_str or '\\tests' in path_str:
            return True
        
        if file_name.startswith('test_') or file_name == 'conftest.py':
            return True
        
        return False


@dataclass
class ScanFilesContext(ScanContext):
    """Context for scanning multiple files (file-by-file).
    
    Extends ScanContext with file collections and progress callback.
    Used by scan() method.
    """
    files: FileCollection = field(default_factory=FileCollection)
    on_file_scanned: Optional[Callable] = None
    
    @property
    def test_files(self) -> List[Path]:
        """Get test files from the collection."""
        return self.files.test_files
    
    @property
    def code_files(self) -> List[Path]:
        """Get code files from the collection."""
        return self.files.code_files


@dataclass
class CrossFileScanContext(ScanContext):
    """Context for cross-file scanning operations.
    
    Extends ScanContext with:
    - changed_files: Files that changed (for incremental scans)
    - all_files: All files in scope (for cross-file comparisons)
    - status_writer: For progress output
    - max_comparisons: Limit on cross-file comparisons
    """
    changed_files: FileCollection = field(default_factory=FileCollection)
    all_files: FileCollection = field(default_factory=FileCollection)
    status_writer: Optional[Any] = None
    max_comparisons: int = 20
    
    @property
    def test_files(self) -> List[Path]:
        """Get changed test files."""
        return self.changed_files.test_files
    
    @property
    def code_files(self) -> List[Path]:
        """Get changed code files."""
        return self.changed_files.code_files
    
    @property
    def all_test_files(self) -> List[Path]:
        """Get all test files (for cross-file comparison)."""
        return self.all_files.test_files
    
    @property
    def all_code_files(self) -> List[Path]:
        """Get all code files (for cross-file comparison)."""
        return self.all_files.code_files

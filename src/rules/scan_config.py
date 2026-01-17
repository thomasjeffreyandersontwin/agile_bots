"""Configuration object for rule scanning operations."""
from typing import Dict, List, Optional, Any, Callable, TYPE_CHECKING
from pathlib import Path
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from scanners.scan_context import ScanFilesContext, CrossFileScanContext, FileCollection


@dataclass
class ScanConfig:
    """Configuration for scanner execution.
    
    This consolidates scanner parameters to avoid excessive parameter passing.
    ScanConfig is used at the Rule level to configure overall validation.
    
    For scanner-level operations, this can create context objects:
    - to_scan_files_context(rule_obj): Creates ScanFilesContext for file-by-file scanning
    - to_cross_file_context(rule_obj): Creates CrossFileScanContext for cross-file scanning
    """
    
    # Core scan data
    story_graph: Dict[str, Any]
    files: Optional[Dict[str, List[Path]]] = None
    changed_files: Optional[Dict[str, List[Path]]] = None
    
    # Scanner behavior configuration
    skip_cross_file: bool = False
    max_cross_file_comparisons: int = 20
    
    # Callbacks and output
    on_file_scanned: Optional[Callable] = None
    status_writer: Optional[Any] = None
    
    # Derived properties (computed on demand)
    _test_files: Optional[List[Path]] = field(default=None, init=False, repr=False)
    _code_files: Optional[List[Path]] = field(default=None, init=False, repr=False)
    _all_test_files: Optional[List[Path]] = field(default=None, init=False, repr=False)
    _all_code_files: Optional[List[Path]] = field(default=None, init=False, repr=False)
    
    def __post_init__(self):
        """Ensure files dict is initialized."""
        if self.files is None:
            self.files = {}
        if self.changed_files is None:
            self.changed_files = {}
    
    @property
    def test_files(self) -> List[Path]:
        """Get test files from changed_files or files."""
        if self._test_files is None:
            files_to_scan = self.changed_files if self.changed_files else self.files
            self._test_files = files_to_scan.get('test', [])
        return self._test_files
    
    @property
    def code_files(self) -> List[Path]:
        """Get code files from changed_files or files."""
        if self._code_files is None:
            files_to_scan = self.changed_files if self.changed_files else self.files
            self._code_files = files_to_scan.get('src', [])
        return self._code_files
    
    @property
    def all_test_files(self) -> List[Path]:
        """Get all test files (for cross-file scanning)."""
        if self._all_test_files is None:
            self._all_test_files = self.files.get('test', [])
        return self._all_test_files
    
    @property
    def all_code_files(self) -> List[Path]:
        """Get all code files (for cross-file scanning)."""
        if self._all_code_files is None:
            self._all_code_files = self.files.get('src', [])
        return self._all_code_files
    
    def to_scan_files_context(self, rule_obj: Any) -> 'ScanFilesContext':
        """Create a ScanFilesContext for file-by-file scanning.
        
        Args:
            rule_obj: The rule being validated
            
        Returns:
            ScanFilesContext with files and callbacks from this config
        """
        from scanners.scan_context import ScanFilesContext, FileCollection
        return ScanFilesContext(
            rule_obj=rule_obj,
            story_graph=self.story_graph,
            files=FileCollection(
                test_files=self.test_files,
                code_files=self.code_files
            ),
            on_file_scanned=self.on_file_scanned
        )
    
    def to_cross_file_context(self, rule_obj: Any) -> 'CrossFileScanContext':
        """Create a CrossFileScanContext for cross-file scanning.
        
        Args:
            rule_obj: The rule being validated
            
        Returns:
            CrossFileScanContext with changed files, all files, and settings
        """
        from scanners.scan_context import CrossFileScanContext, FileCollection
        return CrossFileScanContext(
            rule_obj=rule_obj,
            story_graph=self.story_graph,
            changed_files=FileCollection(
                test_files=self.test_files,
                code_files=self.code_files
            ),
            all_files=FileCollection(
                test_files=self.all_test_files,
                code_files=self.all_code_files
            ),
            status_writer=self.status_writer,
            max_comparisons=self.max_cross_file_comparisons
        )

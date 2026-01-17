"""Parameter objects for scanner execution."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable

@dataclass
class ScanContext:
    story_graph: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.story_graph is None:
            self.story_graph = {}


@dataclass
class FileCollection:
    test_files: List[Path] = field(default_factory=list)
    code_files: List[Path] = field(default_factory=list)
    
    @property
    def all_files(self) -> List[Path]:
        return list(self.test_files) + list(self.code_files)
    
    @property
    def has_files(self) -> bool:
        return bool(self.test_files or self.code_files)
    
    def __len__(self) -> int:
        return len(self.test_files) + len(self.code_files)


@dataclass
class FileScanContext(ScanContext):
    file_path: Optional[Path] = None
    
    @property
    def exists(self) -> bool:
        return self.file_path is not None and self.file_path.exists()
    
    @property
    def is_test_file(self) -> bool:
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
    files: FileCollection = field(default_factory=FileCollection)
    on_file_scanned: Optional[Callable] = None
    
    @property
    def test_files(self) -> List[Path]:
        return self.files.test_files
    
    @property
    def code_files(self) -> List[Path]:
        return self.files.code_files


@dataclass
class CrossFileScanContext(ScanContext):
    changed_files: FileCollection = field(default_factory=FileCollection)
    all_files: FileCollection = field(default_factory=FileCollection)
    status_writer: Optional[Any] = None
    max_comparisons: int = 20
    
    @property
    def test_files(self) -> List[Path]:
        return self.changed_files.test_files
    
    @property
    def code_files(self) -> List[Path]:
        return self.changed_files.code_files
    
    @property
    def all_test_files(self) -> List[Path]:
        return self.all_files.test_files
    
    @property
    def all_code_files(self) -> List[Path]:
        return self.all_files.code_files

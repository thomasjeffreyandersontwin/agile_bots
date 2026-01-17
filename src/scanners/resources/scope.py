
from typing import List, Set, TYPE_CHECKING
from pathlib import Path
from file import File

if TYPE_CHECKING:
    from block import Block

class Scope:
    
    def __init__(self, files: List[Path]):
        self._file_paths = files
        self._files: List[File] = []
        self._blocks: List['Block'] = []
    
    @property
    def files(self) -> List[File]:
        if not self._files:
            self._load_files()
        return self._files
    
    @property
    def blocks(self) -> List['Block']:
        if not self._blocks:
            self._blocks = self._collect_blocks_from_files()
        return self._blocks

    def _collect_blocks_from_files(self) -> List['Block']:
        blocks = []
        for file in self.files:
            blocks.extend(file.blocks)
        return blocks

    def _create_files_from_paths(self) -> List[File]:
        files = []
        for path in self._file_paths:
            if path.exists() and path.is_file():
                file = File(path, self)
                files.append(file)
        return files
    
    def _load_files(self):
        self._files = self._create_files_from_paths()



from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from scanners.violation import Violation

class CodeRepresentationCodeScanner(CodeScanner):
    
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        return []


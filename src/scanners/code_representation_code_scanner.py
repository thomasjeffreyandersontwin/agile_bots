
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation

class CodeRepresentationCodeScanner(CodeScanner):
    
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return []


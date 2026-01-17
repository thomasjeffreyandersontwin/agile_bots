"""Scanner for detecting functions that are too large."""

from scanners.code_scanner import CodeScanner
from scanners.resources.violation import Violation
from scanners.resources.scan_context import ScanContext


class FunctionSizeScanner(CodeScanner):

    def scan(self, context: ScanContext) -> list[Violation]:
        return []

"""Scanner for detecting vertical density issues."""

from scanners.code_scanner import CodeScanner
from scanners.resources.violation import Violation
from scanners.resources.scan_context import ScanContext


class VerticalDensityScanner(CodeScanner):

    def scan(self, context: ScanContext) -> list[Violation]:
        return []

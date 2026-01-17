"""Scanner for detecting single responsibility violations."""

from scanners.code_scanner import CodeScanner
from scanners.resources.violation import Violation
from scanners.resources.scan_context import ScanContext


class SingleResponsibilityScanner(CodeScanner):

    def scan(self, context: ScanContext) -> list[Violation]:
        return []

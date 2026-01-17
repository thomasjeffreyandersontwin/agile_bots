"""Scanner for detecting domain grouping issues."""

from scanners.code_scanner import CodeScanner
from scanners.resources.violation import Violation
from scanners.resources.scan_context import ScanContext


class DomainGroupingCodeScanner(CodeScanner):

    def scan(self, context: ScanContext) -> list[Violation]:
        return []

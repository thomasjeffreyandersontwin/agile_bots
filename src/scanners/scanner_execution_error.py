class ScannerExecutionError(Exception):

    def __init__(self, rule_file: str, scanner_path: str, original_error: Exception):
        self.rule_file = rule_file
        self.scanner_path = scanner_path
        self.original_error = original_error
        message = f"Scanner execution failed for rule '{rule_file}' (scanner: {scanner_path}): {original_error}"
        super().__init__(message)

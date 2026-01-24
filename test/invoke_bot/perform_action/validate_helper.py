"""
Validate Test Helper
Handles validate action, scanners, rules, violations + validate-specific instruction assertions
"""
import json
from pathlib import Path
from helpers.base_helper import BaseHelper


class ValidateTestHelper(BaseHelper):
    """Helper for validate action, scanners, and rules testing"""
    
    def assert_validate_instructions(self, instructions):
        """Assert ValidateRulesAction injected all required fields with actual rule content.
        
        Validates that instructions contain exact required fields as per validate_action.py:
        - base_instructions: list with placeholders replaced  
        - rules: list of absolute paths to rule JSON files
        - Rule content from files must appear in base_instructions
        - config_path: optional path to config file
        - template_path: optional path to template file
        
        Args:
            instructions: Instructions dict from ValidateRulesAction.do_execute()
        """
        # REQUIRED: base_instructions must be list of strings
        base_instructions = instructions.get('base_instructions')
        assert base_instructions is not None, "base_instructions field must exist"
        assert isinstance(base_instructions, list), "base_instructions must be a list"
        assert len(base_instructions) > 0, "base_instructions must not be empty"
        assert all(isinstance(line, str) for line in base_instructions), \
            "All base_instructions items must be strings"
        
        base_text = ' '.join(base_instructions)
        
        # REQUIRED: Placeholders must be replaced (validate_action.py lines 47-53)
        assert '{{rules}}' not in base_text, "{{rules}} placeholder must be replaced"
        assert '{{scanner_output}}' not in base_text, "{{scanner_output}} placeholder must be replaced"
        assert '{{schema}}' not in base_text, "{{schema}} placeholder must be replaced"
        assert '{{description}}' not in base_text, "{{description}} placeholder must be replaced"
        assert '{rules}' not in base_text, "{rules} placeholder must be replaced"
        assert '{scanner_output}' not in base_text, "{scanner_output} placeholder must be replaced"
        
        # REQUIRED: rules field must be list of absolute paths to .json files (validate_action.py lines 90-102)
        rules = instructions.get('rules')
        assert rules is not None, "rules field must exist"
        assert isinstance(rules, list), "rules must be a list"
        assert len(rules) > 0, "rules list must not be empty"
        assert all(isinstance(r, str) for r in rules), "All rules must be strings"
        assert all(r.endswith('.json') for r in rules), "All rules must be .json file paths"
        assert all('/agile_bots/bots/' in r or '\\agile_bots\\bots\\' in r for r in rules), \
            "Rules must be absolute paths in agile_bots/bots/"
        
        # REQUIRED: Load each rule file and verify content appears in instructions (validate_action.py lines 179-209)
        for rule_path in rules:
            rule_file = Path(rule_path)
            assert rule_file.exists(), f"Rule file must exist: {rule_path}"
            
            # Load rule JSON
            rule_content = json.loads(rule_file.read_text(encoding='utf-8'))
            
            # Get rule info (same as validate_action.py _format_rules_with_file_paths)
            description = rule_content.get('description', '')
            priority = rule_content.get('priority')
            
            # Verify description appears in instructions
            if description:
                assert description in base_text, \
                    f"Rule description must appear in instructions: {description[:100]}"
            
            # Verify priority appears in instructions
            if priority is not None:
                assert f"Priority {priority}" in base_text, \
                    f"Rule priority must appear in instructions: Priority {priority}"
            
            # Verify DO section appears if present
            do_section = rule_content.get('do', {})
            do_desc = do_section.get('description', '')
            if do_desc:
                assert do_desc in base_text or do_desc[:50] in base_text, \
                    f"Rule DO description must appear in instructions: {do_desc[:100]}"
            
            # Verify DON'T section appears if present
            dont_section = rule_content.get('dont', {})
            dont_desc = dont_section.get('description', '')
            if dont_desc:
                assert dont_desc in base_text or dont_desc[:50] in base_text, \
                    f"Rule DON'T description must appear in instructions: {dont_desc[:100]}"
            
            # Verify scanner status appears
            has_scanner = 'scanner' in rule_content or 'scanners' in rule_content
            scanner_status = '[Scanner]' if has_scanner else '[Manual Check]'
            assert scanner_status in base_text, \
                f"Scanner status must appear in instructions for rule: {rule_file.name}"
        
        # REQUIRED: Scanner output must be in base instructions (validate_action.py line 44)
        # Should contain either violations, scanner results, or success message
        has_scanner_output = (
            'scanner' in base_text.lower() or 
            'violations' in base_text.lower() or 
            'passed' in base_text.lower() or
            'no violations' in base_text.lower()
        )
        assert has_scanner_output, "base_instructions must contain scanner output"
        
        # OPTIONAL: config_path and template_path (validate_action.py lines 75-87)
        # These are optional but if present must be strings
        if 'config_path' in instructions:
            assert isinstance(instructions['config_path'], str), "config_path must be a string"
        if 'template_path' in instructions:
            assert isinstance(instructions['template_path'], str), "template_path must be a string"
    
    # ========================================================================
    # SETUP HELPERS - Create test data structures
    # ========================================================================
    
    def create_files_dict(self, test_files=None, code_files=None):
        """Create files dict for scanner input.
        
        Args:
            test_files: List of Path objects for test files
            code_files: List of Path objects for code files
            
        Returns:
            Dict with 'test' and/or 'src' keys containing file lists
        """
        files_dict = {}
        if test_files:
            files_dict['test'] = test_files
        if code_files:
            files_dict['src'] = code_files
        return files_dict
    
    # ========================================================================
    # ACTION HELPERS - Execute scanners (deterministic, no conditionals)
    # ========================================================================
    
    def scan_with_rule(self, rule, story_graph, files_dict=None):
        """Scan using rule.scan() method.
        
        Args:
            rule: Rule object with scanner
            story_graph: KG dict
            files_dict: Optional files dict with 'test' and/or 'src' keys
            
        Returns:
            List of violations
        """
        scanner_results = rule.scan(story_graph, files=files_dict)
        return self._extract_violations_from_results(scanner_results)
    
    def scan_test_files(self, scanner, test_files, rule, story_graph):
        """Scan test files using scanner.scan_test_file().
        
        Args:
            scanner: Scanner instance
            test_files: List of Path objects
            rule: Rule object
            story_graph: KG dict
            
        Returns:
            List of violations
        """
        violations = []
        for test_file_path in test_files:
            file_violations = scanner.scan_test_file(test_file_path, rule, story_graph)
            violations.extend(file_violations)
        return violations
    
    def scan_code_files(self, scanner, code_files, rule):
        """Scan code files using scanner.scan_code_file().
        
        Args:
            scanner: Scanner instance
            code_files: List of Path objects
            rule: Rule object
            
        Returns:
            List of violations
        """
        violations = []
        for code_file_path in code_files:
            file_violations = scanner.scan_code_file(code_file_path, rule)
            violations.extend(file_violations)
        return violations
    
    def _extract_violations_from_results(self, scanner_results):
        """Extract violations list from scanner results dict.
        
        Args:
            scanner_results: Dict from rule.scan()
            
        Returns:
            List of violations
        """
        violations = []
        
        # Direct violations list
        if 'violations' in scanner_results:
            violations = scanner_results['violations']
        
        # File-by-file violations
        if 'file_by_file' in scanner_results:
            violations.extend(scanner_results['file_by_file'].get('violations', []))
        
        # Cross-file violations
        if 'cross_file' in scanner_results:
            violations.extend(scanner_results['cross_file'].get('violations', []))
        
        return violations
    
    # ========================================================================
    # ASSERTION HELPERS - Verify scanner results
    # ========================================================================
    
    def assert_violations_found(self, violations, expected_count):
        """Assert exact number of violations found.
        
        Args:
            violations: List of violations
            expected_count: Expected number of violations
        """
        assert len(violations) == expected_count, \
            f"Expected {expected_count} violations, got {len(violations)}"
    
    def assert_no_violations(self, violations):
        """Assert no violations found.
        
        Args:
            violations: List of violations
        """
        assert len(violations) == 0, \
            f"Expected no violations, but found {len(violations)}: {violations}"
    
    def assert_scanners_loaded(self, rules, expected_count):
        """Assert exact number of scanners loaded from rules.
        
        Args:
            rules: List of Rule objects
            expected_count: Expected number of loaded scanners
        """
        scanners = [rule.scanner for rule in rules if rule.scanner is not None]
        assert len(scanners) == expected_count, \
            f"Expected {expected_count} scanners loaded, got {len(scanners)}"
        
        # Verify all loaded scanners are valid instances
        for rule in rules:
            if rule.scanner is not None:
                assert rule.has_scanner, f"Rule {rule.file_path.name} must have has_scanner=True"
                assert rule.scanner_class is not None, f"Rule {rule.file_path.name} must have scanner_class"

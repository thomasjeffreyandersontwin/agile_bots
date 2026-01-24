"""
Rules Test Helper
Handles rules action, rules digest, and rules-specific instruction assertions
"""
from pathlib import Path
import json
from helpers.base_helper import BaseHelper


class RulesTestHelper(BaseHelper):
    """Helper for rules action testing"""
    
    def assert_rules_instructions(self, result):
        """Assert RulesAction returned properly formatted instructions with rules digest.
        
        Validates that result contains:
        - instructMions: dict with display_content and base_instructions
        - Rules digest with rule descriptions, DO/DON'T sections
        - List of rule names with file paths
        - Proper formatting and structure
        
        Args:
            result: Result dict from RulesAction.do_execute()
        """
        # REQUIRED: instructions field must exist
        instructions = result.get('instructions')
        assert instructions is not None, "instructions field must exist"
        assert isinstance(instructions, dict), "instructions must be a dict"
        
        # REQUIRED: display_content field with rule list
        display_content = instructions.get('display_content', [])
        assert isinstance(display_content, list), "display_content must be a list"
        assert len(display_content) > 0, "display_content must not be empty"
        
        display_text = '\n'.join(display_content)
        
        # REQUIRED: Must show rules count
        assert 'Rules Available' in display_text, "Must show 'Rules Available' header"
        assert 'total)' in display_text, "Must show total count of rules"
        
        # REQUIRED: base_instructions field with rules digest
        base_instructions = instructions.get('base_instructions', [])
        assert isinstance(base_instructions, list), "base_instructions must be a list"
        assert len(base_instructions) > 0, "base_instructions must not be empty"
        
        base_text = '\n'.join(base_instructions)
        
        # REQUIRED: Rules digest must contain rule information
        # Should have descriptions, priorities, DO/DON'T sections
        assert len(base_text) > 100, "Rules digest must contain substantial content"
        
        # Verify at least some rules content appears
        has_rule_content = (
            'Priority' in base_text or
            'description' in base_text.lower() or
            'do' in base_text.lower() or
            "don't" in base_text.lower()
        )
        assert has_rule_content, "Rules digest must contain rule descriptions and guidance"
    
    def assert_rules_list_contains_file_paths(self, result):
        """Assert that the rules list in display_content includes file paths.
        
        Args:
            result: Result dict from RulesAction.do_execute()
        """
        instructions = result.get('instructions', {})
        display_content = instructions.get('display_content', [])
        display_text = '\n'.join(display_content)
        
        # Should contain file paths to rule files
        assert '.json' in display_text, "Display must show .json file paths"
        assert 'behaviors/' in display_text or 'behaviors\\' in display_text, \
            "Display must show paths to behavior rule files"
    
    def assert_rules_digest_contains_all_rules(self, result, expected_rule_count):
        """Assert that rules digest contains information from all rules.
        
        Args:
            result: Result dict from RulesAction.do_execute()
            expected_rule_count: Minimum number of rules expected
        """
        instructions = result.get('instructions', {})
        display_content = instructions.get('display_content', [])
        display_text = '\n'.join(display_content)
        
        # Count numbered items in display_content (1. rule_name, 2. rule_name, etc.)
        import re
        numbered_items = re.findall(r'^\d+\.', display_text, re.MULTILINE)
        actual_count = len(numbered_items)
        
        assert actual_count >= expected_rule_count, \
            f"Expected at least {expected_rule_count} rules, found {actual_count}"
    
    def assert_user_message_included(self, result, expected_message):
        """Assert that user message is included in instructions.
        
        Args:
            result: Result dict from RulesAction.do_execute()
            expected_message: Expected message text
        """
        instructions = result.get('instructions', {})
        base_instructions = instructions.get('base_instructions', [])
        base_text = '\n'.join(base_instructions)
        
        assert 'User Request:' in base_text, "Must show 'User Request:' header"
        assert expected_message in base_text, \
            f"Must include user message: {expected_message}"
    
    def assert_no_user_message_when_empty(self, result):
        """Assert that no user message section appears when message is empty.
        
        Args:
            result: Result dict from RulesAction.do_execute()
        """
        instructions = result.get('instructions', {})
        base_instructions = instructions.get('base_instructions', [])
        base_text = '\n'.join(base_instructions)
        
        assert 'User Request:' not in base_text, \
            "Should not show 'User Request:' when no message provided"

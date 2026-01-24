"""
Instructions Test Helper
Handles instruction merging, assertion, and validation
"""
from pathlib import Path
from helpers.base_helper import BaseHelper


def validate_violation_structure(violation: dict, required_fields: list) -> bool:
    """Validate that a violation dict has all required fields."""
    return all(field in violation for field in required_fields)


class InstructionsTestHelper(BaseHelper):
    """Helper for instructions testing"""
    
    def assert_instructions_have_structure(self, instructions, structure='validation_rules'):
        """Assert instructions have expected structure."""
        if structure == 'validation_rules':
            assert 'validation_rules' in instructions, "Instructions must contain 'validation_rules' key"
            validation_rules = instructions['validation_rules']
            assert len(validation_rules) > 0, "Instructions should contain validation rules"
            
            from actions.rules.rule import Rule
            
            for rule in validation_rules:
                if isinstance(rule, Rule):
                    assert hasattr(rule, 'rule_file'), f"Rule object must have 'rule_file' attribute"
                    assert hasattr(rule, 'rule_content'), f"Rule object must have 'rule_content' attribute"
                    rule_content = rule.rule_content
                elif isinstance(rule, dict):
                    assert 'rule_content' in rule, f"Rule dict must contain 'rule_content' key: {rule}"
                    rule_content = rule['rule_content']
                    if 'scanner_results' in rule:
                        scanner_results = rule['scanner_results']
                        if 'violations' in scanner_results:
                            violations = scanner_results['violations']
                            assert isinstance(violations, list), "Scanner results should contain violations list"
                            for violation in violations:
                                assert validate_violation_structure(violation, ['rule', 'line_number', 'location', 'violation_message', 'severity']), (
                                    f"Violation missing required fields: {violation}"
                                )
                else:
                    raise AssertionError(f"Rule should be a Rule object or dict, got: {type(rule)}")
                
                if isinstance(rule_content, dict):
                    assert 'scanner' in rule_content, f"Rule content must contain 'scanner' key: {rule_content}"
                    scanner_path = rule_content['scanner']
                    assert scanner_path is not None, f"Rule should have a scanner attached"
            
            assert 'base_instructions' in instructions, "Instructions must contain 'base_instructions' key"
            base_instructions = instructions['base_instructions']
            assert isinstance(base_instructions, list), "Base instructions should be a list"
        elif isinstance(structure, dict):
            for key, validator in structure.items():
                assert key in instructions, f"Instructions must contain '{key}' key"
                if callable(validator):
                    validator(instructions[key])
                elif isinstance(validator, type):
                    assert isinstance(instructions[key], validator), f"'{key}' should be of type {validator.__name__}"
                elif isinstance(validator, list):
                    assert instructions[key] in validator, f"'{key}' should be one of {validator}"
    
    def assert_config_path_matches(self, instructions, config_path, config_key='story_graph_config'):
        """Assert config path matches expected."""
        if config_key not in instructions:
            return
        config = instructions[config_key]
        if isinstance(config, dict) and 'path' in config:
            actual_path = config['path']
            if '\\' in actual_path or '/' in actual_path:
                actual_path_obj = Path(actual_path)
                config_path_obj = Path(config_path)
                assert str(actual_path_obj).replace('\\', '/').endswith(str(config_path_obj).replace('\\', '/')), \
                    f"Expected config path to end with '{config_path}', got '{actual_path}'"
            else:
                assert actual_path == config_path, f"Expected config path '{config_path}', got '{actual_path}'"
    
    def assert_instructions_merged_from_sources(self, merged_instructions, behavior, action, sources='both'):
        """Assert instructions merged from sources."""
        # Check action name (nested in action_instructions or direct key)
        if 'action_instructions' in merged_instructions:
            actual_action = merged_instructions['action_instructions'].get('name')
            assert actual_action == action, f"Expected action '{action}', got '{actual_action}'"
        elif 'action' in merged_instructions:
            assert merged_instructions['action'] == action, f"Expected action '{action}', got '{merged_instructions.get('action')}'"
        
        # Check behavior name (nested in behavior_instructions or direct key)
        if 'behavior_instructions' in merged_instructions:
            actual_behavior = merged_instructions['behavior_instructions'].get('name')
            assert actual_behavior == behavior, f"Expected behavior '{behavior}', got '{actual_behavior}'"
        elif 'behavior' in merged_instructions:
            assert merged_instructions['behavior'] == behavior, f"Expected behavior '{behavior}', got '{merged_instructions.get('behavior')}'"
        
        if sources == 'both':
            assert 'base_instructions' in merged_instructions, "Instructions must contain 'base_instructions' key"
            assert 'behavior_instructions' in merged_instructions or 'action_instructions' in merged_instructions, \
                "Instructions must contain 'behavior_instructions' or 'action_instructions' key"
        elif sources == 'base_only':
            assert 'base_instructions' in merged_instructions, "Instructions must contain 'base_instructions' key"
        elif sources == 'behavior_only':
            assert 'behavior_instructions' in merged_instructions or 'action_instructions' in merged_instructions, \
                "Instructions must contain 'behavior_instructions' or 'action_instructions' key"
    
    def assert_instructions_contain(self, instructions, content_type, **content_params):
        """Assert instructions contain specified content type."""
        if content_type == 'next_behavior_reminder':
            instructions_dict = instructions.get('instructions', {}) if isinstance(instructions, dict) else instructions
            assert instructions_dict, f"No instructions found. Result: {instructions}"
            base_instructions_list = instructions_dict.get('base_instructions', [])
            reminder_found = False
            next_behavior_found = False
            for i, instruction in enumerate(base_instructions_list):
                if 'NEXT BEHAVIOR REMINDER' in instruction:
                    reminder_found = True
                    if i + 1 < len(base_instructions_list):
                        next_instruction = base_instructions_list[i + 1]
                        if 'prioritization' in next_instruction.lower():
                            next_behavior_found = True
            assert reminder_found, "base_instructions should include 'NEXT BEHAVIOR REMINDER' section"
            assert next_behavior_found, "Reminder should mention 'prioritization' as the next behavior"
            return base_instructions_list
        
        elif content_type == 'reminder_prompt_text':
            instructions_text = ' '.join(instructions) if isinstance(instructions, list) else instructions
            assert 'next behavior in sequence' in instructions_text.lower(), "Reminder should contain 'next behavior in sequence' text"
            assert 'would you like to continue' in instructions_text.lower() or 'work on a different behavior' in instructions_text.lower(), "Reminder should contain prompt asking user if they want to continue"
        
        elif content_type == 'guardrails':
            assert 'guardrails' in instructions
            assert 'required_context' in instructions['guardrails']
            assert 'key_questions' in instructions['guardrails']['required_context']
            assert instructions['guardrails']['required_context']['key_questions'] == content_params.get('expected_questions', [])
            assert 'evidence' in instructions['guardrails']['required_context']
            assert instructions['guardrails']['required_context']['evidence'] == content_params.get('expected_evidence', [])
        
        elif content_type == 'strategy_criteria_and_assumptions':
            assert 'strategy_criteria' in instructions
            assert 'assumptions' in instructions
            assert instructions['assumptions'] == content_params.get('expected_assumptions', [])
            assert instructions['strategy_criteria'] is not None
        
        elif content_type == 'template_path':
            template_name = content_params.get('template_name')
            if 'template_path' in instructions:
                assert template_name in instructions['template_path']
        
        elif content_type == 'validation_rules':
            assert 'validation_rules' in instructions, "Instructions must contain 'validation_rules' key"
            return instructions['validation_rules']
        
        elif content_type == 'render_required_fields':
            assert instructions.strip() != ''
            assert 'render' in instructions.lower() or 'template' in instructions.lower() or 'output' in instructions.lower()
        
        elif content_type == 'render_field_values':
            assert instructions.strip() != ''
            assert 'render' in instructions.lower() or 'scenario' in instructions.lower() or 'template' in instructions.lower()
        
        else:
            raise ValueError(f"Unknown content_type: {content_type}")
    
    def assert_instructions_do_not_contain(self, instructions, content_type):
        """Assert instructions do not contain specified content type."""
        if content_type == 'next_behavior_reminder':
            if hasattr(instructions, 'data'):
                instructions_dict = instructions.data.get('instructions', {})
            else:
                instructions_dict = instructions.get('instructions', {}) if isinstance(instructions, dict) else instructions
            base_instructions_list = instructions_dict.get('base_instructions', [])
            instructions_text = ' '.join(base_instructions_list)
            assert 'NEXT BEHAVIOR REMINDER' not in instructions_text, "base_instructions should NOT include 'NEXT BEHAVIOR REMINDER' when action is not final"
        
        elif content_type == 'next_action_instructions':
            assert instructions == '' or 'complete' in instructions.lower()
        
        elif content_type == 'guardrails':
            assert 'guardrails' not in instructions or instructions['guardrails'] == {}
        
        elif content_type == 'strategy_data':
            assert 'strategy_criteria' not in instructions or instructions['strategy_criteria'] == {}
            assert 'assumptions' not in instructions or instructions['assumptions'] == []
        
        else:
            raise ValueError(f"Unknown content_type: {content_type}")
    
    def assert_template_variables_replaced(self, instructions_text, type=None):
        """Assert template variables are replaced in instructions text."""
        if type is None or type == 'build':
            assert isinstance(instructions_text, str)
            assert instructions_text.strip() != ''
        
        elif type == 'render_configs':
            assert '{{render_configs}}' not in instructions_text
            assert 'render' in instructions_text.lower()
        
        elif type == 'render_instructions':
            assert '{{render_configs}}' not in instructions_text
            assert '{{render_instructions}}' not in instructions_text
            assert instructions_text.strip() != ''
    
    def assert_instructions_match(self, instructions, expected_content):
        """Assert instructions match expected content."""
        if isinstance(expected_content, dict) and isinstance(instructions, dict):
            assert instructions == expected_content, f"Expected {expected_content}, got {instructions}"
        else:
            assert str(instructions) == str(expected_content), f"Expected {expected_content}, got {instructions}"
    
    def assert_base_instructions_present(self, instructions):
        """Assert base instructions are present (generic check)."""
        base_instructions = instructions.get('base_instructions', [])
        assert base_instructions, "base_instructions should be present"
        assert len(base_instructions) > 0, "base_instructions should not be empty"
    
    def assert_behavior_instructions_present(self, instructions):
        """Assert behavior metadata is present."""
        behavior_metadata = instructions.get('behavior_metadata') or instructions.get('behavior_instructions')
        assert behavior_metadata is not None, "behavior_metadata should be set"
    
    def assert_behavior_instructions_contain_action(self, instructions, behavior: str, action: str):
        """Assert action metadata is present."""
        action_metadata = instructions.get('action_metadata') or instructions.get('action_instructions')
        assert action_metadata is not None, "action_metadata should be set"

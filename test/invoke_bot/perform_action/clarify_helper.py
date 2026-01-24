"""
Clarify Test Helper
Handles clarify action-specific methods and instruction assertions
"""
import json
from pathlib import Path
from bot_path import BotPath
from helpers.base_helper import BaseHelper


class ClarifyTestHelper(BaseHelper):
    """Helper for clarify action-specific testing"""
    
    def get_clarification_file_path(self) -> Path:
        """Get path to clarification.json file in workspace.
        
        Returns:
            Path to clarification.json
        """
        bot_paths = BotPath(workspace_path=self.parent.workspace, bot_directory=self.parent.bot_directory)
        documentation_path = bot_paths.documentation_path
        return self.parent.workspace / documentation_path / 'clarification.json'
    
    def given_existing_clarification_data(self, existing_data: dict) -> Path:
        """Create existing clarification.json with full data structure.
        
        Args:
            existing_data: Full dict of behavior data (can contain multiple behaviors)
            
        Returns:
            Path to clarification.json file
        """
        clarification_file = self.get_clarification_file_path()
        clarification_file.parent.mkdir(parents=True, exist_ok=True)
        
        clarification_file.write_text(json.dumps(existing_data, indent=2), encoding='utf-8')
        return clarification_file
    
    def assert_clarification_file_exists(self):
        """Assert clarification.json file exists."""
        clarification_file = self.get_clarification_file_path()
        assert clarification_file.exists(), f"clarification.json should be created at {clarification_file}"
    
    def assert_clarification_contains_behavior(self, behavior_name: str, expected_answers: dict, expected_evidence: dict):
        """Assert clarification contains specific behavior with answers and evidence.
        
        Args:
            behavior_name: Behavior name
            expected_answers: Dict of expected answers
            expected_evidence: Dict of expected evidence
        """
        clarification_data = self.assert_clarification_saved(behavior_name)
        behavior_data = clarification_data[behavior_name]
        
        # Check answers
        assert 'key_questions' in behavior_data, "Behavior should have key_questions"
        assert 'answers' in behavior_data['key_questions'], "key_questions should have answers"
        actual_answers = behavior_data['key_questions']['answers']
        for key, expected_value in expected_answers.items():
            assert key in actual_answers, f"Answer '{key}' not found in {actual_answers}"
            assert actual_answers[key] == expected_value, \
                f"Expected answer['{key}'] = '{expected_value}', got '{actual_answers[key]}'"
        
        # Check evidence
        assert 'evidence' in behavior_data, "Behavior should have evidence"
        assert 'provided' in behavior_data['evidence'], "evidence should have provided"
        actual_evidence = behavior_data['evidence']['provided']
        for key, expected_value in expected_evidence.items():
            assert key in actual_evidence, f"Evidence '{key}' not found in {actual_evidence}"
            assert actual_evidence[key] == expected_value, \
                f"Expected evidence['{key}'] = '{expected_value}', got '{actual_evidence[key]}'"
    
    def assert_clarification_saved(self, behavior_name: str):
        """Assert clarification.json exists and contains behavior section.
        
        Args:
            behavior_name: Behavior name to check
        """
        clarification_file = self.get_clarification_file_path()
        assert clarification_file.exists(), f"clarification.json should be created at {clarification_file}"
        
        clarification_data = json.loads(clarification_file.read_text(encoding='utf-8'))
        assert behavior_name in clarification_data, \
            f"Behavior '{behavior_name}' should be in clarification.json. Found: {list(clarification_data.keys())}"
        
        return clarification_data
    
    def assert_clarification_not_created(self):
        """Assert clarification.json file does not exist."""
        clarification_file = self.get_clarification_file_path()
        assert not clarification_file.exists(), \
            f"clarification.json should not be created when no clarification data provided"
    
    def assert_clarification_file_not_exists(self):
        """Alias for assert_clarification_not_created."""
        self.assert_clarification_not_created()
    
    def assert_clarification_contains_answers(self, behavior_name: str, expected_answers: dict):
        """Assert clarification contains specific answers for a behavior.
        
        Args:
            behavior_name: Behavior name
            expected_answers: Dict of expected answers
        """
        clarification_data = self.assert_clarification_saved(behavior_name)
        behavior_data = clarification_data[behavior_name]
        
        assert 'key_questions' in behavior_data, "Behavior should have key_questions"
        assert 'answers' in behavior_data['key_questions'], "key_questions should have answers"
        
        actual_answers = behavior_data['key_questions']['answers']
        for key, expected_value in expected_answers.items():
            assert key in actual_answers, f"Answer '{key}' not found in {actual_answers}"
            assert actual_answers[key] == expected_value, \
                f"Expected answer['{key}'] = '{expected_value}', got '{actual_answers[key]}'"
    
    def assert_clarification_contains_evidence(self, behavior_name: str, expected_evidence: dict):
        """Assert clarification contains specific evidence for a behavior.
        
        Args:
            behavior_name: Behavior name
            expected_evidence: Dict of expected evidence
        """
        clarification_data = self.assert_clarification_saved(behavior_name)
        behavior_data = clarification_data[behavior_name]
        
        assert 'evidence' in behavior_data, "Behavior should have evidence"
        assert 'provided' in behavior_data['evidence'], "evidence should have provided"
        
        actual_evidence = behavior_data['evidence']['provided']
        for key, expected_value in expected_evidence.items():
            assert key in actual_evidence, f"Evidence '{key}' not found in {actual_evidence}"
            assert actual_evidence[key] == expected_value, \
                f"Expected evidence['{key}'] = '{expected_value}', got '{actual_evidence[key]}'"
    
    def assert_clarification_preserves_behavior(self, preserved_behavior: str, preserved_answers: dict):
        """Assert existing behavior data is preserved in clarification.json.
        
        Args:
            preserved_behavior: Name of behavior that should be preserved
            preserved_answers: Expected answers that should still exist
        """
        clarification_file = self.get_clarification_file_path()
        clarification_data = json.loads(clarification_file.read_text(encoding='utf-8'))
        
        assert preserved_behavior in clarification_data, \
            f"Preserved behavior '{preserved_behavior}' should still be in clarification.json"
        
        # Check preserved answers
        behavior_data = clarification_data[preserved_behavior]
        actual_answers = behavior_data['key_questions']['answers']
        for key, expected_value in preserved_answers.items():
            assert actual_answers[key] == expected_value, \
                f"Preserved answer['{key}'] should be '{expected_value}', got '{actual_answers[key]}'"
    
    def given_guardrails_in_workspace(self, behavior_name: str) -> tuple:
        """Create guardrails files in bot_directory with fixed sample template data.
        
        Guardrails are templates: questions to ask, evidence required, assumptions available.
        They do NOT contain answers/provided evidence - those go in workspace clarification.json.
        
        Args:
            behavior_name: Behavior name (e.g., 'shape', 'discovery')
            
        Returns:
            Tuple of (questions_file_path, evidence_file_path)
        """
        # Fixed sample questions (what to ask - no answers yet)
        sample_questions = [
            'What is the scope of this work?',
            'Who are the target users?',
            'What is the first priority action?'
        ]
        
        # Fixed sample evidence requirements (what evidence is needed - not provided yet)
        sample_evidence = [
            'Requirements doc',
            'User interviews',
            'Product roadmap'
        ]
        
        guardrails_dir = self.parent.bot_directory / 'behaviors' / behavior_name / 'guardrails' / 'required_context'
        guardrails_dir.mkdir(parents=True, exist_ok=True)
        
        questions_file = guardrails_dir / 'key_questions.json'
        questions_file.write_text(json.dumps({'questions': sample_questions}, indent=2), encoding='utf-8')
        
        evidence_file = guardrails_dir / 'evidence.json'
        evidence_file.write_text(json.dumps({'evidence': sample_evidence}, indent=2), encoding='utf-8')
        
        return questions_file, evidence_file
    
    def assert_guardrails_loaded_correctly(self, guardrails):
        """Assert guardrails templates loaded correctly (questions, evidence requirements).
        
        Guardrails are templates - they don't have answers/provided evidence yet.
        Uses same fixed sample data as given_guardrails_in_workspace.
        
        Args:
            guardrails: Guardrails object from behavior
        """
        # Expected data matches what given_guardrails_in_workspace creates
        expected_questions = [
            'What is the scope of this work?',
            'Who are the target users?',
            'What is the first priority action?'
        ]
        
        expected_evidence = [
            'Requirements doc',
            'User interviews',
            'Product roadmap'
        ]
        
        assert hasattr(guardrails, 'required_context'), "Guardrails should have required_context"
        required_context = guardrails.required_context
        assert hasattr(required_context, 'instructions'), "Required context should have instructions"
        
        instructions = required_context.instructions
        assert 'key_questions' in instructions, "Instructions should contain key_questions"
        assert 'evidence' in instructions, "Instructions should contain evidence"
        
        actual_questions = instructions['key_questions']
        actual_evidence = instructions['evidence']
        
        assert len(actual_questions) == len(expected_questions), \
            f"Expected {len(expected_questions)} questions, got {len(actual_questions)}"
        assert len(actual_evidence) == len(expected_evidence), \
            f"Expected {len(expected_evidence)} evidence items, got {len(actual_evidence)}"
        
        # Deep check: verify each question string
        for expected_q in expected_questions:
            assert expected_q in actual_questions, \
                f"Expected question '{expected_q}' not found in {actual_questions}"
        
        # Deep check: verify each evidence requirement string
        for expected_e in expected_evidence:
            assert expected_e in actual_evidence, \
                f"Expected evidence '{expected_e}' not found in {actual_evidence}"
    
    def get_clarification_file_path(self) -> Path:
        """Get path to clarification.json file in workspace.
        
        Returns:
            Path to clarification.json
        """
        from bot_path import BotPath
        bot_paths = BotPath(workspace_path=self.parent.workspace, bot_directory=self.parent.bot_directory)
        documentation_path = bot_paths.documentation_path
        return self.parent.workspace / documentation_path / 'clarification.json'
    
    def given_existing_clarification_data(self, data: dict) -> Path:
        """Create existing clarification.json file with data.
        
        Args:
            data: Dict containing clarification data (behavior sections)
            
        Returns:
            Path to created file
        """
        clarification_file = self.get_clarification_file_path()
        clarification_file.parent.mkdir(parents=True, exist_ok=True)
        clarification_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
        return clarification_file
    
    def assert_clarification_file_exists(self):
        """Assert clarification.json file exists."""
        clarification_file = self.get_clarification_file_path()
        assert clarification_file.exists(), f"clarification.json should exist at {clarification_file}"
    
    def assert_clarification_file_not_exists(self):
        """Assert clarification.json file does not exist."""
        clarification_file = self.get_clarification_file_path()
        assert not clarification_file.exists(), f"clarification.json should not exist at {clarification_file}"
    
    def assert_clarification_contains_behavior(self, behavior_name: str, expected_answers: dict = None, expected_evidence: dict = None):
        """Assert clarification file contains behavior section with expected data.
        
        Args:
            behavior_name: Behavior name (e.g., 'shape', 'discovery')
            expected_answers: Expected answers dict (optional)
            expected_evidence: Expected evidence dict (optional)
        """
        clarification_file = self.get_clarification_file_path()
        assert clarification_file.exists(), f"clarification.json should exist at {clarification_file}"
        
        clarification_data = json.loads(clarification_file.read_text(encoding='utf-8'))
        assert behavior_name in clarification_data, f"Behavior '{behavior_name}' should be in clarification data"
        
        behavior_data = clarification_data[behavior_name]
        
        if expected_answers:
            assert 'key_questions' in behavior_data, "Behavior should have key_questions"
            assert 'answers' in behavior_data['key_questions'], "key_questions should have answers"
            for key, value in expected_answers.items():
                assert behavior_data['key_questions']['answers'][key] == value, \
                    f"Expected answer '{key}' = '{value}', got '{behavior_data['key_questions']['answers'].get(key)}'"
        
        if expected_evidence:
            assert 'evidence' in behavior_data, "Behavior should have evidence"
            assert 'provided' in behavior_data['evidence'], "evidence should have provided"
            for key, value in expected_evidence.items():
                assert behavior_data['evidence']['provided'][key] == value, \
                    f"Expected evidence '{key}' = '{value}', got '{behavior_data['evidence']['provided'].get(key)}'"
    
    def assert_clarify_context_instructions(self, instructions):
        """Assert ClarifyContextAction injected all required fields.
        
        Args:
            instructions: Instructions object from ClarifyContextAction
        """
        # Check base instructions exist
        base_instructions = instructions.get('base_instructions', [])
        assert base_instructions, "base_instructions should be present"
        
        # Check ClarifyContextAction-specific fields
        guardrails = instructions.get('guardrails')
        assert guardrails is not None, "guardrails should be set"
        assert 'required_context' in guardrails, "guardrails should contain required_context"
        
        required_context = guardrails['required_context']
        assert 'key_questions' in required_context, "required_context should have key_questions"
        assert 'evidence' in required_context, "required_context should have evidence"

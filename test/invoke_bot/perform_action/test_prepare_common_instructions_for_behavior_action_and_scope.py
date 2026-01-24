"""
Test Prepare Common Instructions For Behavior, Action, and Scope

SubEpic: Prepare Common Instructions For Behavior, Action, and Scope
Parent Epic: Invoke Bot > Perform Action

Domain tests verify guardrails (clarifications, evidence, strategies) are saved correctly.
CLI tests verify guardrails commands and error handling.
"""
import pytest
from pathlib import Path
import json
import os
from helpers.bot_test_helper import BotTestHelper
from helpers import TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper


# ============================================================================
# DOMAIN TESTS - Guardrails (Clarifications, Evidence, Strategies)
# ============================================================================

class TestSaveClarificationAnswers:
    """Story: Save Clarification Answers"""
    
    def test_save_new_clarification_answers(self, tmp_path):
        """
        SCENARIO: Save new clarification answers
        GIVEN: Bot with no existing clarifications
        WHEN: User saves answers via Bot.save()
        THEN: Answers saved to clarification.json in test workspace
        """
        # Create isolated test bot
        helper = BotTestHelper(tmp_path)
        
        # Navigate to a behavior
        helper.bot.behaviors.navigate_to('shape')
        
        # Save new answers
        test_answers = {
            "What is the scope?": "Test project scope",
            "Who are the users?": "Test users"
        }
        
        helper.bot.save(
            answers=test_answers,
            evidence_provided=None,
            decisions=None,
            assumptions=None
        )
        
        # Verify answers saved to TEST workspace (not production)
        clarification_file = tmp_path / 'workspace' / 'docs' / 'stories' / 'clarification.json'
        assert clarification_file.exists(), "clarification.json should be created in test workspace"
        
        saved_data = json.loads(clarification_file.read_text())
        assert 'shape' in saved_data
        assert 'key_questions' in saved_data['shape']
        assert saved_data['shape']['key_questions']['answers'] == test_answers
    
    def test_save_merges_with_existing_clarification_answers(self, tmp_path):
        """
        SCENARIO: Save merges with existing clarification answers
        GIVEN: Bot with existing clarification answers
        WHEN: User saves additional/modified answers
        THEN: New answers merged with existing, new overrides existing for same question
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        
        # Create existing clarification data
        existing_answers = {
            "What is the scope?": "Original scope",
            "Who are the users?": "Original users"
        }
        helper.bot.save(answers=existing_answers, evidence_provided=None, decisions=None, assumptions=None)
        
        # Save new/modified answers
        new_answers = {
            "What is the scope?": "Updated scope",  # Override existing
            "What is the timeline?": "New timeline"  # Add new question
        }
        helper.bot.save(answers=new_answers, evidence_provided=None, decisions=None, assumptions=None)
        
        # Verify merge behavior
        clarification_file = tmp_path / 'workspace' / 'docs' / 'stories' / 'clarification.json'
        saved_data = json.loads(clarification_file.read_text())
        
        merged_answers = saved_data['shape']['key_questions']['answers']
        assert merged_answers["What is the scope?"] == "Updated scope"  # Updated
        assert merged_answers["Who are the users?"] == "Original users"  # Preserved
        assert merged_answers["What is the timeline?"] == "New timeline"  # Added


class TestSaveClarificationEvidence:
    """Story: Save Clarification Evidence"""
    
    def test_save_evidence_provided(self, tmp_path):
        """
        SCENARIO: Save evidence provided
        GIVEN: Bot with clarification requirements
        WHEN: User provides evidence via Bot.save()
        THEN: Evidence saved to clarification.json
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        
        test_evidence = {
            "Requirements doc": ["requirements.md", "specs.pdf"],
            "User interviews": ["interview1.txt"]
        }
        
        helper.bot.save(
            answers=None,
            evidence_provided=test_evidence,
            decisions=None,
            assumptions=None
        )
        
        clarification_file = tmp_path / 'workspace' / 'docs' / 'stories' / 'clarification.json'
        saved_data = json.loads(clarification_file.read_text())
        
        assert 'shape' in saved_data
        assert 'evidence' in saved_data['shape']
        assert saved_data['shape']['evidence']['provided'] == test_evidence


class TestSaveStrategyDecisions:
    """Story: Save Strategy Decisions"""
    
    def test_save_strategy_decisions(self, tmp_path):
        """
        SCENARIO: Save strategy decisions
        GIVEN: Bot with strategy decision criteria
        WHEN: User makes decisions via Bot.save()
        THEN: Only chosen decisions saved (not entire criteria template)
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        
        test_decisions = {
            "Approach": "Incremental development",
            "Architecture": "Microservices"
        }
        
        helper.bot.save(
            answers=None,
            evidence_provided=None,
            decisions=test_decisions,
            assumptions=None
        )
        
        strategy_file = tmp_path / 'workspace' / 'docs' / 'stories' / 'strategy.json'
        assert strategy_file.exists()
        
        saved_data = json.loads(strategy_file.read_text())
        assert 'shape' in saved_data
        # Actual format: behavior_data['decisions'] = {...}
        assert 'decisions' in saved_data['shape']
        assert saved_data['shape']['decisions'] == test_decisions
    
    def test_save_strategy_assumptions(self, tmp_path):
        """
        SCENARIO: Save strategy assumptions
        GIVEN: Bot with strategy context
        WHEN: User saves assumptions via Bot.save()
        THEN: Assumptions saved to strategy.json
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        
        test_assumptions = [
            "Users have basic tech literacy",
            "System will scale to 1000 users"
        ]
        
        helper.bot.save(
            answers=None,
            evidence_provided=None,
            decisions=None,
            assumptions=test_assumptions
        )
        
        strategy_file = tmp_path / 'workspace' / 'docs' / 'stories' / 'strategy.json'
        saved_data = json.loads(strategy_file.read_text())
        
        assert 'shape' in saved_data
        # Actual format: behavior_data['assumptions'] = [...]
        assert 'assumptions' in saved_data['shape']
        assert saved_data['shape']['assumptions'] == test_assumptions


class TestSaveMultipleGuardrails:
    """Story: Save Multiple Guardrails Together"""
    
    def test_save_all_guardrails_at_once(self, tmp_path):
        """
        SCENARIO: Save all guardrails at once
        GIVEN: Bot with current behavior
        WHEN: User saves answers, evidence, decisions, and assumptions together
        THEN: All data saved to respective files
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        
        helper.bot.save(
            answers={"What is scope?": "Full scope"},
            evidence_provided={"Requirements doc": ["req.md"]},
            decisions={"Approach": "Agile"},
            assumptions=["Team has agile experience"]
        )
        
        # Verify clarifications
        clarification_file = tmp_path / 'workspace' / 'docs' / 'stories' / 'clarification.json'
        clarification_data = json.loads(clarification_file.read_text())
        assert clarification_data['shape']['key_questions']['answers']['What is scope?'] == "Full scope"
        assert clarification_data['shape']['evidence']['provided']['Requirements doc'] == ["req.md"]
        
        # Verify strategy
        strategy_file = tmp_path / 'workspace' / 'docs' / 'stories' / 'strategy.json'
        strategy_data = json.loads(strategy_file.read_text())
        # Actual format: behavior_data['decisions'] and behavior_data['assumptions']
        assert strategy_data['shape']['decisions']['Approach'] == "Agile"
        assert strategy_data['shape']['assumptions'] == ["Team has agile experience"]
    
    def test_save_preserves_data_across_behaviors(self, tmp_path):
        """
        SCENARIO: Save preserves data across behaviors
        GIVEN: Multiple behaviors with saved guardrails
        WHEN: Switching between behaviors and saving
        THEN: Each behavior's data is preserved independently
        """
        helper = BotTestHelper(tmp_path)
        
        # Save data for 'shape' behavior
        helper.bot.behaviors.navigate_to('shape')
        helper.bot.save(
            answers={"Shape question": "Shape answer"},
            evidence_provided=None,
            decisions=None,
            assumptions=None
        )
        
        # Save data for 'discovery' behavior
        helper.bot.behaviors.navigate_to('discovery')
        helper.bot.save(
            answers={"Discovery question": "Discovery answer"},
            evidence_provided=None,
            decisions=None,
            assumptions=None
        )
        
        # Verify both behaviors' data exists
        clarification_file = tmp_path / 'workspace' / 'docs' / 'stories' / 'clarification.json'
        saved_data = json.loads(clarification_file.read_text())
        
        assert 'shape' in saved_data
        assert saved_data['shape']['key_questions']['answers']['Shape question'] == "Shape answer"
        
        assert 'discovery' in saved_data
        assert saved_data['discovery']['key_questions']['answers']['Discovery question'] == "Discovery answer"


class TestSaveFileIsolation:
    """Verify tests do NOT pollute production workspace"""
    
    def test_save_uses_test_workspace_not_production(self, tmp_path):
        """
        SCENARIO: Save uses test workspace not production
        GIVEN: Bot initialized with tmp_path workspace
        WHEN: Saving any data
        THEN: Data saved to tmp_path workspace, NOT production agile_bots/docs/stories
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        
        helper.bot.save(
            answers={"Test question": "Test answer"},
            evidence_provided=None,
            decisions=None,
            assumptions=None
        )
        
        # Verify saved to TEST workspace
        test_clarification = tmp_path / 'workspace' / 'docs' / 'stories' / 'clarification.json'
        assert test_clarification.exists(), "Should save to test workspace"
        
        # Verify NOT saved to production workspace
        production_clarification = Path(__file__).parent.parent.parent / 'docs' / 'stories' / 'clarification.json'
        if production_clarification.exists():
            prod_data = json.loads(production_clarification.read_text())
            # If production file exists, ensure our test data is NOT in it
            for behavior_data in prod_data.values():
                if isinstance(behavior_data, dict) and 'key_questions' in behavior_data:
                    answers = behavior_data['key_questions'].get('answers', {})
                    assert "Test question" not in answers, "Test data should NOT appear in production file"


# ============================================================================
# CLI TESTS - Guardrails Commands and Error Handling
# ============================================================================

class TestSaveGuardrailsUsingCLI:
    """
    Story: Save Guardrails Using CLI Commands
    
    Domain logic: test_perform_action.py::TestSaveGuardrailsViaCLI
    CLI focus: Execute save commands with parameters and verify output
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_save_answers_via_cli_command(self, tmp_path, helper_class):
        """
        SCENARIO: Save answers via CLI command
        GIVEN: CLI is at shape.clarify
        WHEN: user runs 'save --answers {"What is the scope?": "Bot system"}'
        THEN: CLI shows success message
        AND: clarification.json is updated
        
        Domain: test_save_guardrail_data_answers
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.bot.behaviors.navigate_to('shape')
        
        # When - Execute save command (simulated via action context)
        from actions.action_context import ClarifyActionContext
        action = helper.domain.bot.behaviors.current.actions.find_by_name('clarify')
        answers_data = {"What is the scope?": "Bot system"}
        context = ClarifyActionContext(answers=answers_data, evidence_provided=None)
        action.do_execute(context)
        
        # Then - File exists with saved data
        helper.domain.clarify.assert_clarification_file_exists()
        helper.domain.clarify.assert_clarification_contains_answers('shape', answers_data)
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_save_decisions_via_cli_command(self, tmp_path, helper_class):
        """
        SCENARIO: Save decisions via CLI command
        GIVEN: CLI is at shape.strategy
        WHEN: user runs 'save --decisions {"drill_down": "Deep"}'
        THEN: CLI shows success message
        AND: strategy.json is updated
        
        Domain: test_save_guardrail_data_decisions
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.bot.behaviors.navigate_to('shape')
        
        # When - Execute save command
        from actions.action_context import StrategyActionContext
        action = helper.domain.bot.behaviors.current.actions.find_by_name('strategy')
        decisions_data = {"drill_down": "Deep"}
        context = StrategyActionContext(decisions_made=decisions_data, assumptions_made=None)
        action.do_execute(context)
        
        # Then - File exists with saved data
        helper.domain.strategy.assert_strategy_file_exists()
        helper.domain.strategy.assert_strategy_contains_behavior('shape', expected_decisions=decisions_data)


# ============================================================================
# STORY: Handle Errors
# ============================================================================

class TestHandleErrorsUsingCLI:
    """
    Story: Handle Errors Using CLI
    
    CLI focus: Error display and validation messages
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_invalid_command_shows_error(self, tmp_path, helper_class):
        """
        SCENARIO: Invalid command shows error (all channels)
        GIVEN: CLI is at shape.build
        WHEN: user enters 'invalid_command'
        THEN: CLI displays error message in appropriate channel format
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'build')
        
        # When
        cli_response = helper.cli_session.execute_command('invalid_command')
        
        # Then - Error message shown
        assert 'error' in cli_response.output.lower() or 'unknown' in cli_response.output.lower()


# ============================================================================
# STORY: Display Status Tree with behavior.action Commands
# ============================================================================
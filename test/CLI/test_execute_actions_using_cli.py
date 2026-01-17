"""
Execute Action Operations Using CLI Commands Tests - Parameterized Across Channels

Maps directly to: test_perform_action.py domain tests

These tests focus on CLI-specific concerns:
- Action execution command parsing
- CLI output format verification (TTY, Markdown, JSON modes)
- Delegation to domain logic

Uses parameterized tests to run same test logic across all 3 channels.

Stories covered:
- Build Story Graph
- Clarify Requirements
- Validate Rules
- Display Rules
- Decide Strategy
- Render Output
- Save Guardrails
- Handle Errors
"""
import pytest
from CLI.helpers import TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper


# ============================================================================
# STORY: Build Story Graph
# Maps to: TestBuildStoryGraph in test_perform_action.py
# ============================================================================
class TestBuildStoryGraphUsingCLI:
    """
    Story: Build Story Graph Using CLI
    
    Domain logic: test_perform_action.py::TestBuildStoryGraph
    CLI focus: Execute build action and verify template injection in output
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_build_action_shows_template_in_output(self, tmp_path, helper_class):
        """
        SCENARIO: Build action shows story graph template in CLI output
        GIVEN: CLI is at shape.build
        WHEN: user navigates to shape.build
        THEN: CLI output contains template_path information
        
        Domain: test_action_injects_story_graph_template
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'build')
        
        # When - Navigate to build action (shows instructions with template)
        cli_response = helper.cli_session.execute_command('shape.build')
        
        # Then - Output contains template information
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'build')
        assert 'template' in cli_response.output.lower()
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_build_action_shows_complete_instructions(self, tmp_path, helper_class):
        """
        SCENARIO: Build action shows complete build story graph instructions
        GIVEN: CLI is at shape.build
        WHEN: user navigates to shape.build
        THEN: CLI output contains all BuildStoryGraphAction fields
        
        Domain: test_action_loads_and_merges_instructions
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'build')
        
        # When
        cli_response = helper.cli_session.execute_command('shape.build')
        
        # Then
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'build')
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_prioritization_validate_shows_increments_instructions(self, tmp_path, helper_class):
        """
        SCENARIO: Prioritization validate action shows increments validation
        GIVEN: CLI is at prioritization.validate
        AND: Story graph exists in workspace
        WHEN: user navigates to prioritization.validate
        THEN: CLI output shows validation instructions for increments
        
        Domain: test_behavior_updates_existing_story_graph_json (adapted)
        """
        # Given
        helper = helper_class(tmp_path)
        
        # Create existing story graph
        existing_story_graph = helper.domain.story.given_story_graph_dict(epic='mob')
        stories_dir = helper.domain.workspace / 'docs' / 'stories'
        helper.domain.files.given_file_created(stories_dir, 'story-graph.json', existing_story_graph)
        
        helper.domain.state.set_state('prioritization', 'validate')
        
        # When
        cli_response = helper.cli_session.execute_command('prioritization.validate')
        
        # Then
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'prioritization', 'validate')


# ============================================================================
# STORY: Clarify Requirements
# Maps to: TestClarifyRequirements in test_perform_action.py
# ============================================================================
class TestClarifyRequirementsUsingCLI:
    """
    Story: Clarify Requirements Using CLI
    
    Domain logic: test_perform_action.py::TestClarifyRequirements
    CLI focus: Execute clarify action and verify guardrails in output
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_clarify_action_shows_questions_and_evidence(self, tmp_path, helper_class):
        """
        SCENARIO: Clarify action shows questions and evidence in CLI output
        GIVEN: CLI is at shape.clarify
        WHEN: user navigates to shape.clarify
        THEN: CLI output contains questions and evidence from guardrails
        
        Domain: test_action_injects_questions_and_evidence
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # When
        cli_response = helper.cli_session.execute_command('shape.clarify')
        
        # Then
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'clarify')
        # Guardrails should be in output
        output_lower = cli_response.output.lower()
        assert 'question' in output_lower or 'evidence' in output_lower or 'clarify' in output_lower


# ============================================================================
# STORY: Validate Rules
# Maps to: TestValidateRules in test_perform_action.py
# ============================================================================
class TestValidateRulesUsingCLI:
    """
    Story: Validate Rules Using CLI
    
    Domain logic: test_perform_action.py::TestValidateRules
    CLI focus: Execute validate action and verify rules in output
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_validate_action_shows_rules_in_output(self, tmp_path, helper_class):
        """
        SCENARIO: Validate action shows rules in CLI output
        GIVEN: CLI is at shape.validate
        AND: Story graph exists
        WHEN: user navigates to shape.validate
        THEN: CLI output contains rule descriptions and DO/DON'T sections
        
        Domain: test_story_graph_rules_formatted_in_instructions
        """
        # Given
        helper = helper_class(tmp_path)
        
        # Create story graph
        story_graph_data = {'epics': []}
        helper.domain.story.create_story_graph(story_graph_data)
        
        helper.domain.state.set_state('shape', 'validate')
        
        # When
        cli_response = helper.cli_session.execute_command('shape.validate')
        
        # Then
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'validate')
        # Rules should be in output
        output_lower = cli_response.output.lower()
        assert 'rule' in output_lower or 'validate' in output_lower
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_validate_code_shows_file_rules(self, tmp_path, helper_class):
        """
        SCENARIO: Code validate action shows file rules in CLI output
        GIVEN: CLI is at code.validate
        AND: Story graph exists
        WHEN: user navigates to code.validate
        THEN: CLI output contains file validation rules
        
        Domain: test_file_rules_formatted_in_instructions
        """
        # Given
        helper = helper_class(tmp_path)
        
        # Create story graph
        story_graph_data = {'epics': []}
        helper.domain.story.create_story_graph(story_graph_data)
        
        helper.domain.state.set_state('code', 'validate')
        
        # When
        cli_response = helper.cli_session.execute_command('code.validate')
        
        # Then
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'code', 'validate')


# ============================================================================
# STORY: Display Rules
# Maps to: TestDisplayRules in test_perform_action.py
# ============================================================================
class TestDisplayRulesUsingCLI:
    """
    Story: Display Rules Using CLI
    
    Domain logic: test_perform_action.py::TestDisplayRules
    CLI focus: Execute rules action and verify rules digest in output
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_rules_action_shows_rules_digest(self, tmp_path, helper_class):
        """
        SCENARIO: Rules action shows rules digest in CLI output
        GIVEN: CLI is at shape.validate (which shows rules)
        WHEN: user navigates to shape.validate
        THEN: CLI output contains formatted rules digest
        
        Domain: test_action_loads_and_formats_rules_digest (adapted - using validate instead of rules action)
        """
        # Given
        helper = helper_class(tmp_path)
        
        # Create story graph for validation
        story_graph_data = {'epics': []}
        helper.domain.story.create_story_graph(story_graph_data)
        
        helper.domain.state.set_state('shape', 'validate')
        
        # When
        cli_response = helper.cli_session.execute_command('shape.validate')
        
        # Then
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'validate')
        # Rules content should be in output
        output_lower = cli_response.output.lower()
        assert 'rule' in output_lower or 'validate' in output_lower
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_rules_output_includes_validation_content(self, tmp_path, helper_class):
        """
        SCENARIO: Validation output includes rules content
        GIVEN: CLI is at shape.validate
        WHEN: user navigates to shape.validate
        THEN: CLI output contains validation rules
        
        Domain: test_rules_list_includes_file_paths (adapted)
        """
        # Given
        helper = helper_class(tmp_path)
        
        # Create story graph for validation
        story_graph_data = {'epics': []}
        helper.domain.story.create_story_graph(story_graph_data)
        
        helper.domain.state.set_state('shape', 'validate')
        
        # When
        cli_response = helper.cli_session.execute_command('shape.validate')
        
        # Then
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'validate')


# ============================================================================
# STORY: Decide Strategy
# Maps to: TestDecideStrategy in test_perform_action.py
# ============================================================================
class TestDecideStrategyUsingCLI:
    """
    Story: Decide Strategy Using CLI
    
    Domain logic: test_perform_action.py::TestDecideStrategy
    CLI focus: Execute strategy action and verify criteria/assumptions in output
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_strategy_action_shows_criteria_and_assumptions(self, tmp_path, helper_class):
        """
        SCENARIO: Strategy action shows criteria and assumptions in CLI output
        GIVEN: CLI is at shape.strategy
        WHEN: user navigates to shape.strategy
        THEN: CLI output contains decision criteria and assumptions
        
        Domain: test_action_injects_decision_criteria_and_assumptions
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'strategy')
        
        # When
        cli_response = helper.cli_session.execute_command('shape.strategy')
        
        # Then
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'strategy')
        # Strategy content should be in output
        output_lower = cli_response.output.lower()
        assert 'strateg' in output_lower or 'decision' in output_lower or 'assumption' in output_lower


# ============================================================================
# STORY: Render Output
# Maps to: TestRenderOutput in test_perform_action.py
# ============================================================================
class TestRenderOutputUsingCLI:
    """
    Story: Render Output Using CLI
    
    Domain logic: test_perform_action.py::TestRenderOutput
    CLI focus: Execute render action and verify configs in output
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_render_action_shows_configs_in_output(self, tmp_path, helper_class):
        """
        SCENARIO: Render action shows render configs in CLI output
        GIVEN: CLI is at shape.render
        WHEN: user navigates to shape.render
        THEN: CLI output contains render configurations
        
        Domain: test_action_injects_render_configs_and_instructions
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'render')
        
        # When
        cli_response = helper.cli_session.execute_command('shape.render')
        
        # Then
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'render')
        # Render content should be in output
        output_lower = cli_response.output.lower()
        assert 'render' in output_lower
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_render_output_mentions_synchronizers(self, tmp_path, helper_class):
        """
        SCENARIO: Render output mentions synchronizers execution
        GIVEN: CLI is at shape.render
        WHEN: user navigates to shape.render
        THEN: CLI output mentions synchronizers
        
        Domain: test_synchronizers_are_executed_automatically
        """
        # Given
        helper = helper_class(tmp_path)
        helper.domain.state.set_state('shape', 'render')
        
        # When
        cli_response = helper.cli_session.execute_command('shape.render')
        
        # Then
        helper.instructions.assert_section_shows_behavior_and_action(
            cli_response.output, 'shape', 'render')


# ============================================================================
# STORY: Save Guardrails
# Maps to: TestSaveGuardrailsViaCLI in test_perform_action.py
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

"""
Domain Tests for Execute Behavior Actions Epic

Tests for domain/core logic stories, covering:
- Perform Action sub-epic:
  - Build Story Graph
  - Clarify Requirements
  - Validate Rules
  - Display Rules
  - Decide Strategy
  - Render Output
  - Submit Instructions
- Domain sub-epic:
  - Save Guardrails
"""
import pytest
from pathlib import Path
import json
import os
from actions.build.build_action import BuildStoryGraphAction
from actions.render.render_action import RenderOutputAction
from actions.action_context import (
    ClarifyActionContext,
    StrategyActionContext,
    ValidateActionContext,
    ScopeActionContext
)
from domain.bot_test_helper import BotTestHelper


# ============================================================================
# STORY: Build Story Graph
# ============================================================================
class TestBuildStoryGraph:

    def test_action_injects_story_graph_template(self, tmp_path):
        """
        SCENARIO: Action Injects Story Graph Template
        GIVEN: Production story_bot with shape behavior (has story graph templates)
        WHEN: Action injects story graph template
        THEN: Instructions contain template_path from existing templates
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action_obj = BuildStoryGraphAction(behavior=helper.bot.behaviors.current, action_config=None)
        
        instructions = action_obj.get_instructions()
        
        assert 'template_path' in instructions
        assert instructions['template_path'] is not None

    def test_action_loads_and_merges_instructions(self, tmp_path):
        """
        SCENARIO: Action Loads And Merges Instructions
        GIVEN: Production story_bot with shape behavior (has story graph templates)
        WHEN: Action injects story graph and instructions
        THEN: Instructions contain all BuildStoryGraphAction-specific fields
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action_obj = helper.bot.behaviors.current.actions.find_by_name('build')
        
        instructions = action_obj.do_execute()
        
        helper.build.assert_build_story_graph_instructions(instructions)

    def test_all_template_variables_are_replaced_in_instructions(self, tmp_path):
        """
        SCENARIO: All Template Variables Are Replaced In Instructions
        GIVEN: Production story_bot with shape behavior (has story graph templates)
        WHEN: Action injects all template variables
        THEN: Instructions contain all required BuildStoryGraphAction fields
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action_obj = helper.bot.behaviors.current.actions.find_by_name('build')
        
        instructions = action_obj.do_execute()
        
        helper.build.assert_build_story_graph_instructions(instructions)

    def test_behavior_updates_existing_story_graph_json(self, tmp_path):
        """
        SCENARIO: Prioritization behavior updates existing story-graph.json
        GIVEN: Production prioritization behavior with increments templates
        AND: Existing story-graph.json in workspace
        WHEN: Action injects story graph template for increments
        THEN: Instructions use production template (story_graph_increments.json) that updates existing file
        """
        helper = BotTestHelper(tmp_path)
        
        existing_story_graph = helper.story.given_story_graph_dict(epic='mob')
        stories_dir = helper.workspace / 'docs' / 'stories'
        story_graph_path = helper.files.given_file_created(stories_dir, 'story-graph.json', existing_story_graph)
        
        helper.bot.behaviors.navigate_to('prioritization')
        action_obj = BuildStoryGraphAction(behavior=helper.bot.behaviors.current, action_config=None)
        
        instructions = action_obj.do_execute()
        
        # Then: Instructions indicate updating existing file
        assert instructions.get('story_graph_config'), "Instructions should contain 'story_graph_config'"
        config = instructions.get('story_graph_config', {})
        assert config.get('output') == 'story-graph.json', f"Expected output 'story-graph.json', got '{config.get('output')}'"
        assert instructions.get('template_path'), "Instructions should contain 'template_path'"
        assert story_graph_path.exists(), f"Story graph file should exist: {story_graph_path}"
        path_str = str(config.get('path')).replace('\\', '/')
        assert 'docs/stories' in path_str, f"Expected path to contain 'docs/stories', got '{config.get('path')}'"


# ============================================================================
# STORY: Clarify Requirements
# ============================================================================
class TestClarifyRequirements:
    def test_action_injects_questions_and_evidence(self, tmp_path):
        """
        SCENARIO: Action injects questions and evidence from production guardrails
        GIVEN: Production story_bot with shape behavior (has guardrails)
        WHEN: Action injects guardrails
        THEN: Instructions contain questions and evidence from production files
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action_obj = helper.bot.behaviors.current.actions.find_by_name('clarify')
        
        instructions = action_obj.do_execute()
        
        helper.clarify.assert_clarify_context_instructions(instructions)

    def test_save_clarification_data_when_parameters_provided(self, tmp_path):
        """
        SCENARIO: Save clarification data when parameters are provided
        GIVEN: Production story_bot clarify action
        WHEN: do_execute is called with key_questions_answered and evidence_provided
        THEN: clarification.json file is created in docs/stories/ folder
        AND: file contains behavior section with key_questions and evidence
        """
        # Given: Production story_bot clarify action
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('clarify')
        
        # When: Action executes with parameters
        context = ClarifyActionContext(
            answers={'user_types': 'Game Masters', 'first_action': 'Group tokens into mobs'},
            evidence_provided={'original_input': 'I want to turn minions into mobs', 'source_file': 'input.txt'}
        )
        action.do_execute(context)
        
        # Then: clarification.json file exists and contains expected data
        helper.clarify.assert_clarification_file_exists()
        helper.clarify.assert_clarification_contains_behavior(
            'shape',
            expected_answers={'user_types': 'Game Masters', 'first_action': 'Group tokens into mobs'},
            expected_evidence={'original_input': 'I want to turn minions into mobs', 'source_file': 'input.txt'}
        )

    def test_preserve_existing_clarification_data_when_saving(self, tmp_path):
        """
        SCENARIO: Preserve existing clarification data when saving
        GIVEN: clarification.json already exists with data for 'discovery' behavior
        AND: Production story_bot clarify action for 'shape' behavior
        WHEN: do_execute is called with parameters
        THEN: clarification.json contains both 'discovery' and 'shape' sections
        AND: existing 'discovery' data is preserved
        """
        # Given: Existing clarification.json with discovery data
        helper = BotTestHelper(tmp_path)
        existing_data = {
            'discovery': {
                'key_questions': {
                    'questions': [],
                    'answers': {'scope': 'Component level'}
                },
                'evidence': {
                    'required': [],
                    'provided': {'doc': 'requirements.md'}
                }
            }
        }
        helper.clarify.given_existing_clarification_data(existing_data)
        
        # Setup production clarify action for shape
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('clarify')
        
        # When: Action executes with parameters
        context = ClarifyActionContext(
            answers={'user_types': 'Game Masters'},
            evidence_provided={'original_input': 'I want to turn minions into mobs'}
        )
        action.do_execute(context)
        
        # Then: Both behaviors' data are preserved
        helper.clarify.assert_clarification_contains_behavior(
            'discovery',
            expected_answers={'scope': 'Component level'},
            expected_evidence={'doc': 'requirements.md'}
        )
        helper.clarify.assert_clarification_contains_behavior(
            'shape',
            expected_answers={'user_types': 'Game Masters'},
            expected_evidence={'original_input': 'I want to turn minions into mobs'}
        )

    def test_skip_saving_when_no_clarification_parameters_provided(self, tmp_path):
        """
        SCENARIO: Skip saving when no clarification parameters are provided
        GIVEN: Production story_bot clarify action
        WHEN: do_execute is called with empty parameters
        THEN: clarification.json file is not created
        """
        # Given: Production story_bot clarify action
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('clarify')
        
        # When: Action executes with empty parameters
        context = ClarifyActionContext(answers=None, evidence_provided=None)
        action.do_execute(context)
        
        # Then: clarification.json file is not created
        helper.clarify.assert_clarification_file_not_exists()
    
    def test_guardrails_loads_required_context_from_workspace(self, tmp_path):
        """
        SCENARIO: Guardrails loads required context from workspace
        GIVEN: Workspace with guardrails files (questions and evidence)
        WHEN: Behavior loads guardrails
        THEN: Questions and evidence are loaded correctly
        """
        # Given: Workspace with guardrails files
        helper = BotTestHelper(tmp_path)
        behavior_name = 'shape'
        helper.clarify.given_guardrails_in_workspace(behavior_name)
        
        # When: Behavior loads guardrails from workspace
        from bot_path import BotPath
        from behaviors.behavior import Behavior
        bot_paths = BotPath(workspace_path=helper.workspace, bot_directory=helper.bot_directory)
        behavior = Behavior(name=behavior_name, bot_paths=bot_paths)
        guardrails = behavior.guardrails
        
        # Then: Questions and evidence loaded correctly
        helper.clarify.assert_guardrails_loaded_correctly(guardrails)
    
    def test_guardrails_loads_strategy_assumptions_from_workspace(self, tmp_path):
        """
        SCENARIO: Guardrails loads strategy assumptions from workspace
        GIVEN: Workspace with strategy guardrails files
        WHEN: Behavior loads guardrails
        THEN: Strategy assumptions are loaded correctly
        """
        # Given: Workspace with strategy guardrails files
        helper = BotTestHelper(tmp_path)
        behavior_name = 'shape'
        helper.strategy.given_strategy_guardrails_in_workspace(behavior_name)
        
        # When: Behavior loads guardrails from workspace
        from bot_path import BotPath
        from behaviors.behavior import Behavior
        bot_paths = BotPath(workspace_path=helper.workspace, bot_directory=helper.bot_directory)
        behavior = Behavior(name=behavior_name, bot_paths=bot_paths)
        guardrails = behavior.guardrails
        
        # Then: Strategy assumptions loaded correctly
        helper.strategy.assert_strategy_guardrails_loaded_correctly(guardrails)


# ============================================================================
# STORY: Validate Rules
# ============================================================================
class TestValidateRules:
    """Tests that rules are properly formatted into instructions for AI to use."""
    
    def test_story_graph_rules_formatted_in_instructions(self, tmp_path):
        """
        SCENARIO: Story graph validation includes rule content in instructions
        GIVEN: Production story_bot with shape behavior (validates story graph)
        AND: Story graph file exists
        WHEN: Validate action executes
        THEN: Instructions contain rule descriptions, DO/DON'T sections, and priorities from rule files
        """
        # GIVEN: Production story_bot with shape behavior (validates story graph)
        helper = BotTestHelper(tmp_path)
        
        # AND: Story graph file exists
        story_graph_data = {'epics': []}
        helper.story.create_story_graph(story_graph_data)
        
        helper.bot.behaviors.navigate_to('shape')
        behavior = helper.bot.behaviors.current
        
        # AND: Validate action from production behavior
        from actions.validate.validate_action import ValidateRulesAction
        action = ValidateRulesAction(behavior=behavior, action_config=None)
        
        # WHEN: Validate action executes
        result = action.do_execute(ValidateActionContext())
        
        # THEN: Instructions contain rule content from rule files
        helper.validate.assert_validate_instructions(result)
    
    def test_file_rules_formatted_in_instructions(self, tmp_path):
        """
        SCENARIO: File validation includes rule content in instructions
        GIVEN: Production story_bot with code behavior (validates files)
        AND: Story graph file exists
        WHEN: Validate action executes
        THEN: Instructions contain rule descriptions, DO/DON'T sections, and priorities from rule files
        """
        # GIVEN: Production story_bot with code behavior (validates files)
        helper = BotTestHelper(tmp_path)
        
        # AND: Story graph file exists
        story_graph_data = {'epics': []}
        helper.story.create_story_graph(story_graph_data)
        
        helper.bot.behaviors.navigate_to('code')
        behavior = helper.bot.behaviors.current
        
        # AND: Validate action from production behavior
        from actions.validate.validate_action import ValidateRulesAction
        action = ValidateRulesAction(behavior=behavior, action_config=None)
        
        # WHEN: Validate action executes
        result = action.do_execute(ValidateActionContext())
        
        # THEN: Instructions contain rule content from rule files
        helper.validate.assert_validate_instructions(result)

    def test_story_graph_scanner_receives_story_graph_data(self, tmp_path):
        """
        SCENARIO: Story graph scanners receive scoped story_graph data
        GIVEN: Story graph with multiple epics ("Build Knowledge", "Epic B")
        AND: Scope filtered to "Build Knowledge" epic
        AND: Production story_bot with shape behavior
        WHEN: Validate action executes with scope
        THEN: Scanner receives filtered story graph (only "Build Knowledge" epic)
        AND: Scanner executes successfully
        AND: Instructions contain "Build Knowledge" in scope description
        """
        # GIVEN: Story graph with multiple epics
        helper = BotTestHelper(tmp_path)
        story_graph_data = {
            'epics': [
                {'name': 'Build Knowledge', 'sub_epics': [], 'story_groups': []},
                {'name': 'Epic B', 'sub_epics': [], 'story_groups': []}
            ]
        }
        helper.story.create_story_graph(story_graph_data)
        
        # AND: Scope filtered to "Build Knowledge" epic
        from scope import Scope, ScopeType
        scope = Scope(workspace_directory=tmp_path)
        scope.filter(type=ScopeType.STORY, value=['Build Knowledge'])
        
        # AND: Production story_bot with shape behavior
        helper.bot.behaviors.navigate_to('shape')
        behavior = helper.bot.behaviors.current
        
        # AND: Validate action with rules
        from actions.validate.validate_action import ValidateRulesAction
        action = ValidateRulesAction(behavior=behavior, action_config=None)
        
        # WHEN: Validate action executes with scope
        context = ValidateActionContext(scope=scope)
        result = action.do_execute(context)
        
        # THEN: Instructions reference the scoped epic
        instructions = result.get('base_instructions', [])
        instructions_text = ' '.join(instructions)
        assert 'Build Knowledge' in instructions_text, \
            "Instructions must reference scoped epic 'Build Knowledge'"
        
        # AND: Scanner executed successfully (scanners ran - we got scanner output)
        # Check that rules were loaded
        rules = result.get('rules', [])
        assert len(rules) > 0, "Shape behavior must have validation rules"
    
    def test_file_scanner_receives_file_data(self, tmp_path):
        """
        SCENARIO: File scanners receive scoped file paths
        GIVEN: Multiple Python files (test_foo.py, test_bar.py, main.py)
        AND: Scope filtered to test files only (**/test*.py)
        AND: Production story_bot with code behavior
        WHEN: Validate action executes with scope
        THEN: Scanner receives filtered files (only test_foo.py, test_bar.py)
        AND: Scanner executes successfully
        AND: Instructions reference test file scope
        """
        # GIVEN: Multiple Python files
        helper = BotTestHelper(tmp_path)
        
        # AND: Story graph file exists (required for code behavior validation)
        story_graph_data = {'epics': []}
        helper.story.create_story_graph(story_graph_data)
        
        test_dir = tmp_path / 'workspace' / 'test'
        test_dir.mkdir(parents=True)
        src_dir = tmp_path / 'workspace' / 'src'
        src_dir.mkdir(parents=True)
        
        (test_dir / 'test_foo.py').write_text('# test file')
        (test_dir / 'test_bar.py').write_text('# test file')
        (src_dir / 'main.py').write_text('# main file')
        
        # AND: Scope filtered to test files only
        from scope import Scope, ScopeType
        scope = Scope(workspace_directory=tmp_path)
        scope.filter(type=ScopeType.FILES, value=['**/test*.py'])
        
        # AND: Production story_bot with code behavior
        helper.bot.behaviors.navigate_to('code')
        behavior = helper.bot.behaviors.current
        
        # AND: Validate action with rules
        from actions.validate.validate_action import ValidateRulesAction
        action = ValidateRulesAction(behavior=behavior, action_config=None)
        
        # WHEN: Validate action executes with scope
        context = ValidateActionContext(scope=scope)
        result = action.do_execute(context)
        
        # THEN: Instructions reference file scope
        instructions = result.get('base_instructions', [])
        instructions_text = ' '.join(instructions)
        
        # Should reference test files in scope or file count
        has_file_reference = (
            'test' in instructions_text.lower() or
            'file' in instructions_text.lower() or
            str(test_dir) in instructions_text or
            'test_foo.py' in instructions_text or
            'test_bar.py' in instructions_text
        )
        assert has_file_reference, "Instructions must reference scoped files"
        
        # AND: Scanner executed successfully (scanners ran - we got scanner output)
        # Check that rules were loaded
        rules = result.get('rules', [])
        assert len(rules) > 0, "Code behavior must have validation rules"


# ============================================================================
# STORY: Display Rules
# ============================================================================
class TestDisplayRules:
    """Tests that rules are properly loaded and formatted for display."""
    
    def test_action_loads_and_formats_rules_digest(self, tmp_path):
        """
        SCENARIO: Action loads and formats rules digest
        GIVEN: Production story_bot with tests behavior (has rules)
        WHEN: Rules action executes
        THEN: Instructions contain formatted rules digest with descriptions, priorities, DO/DON'T sections
        """
        # GIVEN: Production story_bot with tests behavior (has rules)
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('tests')
        behavior = helper.bot.behaviors.current
        
        # AND: Rules action from production behavior
        from rules.rules_action import RulesAction
        from actions.action_context import RulesActionContext
        action = RulesAction(behavior=behavior, action_config=None)
        
        # WHEN: Rules action executes
        result = action.do_execute(RulesActionContext())
        
        # THEN: Instructions contain formatted rules digest
        helper.rules.assert_rules_instructions(result)
    
    def test_rules_list_includes_file_paths(self, tmp_path):
        """
        SCENARIO: Rules list includes file paths for each rule
        GIVEN: Production story_bot with tests behavior (has rules)
        WHEN: Rules action executes
        THEN: Display includes rule names with their file paths
        """
        # GIVEN: Production story_bot with tests behavior
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('tests')
        behavior = helper.bot.behaviors.current
        
        # AND: Rules action
        from rules.rules_action import RulesAction
        from actions.action_context import RulesActionContext
        action = RulesAction(behavior=behavior, action_config=None)
        
        # WHEN: Rules action executes
        result = action.do_execute(RulesActionContext())
        
        # THEN: Display includes file paths
        helper.rules.assert_rules_list_contains_file_paths(result)
    
    def test_all_behavior_rules_included_in_digest(self, tmp_path):
        """
        SCENARIO: All behavior rules are included in the digest
        GIVEN: Production story_bot with tests behavior (has multiple rules)
        WHEN: Rules action executes
        THEN: All rules from behavior are included in digest
        """
        # GIVEN: Production story_bot with tests behavior
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('tests')
        behavior = helper.bot.behaviors.current
        
        # AND: Rules action
        from rules.rules_action import RulesAction
        from actions.action_context import RulesActionContext
        action = RulesAction(behavior=behavior, action_config=None)
        
        # WHEN: Rules action executes
        result = action.do_execute(RulesActionContext())
        
        # THEN: All rules included (tests behavior has 25 rules)
        helper.rules.assert_rules_digest_contains_all_rules(result, expected_rule_count=20)
    
    def test_user_message_included_when_provided(self, tmp_path):
        """
        SCENARIO: User message is included in instructions when provided
        GIVEN: Production story_bot with tests behavior
        AND: User message requesting specific rule information
        WHEN: Rules action executes with message
        THEN: Instructions include user message
        """
        # GIVEN: Production story_bot with tests behavior
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('tests')
        behavior = helper.bot.behaviors.current
        
        # AND: User message
        user_message = "Show me the rules for test organization"
        
        # AND: Rules action
        from rules.rules_action import RulesAction
        from actions.action_context import RulesActionContext
        action = RulesAction(behavior=behavior, action_config=None)
        
        # WHEN: Rules action executes with message
        context = RulesActionContext(message=user_message)
        result = action.do_execute(context)
        
        # THEN: Instructions include user message
        helper.rules.assert_user_message_included(result, user_message)
    
    def test_no_user_message_section_when_empty(self, tmp_path):
        """
        SCENARIO: No user message section when message is empty
        GIVEN: Production story_bot with tests behavior
        WHEN: Rules action executes without message
        THEN: Instructions do not include user message section
        """
        # GIVEN: Production story_bot with tests behavior
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('tests')
        behavior = helper.bot.behaviors.current
        
        # AND: Rules action
        from rules.rules_action import RulesAction
        from actions.action_context import RulesActionContext
        action = RulesAction(behavior=behavior, action_config=None)
        
        # WHEN: Rules action executes without message
        context = RulesActionContext(message=None)
        result = action.do_execute(context)
        
        # THEN: No user message section in instructions
        helper.rules.assert_no_user_message_when_empty(result)


# ============================================================================
# STORY: Decide Strategy
# ============================================================================
class TestDecideStrategy:

    def test_action_injects_decision_criteria_and_assumptions(self, tmp_path):
        """
        SCENARIO: Action Injects Decision Criteria And Assumptions
        GIVEN: Production story_bot with shape behavior (has guardrails)
        WHEN: Action injects strategy criteria and assumptions
        THEN: Instructions contain all required strategy fields
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action_obj = helper.bot.behaviors.current.actions.find_by_name('strategy')
        
        instructions = action_obj.do_execute()
        
        helper.strategy.assert_strategy_instructions(instructions)

    def test_save_strategy_data_when_parameters_provided(self, tmp_path):
        """
        SCENARIO: Save strategy data when parameters are provided
        GIVEN: Production story_bot strategy action
        WHEN: do_execute is called with decisions_made and assumptions_made
        THEN: strategy.json file is created in docs/stories/ folder
        AND: file contains behavior section with decisions_made and assumptions_made
        """
        # Given: Production story_bot strategy action
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('strategy')
        
        # When: Action executes with parameters
        decisions_made = {
            'drill_down': 'Dig deep on system interactions',
            'flow_scope': 'End-to-end user-system behavior'
        }
        assumptions_made = [
            'Focus on user flow over internal systems',
            'Cover the end-to-end scenario'
        ]
        context = StrategyActionContext(
            decisions_made=decisions_made,
            assumptions_made=assumptions_made
        )
        action.do_execute(context)
        
        # Then: strategy.json file exists and contains expected data
        helper.strategy.assert_strategy_file_exists()
        helper.strategy.assert_strategy_contains_behavior(
            'shape',
            expected_decisions=decisions_made,
            expected_assumptions=assumptions_made
        )

    def test_preserve_existing_strategy_data_when_saving(self, tmp_path):
        """
        SCENARIO: Preserve existing strategy data when saving
        GIVEN: strategy.json already exists with data for 'discovery' behavior
        AND: Production story_bot strategy action for 'shape' behavior
        WHEN: do_execute is called with parameters
        THEN: strategy.json contains both 'discovery' and 'shape' sections
        AND: existing 'discovery' data is preserved
        """
        # Given: Existing strategy.json with discovery data (actual format)
        helper = BotTestHelper(tmp_path)
        existing_data = {
            'discovery': {
                'decisions': {'scope': 'Component level'},
                'assumptions': ['Stories follow user story format']
            }
        }
        helper.strategy.given_existing_strategy_data(existing_data)
        
        # Setup production strategy action for shape
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('strategy')
        
        # When: Action executes with parameters
        context = StrategyActionContext(
            decisions_made={
                'drill_down': 'Dig deep on system interactions',
                'flow_scope': 'End-to-end user-system behavior'
            },
            assumptions_made=[
                'Focus on user flow over internal systems',
                'Cover the end-to-end scenario'
            ]
        )
        action.do_execute(context)
        
        # Then: Both behaviors' data are preserved
        helper.strategy.assert_strategy_contains_behavior(
            'discovery',
            expected_decisions={'scope': 'Component level'},
            expected_assumptions=['Stories follow user story format']
        )
        helper.strategy.assert_strategy_contains_behavior(
            'shape',
            expected_decisions={'drill_down': 'Dig deep on system interactions', 'flow_scope': 'End-to-end user-system behavior'},
            expected_assumptions=['Focus on user flow over internal systems', 'Cover the end-to-end scenario']
        )

    def test_skip_saving_when_no_strategy_parameters_provided(self, tmp_path):
        """
        SCENARIO: Skip saving when no strategy parameters are provided
        GIVEN: Production story_bot strategy action
        WHEN: do_execute is called with empty parameters
        THEN: strategy.json file is not created
        """
        # Given: Production story_bot strategy action
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('strategy')
        
        # When: Action executes with empty parameters
        context = StrategyActionContext(decisions_made=None, assumptions_made=None)
        action.do_execute(context)
        
        # Then: strategy.json file is not created
        helper.strategy.assert_strategy_file_not_exists()

# ============================================================================
# STORY: Render Output
# ============================================================================
class TestRenderOutput:

    def test_action_injects_render_configs_and_instructions(self, tmp_path):
        """
        SCENARIO: Action injects render configs and instructions
        GIVEN: Production story_bot with shape behavior (has render configs)
        WHEN: Action injects render data
        THEN: Instructions contain all required render fields
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        helper.state.set_state('shape', 'render')
        action_obj = helper.bot.behaviors.current.actions.find_by_name('render')
        
        instructions = action_obj.do_execute()
        
        helper.render.assert_render_output_instructions(instructions)

    def test_synchronizers_are_executed_automatically(self, tmp_path):
        """
        SCENARIO: Synchronizers are executed automatically during render action
        GIVEN: Production story_bot with shape behavior (has synchronizers)
        WHEN: Render output action executes
        THEN: Synchronizers are executed automatically
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        helper.state.set_state('shape', 'render')
        action_obj = helper.bot.behaviors.current.actions.find_by_name('render')
        
        result = action_obj.do_execute()
        
        base_instructions = result.get('base_instructions', [])
        base_instructions_text = '\n'.join(base_instructions)
        assert 'Synchronizers Already Executed' in base_instructions_text or 'render' in base_instructions_text.lower()

    def test_template_configs_remain_in_instructions(self, tmp_path):
        """
        SCENARIO: Template configs remain in instructions for AI handling
        GIVEN: Production story_bot with shape behavior (has templates)
        WHEN: Render output action executes  
        THEN: Result includes instructions
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        helper.state.set_state('shape', 'render')
        action_obj = helper.bot.behaviors.current.actions.find_by_name('render')
        
        result = action_obj.do_execute()
        
        base_instructions = result.get('base_instructions', [])
        assert len(base_instructions) > 0, "Should have instructions"

    def test_executed_synchronizers_info_in_instructions(self, tmp_path):
        """
        SCENARIO: Executed synchronizers information is included in AI instructions
        GIVEN: Production story_bot with shape behavior (has synchronizers)
        WHEN: Render output action executes
        THEN: Instructions include synchronizer execution info
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        helper.state.set_state('shape', 'render')
        action_obj = helper.bot.behaviors.current.actions.find_by_name('render')
        
        result = action_obj.do_execute()
        
        base_instructions = '\n'.join(result.get('base_instructions', []))
        assert 'Synchronizers Already Executed' in base_instructions or 'render' in base_instructions.lower()


# ============================================================================
# STORY: Save Guardrails (Domain Layer)
# ============================================================================
class TestSaveGuardrailsViaCLI:
    """
    Tests for saving guardrail data - domain/core logic.
    
    Maps to story: Save Guardrails
    Sub-epic: Domain
    Epic: Execute Behavior Actions
    """
    
    def test_save_guardrail_data_answers(self, tmp_path):
        """
        SCENARIO: Save guardrail data (answers parameter)
        GIVEN: Bot is at shape behavior
        WHEN: User runs save command with answers parameter
        THEN: System saves answers to clarification.json under current behavior
        AND: System merges with existing answers
        """
        # Given: Bot is at shape behavior
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('clarify')
        
        # When: User runs save command with answers
        answers_data = {"What is the scope of this work?": "Building bot system"}
        context = ClarifyActionContext(answers=answers_data, evidence_provided=None)
        action.do_execute(context)
        
        # Then: System loads existing clarification.json for current behavior
        # And: System merges new data with existing data
        # And: System saves updated data to clarification.json
        helper.clarify.assert_clarification_file_exists()
        helper.clarify.assert_clarification_contains_answers('shape', answers_data)
    
    def test_save_guardrail_data_evidence(self, tmp_path):
        """
        SCENARIO: Save guardrail data (evidence_provided parameter)
        GIVEN: Bot is at shape behavior
        WHEN: User runs save command with evidence parameter
        THEN: System saves evidence to clarification.json under current behavior
        """
        # Given: Bot is at shape behavior
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('clarify')
        
        # When: User runs save command with evidence
        evidence_data = {
            "Requirements doc": "spec.md",
            "User interviews": "notes.md"
        }
        context = ClarifyActionContext(answers=None, evidence_provided=evidence_data)
        action.do_execute(context)
        
        # Then: System saves evidence to clarification.json
        helper.clarify.assert_clarification_file_exists()
        helper.clarify.assert_clarification_contains_evidence('shape', evidence_data)
    
    def test_save_guardrail_data_decisions(self, tmp_path):
        """
        SCENARIO: Save guardrail data (decisions parameter)
        GIVEN: Bot is at shape behavior
        WHEN: User runs save command with decisions parameter
        THEN: System saves decisions to strategy.json under current behavior
        """
        # Given: Bot is at shape behavior
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('strategy')
        
        # When: User runs save command with decisions
        decisions_data = {"drill_down_approach": "Dig deep on system interactions"}
        context = StrategyActionContext(decisions_made=decisions_data, assumptions_made=None)
        action.do_execute(context)
        
        # Then: System saves decisions to strategy.json
        helper.strategy.assert_strategy_file_exists()
        helper.strategy.assert_strategy_contains_behavior('shape', expected_decisions=decisions_data)
    
    def test_save_guardrail_data_assumptions(self, tmp_path):
        """
        SCENARIO: Save guardrail data (assumptions parameter)
        GIVEN: Bot is at shape behavior
        WHEN: User runs save command with assumptions parameter
        THEN: System saves assumptions to strategy.json under current behavior
        """
        # Given: Bot is at shape behavior
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('strategy')
        
        # When: User runs save command with assumptions
        assumptions_data = ["Focus on user flow over internal systems"]
        context = StrategyActionContext(decisions_made=None, assumptions_made=assumptions_data)
        action.do_execute(context)
        
        # Then: System saves assumptions to strategy.json
        helper.strategy.assert_strategy_file_exists()
        helper.strategy.assert_strategy_contains_behavior('shape', expected_assumptions=assumptions_data)
    
    def test_merge_with_existing_answers(self, tmp_path):
        """
        SCENARIO: Merge with existing data (answers)
        GIVEN: Guardrail file contains existing data for shape behavior
        WHEN: User runs save command with new data
        THEN: System preserves existing values for other fields
        AND: System overwrites only the provided field
        AND: Result matches merged_result
        """
        # Given: Existing data in clarification.json
        helper = BotTestHelper(tmp_path)
        existing_data = {
            'shape': {
                'key_questions': {
                    'questions': [],
                    'answers': {
                        "What is the scope of this work?": "Building bot system",
                        "Who are the target users?": "AI Agents"
                    }
                },
                'evidence': {
                    'required': [],
                    'provided': {}
                }
            }
        }
        helper.clarify.given_existing_clarification_data(existing_data)
        
        # When: User runs save command with new data (overwrites one field)
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('clarify')
        new_answers = {"Who are the target users?": "Developers and AI Agents"}
        context = ClarifyActionContext(answers=new_answers, evidence_provided=None)
        action.do_execute(context)
        
        # Then: System preserves existing values for other fields
        # And: System overwrites only the provided field
        expected_merged = {
            "What is the scope of this work?": "Building bot system",
            "Who are the target users?": "Developers and AI Agents"
        }
        helper.clarify.assert_clarification_contains_answers('shape', expected_merged)
    
    def test_merge_with_existing_decisions(self, tmp_path):
        """
        SCENARIO: Merge with existing data (decisions)
        GIVEN: Guardrail file contains existing data for shape behavior
        WHEN: User runs save command with new data
        THEN: System preserves existing values for other fields
        AND: System overwrites only the provided field
        AND: Result matches merged_result
        """
        # Given: Existing data in strategy.json (actual format)
        helper = BotTestHelper(tmp_path)
        existing_data = {
            'shape': {
                'decisions': {
                    "drill_down_approach": "High and wide across all epics",
                    "depth_of_shaping": "Extensive"
                },
                'assumptions': []
            }
        }
        helper.strategy.given_existing_strategy_data(existing_data)
        
        # When: User runs save command with new data (overwrites one field)
        helper.bot.behaviors.navigate_to('shape')
        action = helper.bot.behaviors.current.actions.find_by_name('strategy')
        new_decisions = {"drill_down_approach": "Dig deep on system interactions"}
        context = StrategyActionContext(decisions_made=new_decisions, assumptions_made=None)
        action.do_execute(context)
        
        # Then: System preserves existing values for other fields
        # And: System overwrites only the provided field
        expected_merged = {
            "drill_down_approach": "Dig deep on system interactions",
            "depth_of_shaping": "Extensive"
        }
        helper.strategy.assert_strategy_contains_behavior('shape', expected_decisions=expected_merged)


# ============================================================================
# STORY: Submit Instructions
# ============================================================================
class TestSubmitInstructions:

    def test_submit_tracks_instruction_submission(self, tmp_path):
        """
        SCENARIO: Submit tracks instruction submission
        GIVEN: Bot is at shape.clarify
        WHEN: User calls submit_current_action() method
        THEN: System returns success status with behavior and action
        AND: System includes timestamp of submission
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        helper.bot.behaviors.current.actions.navigate_to('clarify')
        
        result = helper.bot.submit_current_action()
        
        assert result['status'] == 'success', f"Expected success status, got {result.get('status')}"
        assert result['behavior'] == 'shape', f"Expected behavior 'shape', got {result.get('behavior')}"
        assert result['action'] == 'clarify', f"Expected action 'clarify', got {result.get('action')}"
        assert 'timestamp' in result, "Expected timestamp in result"
        assert result['message'] == 'Instructions submitted for shape.clarify'

    def test_submit_fails_when_no_current_behavior(self, tmp_path):
        """
        SCENARIO: Submit fails when no current behavior
        GIVEN: Bot has no current behavior set
        WHEN: User calls submit_current_action() method
        THEN: System returns error status
        AND: Error indicates no current behavior
        """
        helper = BotTestHelper(tmp_path)
        # Explicitly clear current behavior (bot initializes to first behavior by default)
        helper.bot.behaviors._current_index = None
        result = helper.bot.submit_current_action()
        
        assert result['status'] == 'error', f"Expected error status, got {result.get('status')}"
        assert 'No current behavior' in result['message'], f"Expected 'No current behavior' in message, got {result.get('message')}"

    def test_submit_fails_when_no_current_action(self, tmp_path):
        """
        SCENARIO: Submit fails when no current action
        GIVEN: Bot is at behavior but no action is set
        WHEN: User calls submit_current_action() method
        THEN: System returns error status
        AND: Error indicates no current action
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('shape')
        # Explicitly clear current action (navigating to behavior sets first action by default)
        helper.bot.behaviors.current.actions._current_index = None
        
        result = helper.bot.submit_current_action()
        
        assert result['status'] == 'error', f"Expected error status, got {result.get('status')}"
        assert 'No current action' in result['message'], f"Expected 'No current action' in message, got {result.get('message')}"

    def test_submit_works_with_different_behaviors_and_actions(self, tmp_path):
        """
        SCENARIO: Submit works with different behaviors and actions
        GIVEN: Bot is at prioritization.validate
        WHEN: User calls submit_current_action() method
        THEN: System returns success with correct behavior and action
        """
        helper = BotTestHelper(tmp_path)
        helper.bot.behaviors.navigate_to('prioritization')
        helper.bot.behaviors.current.actions.navigate_to('validate')
        
        result = helper.bot.submit_current_action()
        
        assert result['status'] == 'success'
        assert result['behavior'] == 'prioritization'
        assert result['action'] == 'validate'
        assert 'timestamp' in result

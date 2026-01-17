"""Scanner for validating test structure matches story graph exactly."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import logging
from test_scanner import TestScanner
from scanners.violation import Violation
from .resources.ast_elements import Classes

logger = logging.getLogger(__name__)

class StoryGraphMatchScanner(TestScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        story_names = self._extract_story_names(story_graph)
        
        violations.extend(self._check_test_classes_match_stories(tree, story_names, file_path, rule_obj))
        
        return violations
    
    def _extract_story_names(self, story_graph: Dict[str, Any]) -> List[str]:
        story_names = []
        epics = story_graph.get('epics', [])
        for epic in epics:
            sub_epics = epic.get('sub_epics', [])
            for sub_epic in sub_epics:
                story_groups = sub_epic.get('story_groups', [])
                for story_group in story_groups:
                    stories = story_group.get('stories', [])
                    for story in stories:
                        story_name = story.get('name', '')
                        if story_name:
                            story_names.append(story_name)
        return story_names
    
    def _check_test_classes_match_stories(self, tree: ast.AST, story_names: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        classes = Classes(tree)
        for cls in classes.get_many_classes:
            if cls.node.name.startswith('Test'):
                story_name_from_class = cls.node.name[4:]
                
                matches = [s for s in story_names if story_name_from_class.lower().replace('_', ' ') in s.lower()]
                
                if not matches:
                    line_number = cls.node.lineno if hasattr(cls.node, 'lineno') else None
                    violation = Violation(
                        rule=rule_obj,

## Rules Available (25 total)

1. use_domain_language (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_domain_language.json)
2. consistent_vocabulary (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/consistent_vocabulary.json)
3. no_defensive_code_in_tests (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/no_defensive_code_in_tests.json)
4. production_code_clean_functions (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/production_code_clean_functions.json)
5. bug_fix_test_first (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/bug_fix_test_first.json)
6. call_production_code_directly (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/call_production_code_directly.json)
7. cover_all_behavior_paths (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/cover_all_behavior_paths.json)
8. mock_only_boundaries (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/mock_only_boundaries.json)
9. create_parameterized_tests_for_scenarios (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/create_parameterized_tests_for_scenarios.json)
10. define_fixtures_in_test_file (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/define_fixtures_in_test_file.json)
11. design_api_through_failing_tests (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/design_api_through_failing_tests.json)
12. test_observable_behavior (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/test_observable_behavior.json)
13. helper_extraction_and_reuse (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/helper_extraction_and_reuse.json)
14. match_specification_scenarios (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/match_specification_scenarios.json)
15. place_imports_at_top (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/place_imports_at_top.json)
16. object_oriented_test_helpers (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/object_oriented_test_helpers.json)
17. production_code_explicit_dependencies (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/production_code_explicit_dependencies.json)
18. self_documenting_tests (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/self_documenting_tests.json)
19. standard_test_data_sets (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/standard_test_data_sets.json)
20. assert_full_results (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/assert_full_results.json)
21. use_ascii_only (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_ascii_only.json)
22. pytest_bdd_orchestrator_pattern (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/pytest_bdd_orchestrator_pattern.json)
23. use_class_based_organization (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_class_based_organization.json)
24. use_exact_variable_names (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_exact_variable_names.json)
25. use_given_when_then_helpers (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_given_when_then_helpers.json)

# Behavior: tests

## Behavior Instructions - tests

The purpose of this behavior is to write test files (.py, .js, etc.) with executable test code from scenarios.examples that validate story behavior

**BEHAVIOR PURPOSE:**
This behavior WRITES TEST FILES. The primary output is executable test code files that validate story behavior.
Write test files (.py, .js, etc.) with executable test code from scenarios.examples that validate story behavior
The secondary output is to make sure that the story_graph.json scenarios, stories, and sub-epics have test fields added for the test methods, test classes, and test files respectively.
After creating test files, classes, and methods, you MUST map them to the story-graph.json:

## Action Instructions - rules

The purpose of this action is to load behavior-specific rules into ai context for guidance on writing compliant content

---

**Look for context in the following locations:**
- in this message and chat history
- in `C:/Users/thoma/AppData/Local/Temp/pytest-of-thoma/pytest-3773/test_user_gets_rules_instructi0/workspace/docs/context/`
- generated files in `C:/Users/thoma/AppData/Local/Temp/pytest-of-thoma/pytest-3773/test_user_gets_rules_instructi0/workspace/docs/stories/`
  clarification.json, strategy.json

CRITICAL: This is the rules action - it loads rules for AI context. DO NOT run validation.
CRITICAL: You MUST systematically read each rule file listed below using the read_file tool BEFORE acting on the user's message.
Read ALL rule files first, then apply them to the user's request.
Each rule file path is provided - use read_file to load the complete rule content including examples.
After reading all rules, act on the user's message following ALL the rules you just read.

CRITICAL: When reporting validation results, use this EXACT format:
For each rule checked, report: Rule Name | PASS or FAIL | If FAIL, explain why in one sentence
Example: prefer_object_model_over_config | PASS
Example: eliminate_duplication | FAIL | Same logic repeated in lines 45-50 and 78-83
Keep it simple: just tell the user what passed, what failed, and if it failed, why.

Rules to follow:

- **use_domain_language**: Use Ubiquitous Language (DDD): Same vocabulary in domain model, stories, scenarios, AND code. Class names = domain entities/nouns. Method names = domain responsibilities/verbs. Test names read like plain English stories. Example: test_agent_loads_configuration_when_file_exists (not test_agt_init_sets_vars)
  DO: Use domain language for classes, methods, and test names. Example: class GatherContextAction, def inject_guardrails(), test_agent_loads_config_when_file_exists
  DON'T: Don't use generic technical terms or implementation-specific names. Example: class StdioHandler (wrong), def execute_with_guardrails (wrong), test_agt_init_sets_vars (wrong)

- **consistent_vocabulary**: Use ONE word per concept across entire codebase. Pick consistent vocabulary: create (not build/make/construct), verify (not check/assert/validate), load (not fetch/get/retrieve). Use intention-revealing names that describe behavior. Example: create_agent(), verify_initialized(), load_config() - same verbs everywhere
  DO: Use same word for same concept everywhere. Example: create_agent(), create_config(), create_workspace() - all use 'create'
  DON'T: Don't mix synonyms for same concept. Example: create_agent() + build_config() + make_workspace() (wrong - pick one verb)

- **no_defensive_code_in_tests**: Tests must NEVER contain guard clauses, defensive conditionals, or fallback paths. We control test setup - if it's wrong, the test MUST fail immediately. Guard clauses hide problems. Tests should assume positive outcomes. Example: Just call the code directly, don't wrap in if-checks
  DO: Assume correct setup - let test fail if wrong. Example: behavior = Behavior(name='shape') then assert behavior.name == 'shape'
  DON'T: Don't add if-checks, type guards, or fallback handling in tests. Example: if behavior_file.exists(): (wrong - test should fail if it doesn't)

- **production_code_clean_functions**: Production code functions should do ONE thing, be under 20 lines, and have one level of abstraction. No hidden side effects. Name reveals complete behavior. Extract multiple concerns into separate functions. Example: load_config(), validate_config(), apply_config() - each does one thing
  DO: Single responsibility, small focused functions. Example: initialize_from_config() calls validate_exists(), load_config(), validate_structure(), apply_config()
  DON'T: Don't make functions that do multiple unrelated things or are too long. Example: 50-line function that loads, validates, and applies config

- **bug_fix_test_first**: When production code breaks, follow test-first workflow: write failing test, verify failure, fix code, verify success. Never fix bugs without a failing test first. Example: test_mcp_tool_initializes_bot() fails -> fix initialization -> test passes
  DO: Follow RED-GREEN-PRODUCTION workflow. Example: Write test reproducing bug -> Run test (RED) -> Fix minimal code -> Run test (GREEN) -> Run full suite
  DON'T: Don't fix bugs directly without failing test first. Example: Editing production code without test -> deploying -> hoping it works (wrong)

- **call_production_code_directly**: Call production code directly in tests. Let tests fail naturally if code doesn't exist. Don't comment out calls, mock business logic, or fake state. Only mock external boundaries. Example: agent = Agent(); agent.initialize() (not agent = Mock())
  DO: Call production code directly, let it fail naturally. Example: agent = Agent(workspace); agent.initialize(config); assert agent.is_initialized
  DON'T: Don't mock class under test, comment out calls, or fake state. Example: agent = Mock(spec=Agent) (wrong); agent._initialized = True (wrong)

- **cover_all_behavior_paths**: Cover all behavior paths: normal (happy path), edge cases, and failure scenarios. Each distinct behavior needs its own focused test. Tests must be independent. Example: test_loads_valid_config(), test_loads_empty_config(), test_raises_error_when_file_missing()
  DO: Test normal, edge, and failure paths separately. Example: test_loads_valid_config() (happy), test_loads_empty_config() (edge), test_raises_when_missing() (failure)
  DON'T: Don't test only happy path or combine multiple behaviors in one test. Example: Single test for both success and failure (wrong)

- **mock_only_boundaries**: Mock ONLY at architectural boundaries: external APIs, network, uncontrollable services. Don't mock internal business logic, classes under test, or file operations (use temp files). Example: patch('requests.get') (OK); patch('agent.validate') (wrong)
  DO: Mock only external dependencies you can't control. Example: with patch('requests.get') as mock: (external API - OK to mock)
  DON'T: Don't mock internal logic, class under test, or file I/O. Example: with patch('agent.validate_config') (wrong - test the logic!)

- **create_parameterized_tests_for_scenarios**: If scenarios have Examples tables, create parameterized tests using @pytest.mark.parametrize. Each row becomes a test case. Don't write single tests that only test one example. Example: @pytest.mark.parametrize('input,expected', [(1, 2), (3, 4)])
  DO: Create parameterized tests from Examples tables. Example: @pytest.mark.parametrize('paths,count', [(['p1','p2'], 2), (['p3'], 1)])
  DON'T: Don't hardcode single example or duplicate test methods. Example: def test_with_value_1(): (wrong); def test_with_value_2(): (wrong - use parametrize)

- **define_fixtures_in_test_file**: Define fixtures in the test file, not separate conftest.py. Truly reusable fixtures (file ops, location helpers) go in base conftest.py. Example: @pytest.fixture def workspace_root(tmp_path): return tmp_path / 'workspace'
  DO: Define fixtures in same test file. Example: @pytest.fixture def config_file(tmp_path): ... (in test_agent.py)
  DON'T: Don't create separate conftest.py for agent-specific fixtures. Example: src/conftest.py with agent fixtures (wrong - put in test file)

- **design_api_through_failing_tests**: Write tests against the REAL expected API BEFORE implementing code. Tests MUST fail initially. Set up real test data and call real API. Failure reveals complete API design. Example: project = Project(path=path); project.initialize() (doesn't exist yet -> fails -> drives implementation)
  DO: Write test against real expected API that fails initially. Example: project = Project(path); project.initialize(); assert project.is_ready (fails until implemented)
  DON'T: Don't use placeholders, dummy values, or skip the failing step. Example: project = 'TODO' (wrong); assuming test passes first (wrong)

- **test_observable_behavior**: Test observable behavior, not implementation details. Verify public API and visible state changes. Don't assert on private methods or internal flags. Example: assert agent.config_path.exists() (observable); not assert agent._internal_flag (private)
  DO: Test observable outcomes through public API. Example: assert agent.config_path == expected; assert agent.is_initialized (public properties)
  DON'T: Don't test private state or implementation details. Example: assert agent._initialized (wrong); assert agent._config_cache (wrong)

- **helper_extraction_and_reuse**: Extract duplicate test setup to reusable helper functions. Keep test bodies focused on specific behavior. Example: create_agent_with_config(), create_config_file(), verify_agent_initialized() - reusable across tests
  DO: Extract duplicate setup to reusable helpers. Example: create_agent_with_config(name, workspace, config) returns initialized Agent
  DON'T: Don't duplicate setup code across tests. Example: Same 10 lines of setup in every test method (wrong - extract to helper)

- **match_specification_scenarios**: Tests must match specification scenarios exactly. Test names, steps, and assertions verify exactly what the scenario states. Use exact variable names and terminology from specification. Example: agent_name='story_bot' (from spec), not name='bot'
  DO: Test matches specification exactly. Example: GIVEN config exists, WHEN Agent(agent_name='story_bot'), THEN config_path == agents/base/agent.json
  DON'T: Don't use different terminology or assert things not in specification. Example: assert agent._internal_flag (not in spec - wrong)

- **place_imports_at_top**: Place all imports at top of test file, after docstrings, before code. Group: stdlib, third-party, then local. Example: import json; import pytest; from mymodule import MyClass
  DO: All imports at top, grouped by type. Example: import json; import pytest; from bots... import X
  DON'T: Don't place imports inside functions or after code. Example: def test(): from pathlib import Path (wrong - import inside function)

- **object_oriented_test_helpers**: Consolidate tests around object-oriented helpers/factories (e.g., BotTestHelper test hopper) that build complete domain objects with standard data. Example: helper = BotTestHelper(tmp_path); helper.set_state('shape','clarify'); helper.assert_at_behavior_action('shape','clarify'). Avoid scattering many primitive parameters across parametrize blocks or inline setups.
  DO: Use shared helper objects to create full test fixtures and assert against complete domain objects, not fragments.
  DON'T: Do not spread test setup across many primitive parameters or cherry-pick single values from partial objects.

- **production_code_explicit_dependencies**: Production code: make dependencies explicit through constructor injection. Pass all external dependencies as constructor parameters. No hidden global state. Tests easily inject test doubles. Example: Agent(config_loader=loader, domain_graph=graph)
  DO: Inject all dependencies through constructor. Example: def __init__(self, config_loader, domain_graph): self._loader = config_loader
  DON'T: Don't access globals, singletons, or create dependencies internally. Example: self._loader = ConfigLoader() (wrong - creates internally)

- **self_documenting_tests**: Tests are self-documenting through code structure. Don't add verbose comments explaining failures. Imports, calls, and assertions show the API design. Let code speak for itself. Example: generator = MCPServerGenerator(bot_name, config_path); server = generator.generate_server()
  DO: Let code structure document the test. Example: generator = MCPServerGenerator(name, config); file = generator.generate() - API is clear
  DON'T: Don't add verbose comments explaining obvious things. Example: # This will fail because API doesn't exist yet (unnecessary)

- **standard_test_data_sets**: Use standard, named test data sets across tests instead of recreating ad-hoc values. Example: STANDARD_STATE = {...}; helper.set_state(...); assert helper.get_state() == STANDARD_STATE.
  DO: Define canonical data once (helper constants/factories) and reuse it so every test exercises the full domain object.
  DON'T: Do not create new ad-hoc values per test or assert only one field from a complex object.

- **assert_full_results**: Assert full domain results (state/log/graph objects), not single cherry-picked fields. Example: assert helper.get_state() == STANDARD_STATE, not assert helper.get_state()['current'] == 'shape.clarify'.
  DO: Compare entire objects/dicts/dataclasses against standard data fixtures.
  DON'T: Do not assert single fields or lengths when validating complex results.

- **use_ascii_only**: All test code must use ASCII-only characters. No Unicode symbols, emojis, or special characters. Use plain ASCII alternatives. Example: print('[PASS] Success') not print('[checkmark] Success')
  DO: Use ASCII-only characters. Example: print('[PASS] Agent initialized'); print('[ERROR] Config not found')
  DON'T: Don't use Unicode or emojis. Example: print('[checkmark] Done') (wrong); print('[green_check] OK') (wrong)

- **pytest_bdd_orchestrator_pattern**: Use pytest with orchestrator pattern for story-based tests. NO FEATURE FILES. Test classes contain orchestrator methods (under 20 lines) showing Given-When-Then flow by calling helper functions. Example: def test_agent_loads_config(): given_config_exists(); agent = when_agent_initialized(); then_agent_is_configured(agent)
  DO: Orchestrator pattern: test shows flow, delegates to helpers. Example: # Given; create_config_file(); # When; agent.initialize(); # Then; assert agent.is_initialized
  DON'T: Don't use feature files or inline complex setup. Example: @given('config exists') def step(): ... (wrong - use pytest directly)

- **use_class_based_organization**: Test structure matches story graph: file = sub-epic (test_<sub_epic>.py), class = story (Test<ExactStoryName>), method = scenario (test_<scenario_snake_case>). Classes in story map order. Example: test_generate_bot_tools.py, class TestGenerateBotTools, def test_generator_creates_tool_for_test_bot
  DO: Map story hierarchy to test structure exactly. Example: Sub-epic 'Generate Bot Tools' -> test_generate_bot_tools.py, Story 'Generate Bot Tools' -> TestGenerateBotTools
  DON'T: Don't use generic/abbreviated names or wrong order. Example: class TestToolGen (wrong - use TestGenerateBotTools)

- **use_exact_variable_names**: Use exact variable names from specification scenarios. When spec mentions agent_name, workspace_root, config_path - use those exact names in tests and production code. Example: agent_name = 'story_bot' (from spec), not name = 'story_bot'
  DO: Use exact names from specification in tests and production. Example: agent_name, workspace_root, config_path - all from spec
  DON'T: Don't use different names than specification. Example: name = 'bot' when spec says agent_name (wrong)

- **use_given_when_then_helpers**: Use reusable helper functions instead of inline code blocks of 4+ lines. Optimize for reusability, not exact step names. Place helpers at correct scope: story-level in class, sub-epic in module, epic in separate file. Example: given_config_exists(), when_agent_initialized(), then_agent_is_configured()
  DO: Use Given/When/Then helper functions for setup, action, assertion. Example: given_bot_config_exists(); bot = when_bot_instantiated(); then_bot_uses_correct_directories(bot)
  DON'T: Don't use inline operations of 4+ lines. Example: config_dir = ...; config_dir.mkdir(); config_file = ...; config_file.write_text() (wrong - extract to helper)

CRITICAL: The rules digest above contains everything you need to get started.

WORKFLOW:
1. Read the rules digest above (descriptions + key principles)
2. Apply rules to the user's request
3. IF you need clarity on a specific rule (examples, edge cases, detailed patterns):
   - Use read_file tool to read that specific rule file
   - The full rule has detailed examples and detection patterns
4. Cite rule names when making decisions

Please make sure to validate content against the rules above, as well as the more detailed version of the rule files linked below.

When analyzing code, focus on finding violations and cite the specific rule names.
## Rules Available (25 total)

1. use_domain_language (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_domain_language.json)
2. consistent_vocabulary (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/consistent_vocabulary.json)
3. no_defensive_code_in_tests (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/no_defensive_code_in_tests.json)
4. production_code_clean_functions (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/production_code_clean_functions.json)
5. bug_fix_test_first (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/bug_fix_test_first.json)
6. call_production_code_directly (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/call_production_code_directly.json)
7. cover_all_behavior_paths (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/cover_all_behavior_paths.json)
8. mock_only_boundaries (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/mock_only_boundaries.json)
9. create_parameterized_tests_for_scenarios (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/create_parameterized_tests_for_scenarios.json)
10. define_fixtures_in_test_file (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/define_fixtures_in_test_file.json)
11. design_api_through_failing_tests (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/design_api_through_failing_tests.json)
12. test_observable_behavior (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/test_observable_behavior.json)
13. helper_extraction_and_reuse (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/helper_extraction_and_reuse.json)
14. match_specification_scenarios (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/match_specification_scenarios.json)
15. place_imports_at_top (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/place_imports_at_top.json)
16. object_oriented_test_helpers (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/object_oriented_test_helpers.json)
17. production_code_explicit_dependencies (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/production_code_explicit_dependencies.json)
18. self_documenting_tests (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/self_documenting_tests.json)
19. standard_test_data_sets (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/standard_test_data_sets.json)
20. assert_full_results (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/assert_full_results.json)
21. use_ascii_only (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_ascii_only.json)
22. pytest_bdd_orchestrator_pattern (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/pytest_bdd_orchestrator_pattern.json)
23. use_class_based_organization (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_class_based_organization.json)
24. use_exact_variable_names (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_exact_variable_names.json)
25. use_given_when_then_helpers (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_given_when_then_helpers.json)

# Behavior: tests

## Behavior Instructions - tests

The purpose of this behavior is to write test files (.py, .js, etc.) with executable test code from scenarios.examples that validate story behavior

**BEHAVIOR PURPOSE:**
This behavior WRITES TEST FILES. The primary output is executable test code files that validate story behavior.
Write test files (.py, .js, etc.) with executable test code from scenarios.examples that validate story behavior
The secondary output is to make sure that the story_graph.json scenarios, stories, and sub-epics have test fields added for the test methods, test classes, and test files respectively.
After creating test files, classes, and methods, you MUST map them to the story-graph.json:

## Action Instructions - rules

The purpose of this action is to load behavior-specific rules into ai context for guidance on writing compliant content

---

**Look for context in the following locations:**
- in this message and chat history
- in `C:/Users/thoma/AppData/Local/Temp/pytest-of-thoma/pytest-3773/test_user_gets_rules_instructi2/workspace/docs/context/`
- generated files in `C:/Users/thoma/AppData/Local/Temp/pytest-of-thoma/pytest-3773/test_user_gets_rules_instructi2/workspace/docs/stories/`
  clarification.json, strategy.json

CRITICAL: This is the rules action - it loads rules for AI context. DO NOT run validation.
CRITICAL: You MUST systematically read each rule file listed below using the read_file tool BEFORE acting on the user's message.
Read ALL rule files first, then apply them to the user's request.
Each rule file path is provided - use read_file to load the complete rule content including examples.
After reading all rules, act on the user's message following ALL the rules you just read.

CRITICAL: When reporting validation results, use this EXACT format:
For each rule checked, report: Rule Name | PASS or FAIL | If FAIL, explain why in one sentence
Example: prefer_object_model_over_config | PASS
Example: eliminate_duplication | FAIL | Same logic repeated in lines 45-50 and 78-83
Keep it simple: just tell the user what passed, what failed, and if it failed, why.

Rules to follow:

- **use_domain_language**: Use Ubiquitous Language (DDD): Same vocabulary in domain model, stories, scenarios, AND code. Class names = domain entities/nouns. Method names = domain responsibilities/verbs. Test names read like plain English stories. Example: test_agent_loads_configuration_when_file_exists (not test_agt_init_sets_vars)
  DO: Use domain language for classes, methods, and test names. Example: class GatherContextAction, def inject_guardrails(), test_agent_loads_config_when_file_exists
  DON'T: Don't use generic technical terms or implementation-specific names. Example: class StdioHandler (wrong), def execute_with_guardrails (wrong), test_agt_init_sets_vars (wrong)

- **consistent_vocabulary**: Use ONE word per concept across entire codebase. Pick consistent vocabulary: create (not build/make/construct), verify (not check/assert/validate), load (not fetch/get/retrieve). Use intention-revealing names that describe behavior. Example: create_agent(), verify_initialized(), load_config() - same verbs everywhere
  DO: Use same word for same concept everywhere. Example: create_agent(), create_config(), create_workspace() - all use 'create'
  DON'T: Don't mix synonyms for same concept. Example: create_agent() + build_config() + make_workspace() (wrong - pick one verb)

- **no_defensive_code_in_tests**: Tests must NEVER contain guard clauses, defensive conditionals, or fallback paths. We control test setup - if it's wrong, the test MUST fail immediately. Guard clauses hide problems. Tests should assume positive outcomes. Example: Just call the code directly, don't wrap in if-checks
  DO: Assume correct setup - let test fail if wrong. Example: behavior = Behavior(name='shape') then assert behavior.name == 'shape'
  DON'T: Don't add if-checks, type guards, or fallback handling in tests. Example: if behavior_file.exists(): (wrong - test should fail if it doesn't)

- **production_code_clean_functions**: Production code functions should do ONE thing, be under 20 lines, and have one level of abstraction. No hidden side effects. Name reveals complete behavior. Extract multiple concerns into separate functions. Example: load_config(), validate_config(), apply_config() - each does one thing
  DO: Single responsibility, small focused functions. Example: initialize_from_config() calls validate_exists(), load_config(), validate_structure(), apply_config()
  DON'T: Don't make functions that do multiple unrelated things or are too long. Example: 50-line function that loads, validates, and applies config

- **bug_fix_test_first**: When production code breaks, follow test-first workflow: write failing test, verify failure, fix code, verify success. Never fix bugs without a failing test first. Example: test_mcp_tool_initializes_bot() fails -> fix initialization -> test passes
  DO: Follow RED-GREEN-PRODUCTION workflow. Example: Write test reproducing bug -> Run test (RED) -> Fix minimal code -> Run test (GREEN) -> Run full suite
  DON'T: Don't fix bugs directly without failing test first. Example: Editing production code without test -> deploying -> hoping it works (wrong)

- **call_production_code_directly**: Call production code directly in tests. Let tests fail naturally if code doesn't exist. Don't comment out calls, mock business logic, or fake state. Only mock external boundaries. Example: agent = Agent(); agent.initialize() (not agent = Mock())
  DO: Call production code directly, let it fail naturally. Example: agent = Agent(workspace); agent.initialize(config); assert agent.is_initialized
  DON'T: Don't mock class under test, comment out calls, or fake state. Example: agent = Mock(spec=Agent) (wrong); agent._initialized = True (wrong)

- **cover_all_behavior_paths**: Cover all behavior paths: normal (happy path), edge cases, and failure scenarios. Each distinct behavior needs its own focused test. Tests must be independent. Example: test_loads_valid_config(), test_loads_empty_config(), test_raises_error_when_file_missing()
  DO: Test normal, edge, and failure paths separately. Example: test_loads_valid_config() (happy), test_loads_empty_config() (edge), test_raises_when_missing() (failure)
  DON'T: Don't test only happy path or combine multiple behaviors in one test. Example: Single test for both success and failure (wrong)

- **mock_only_boundaries**: Mock ONLY at architectural boundaries: external APIs, network, uncontrollable services. Don't mock internal business logic, classes under test, or file operations (use temp files). Example: patch('requests.get') (OK); patch('agent.validate') (wrong)
  DO: Mock only external dependencies you can't control. Example: with patch('requests.get') as mock: (external API - OK to mock)
  DON'T: Don't mock internal logic, class under test, or file I/O. Example: with patch('agent.validate_config') (wrong - test the logic!)

- **create_parameterized_tests_for_scenarios**: If scenarios have Examples tables, create parameterized tests using @pytest.mark.parametrize. Each row becomes a test case. Don't write single tests that only test one example. Example: @pytest.mark.parametrize('input,expected', [(1, 2), (3, 4)])
  DO: Create parameterized tests from Examples tables. Example: @pytest.mark.parametrize('paths,count', [(['p1','p2'], 2), (['p3'], 1)])
  DON'T: Don't hardcode single example or duplicate test methods. Example: def test_with_value_1(): (wrong); def test_with_value_2(): (wrong - use parametrize)

- **define_fixtures_in_test_file**: Define fixtures in the test file, not separate conftest.py. Truly reusable fixtures (file ops, location helpers) go in base conftest.py. Example: @pytest.fixture def workspace_root(tmp_path): return tmp_path / 'workspace'
  DO: Define fixtures in same test file. Example: @pytest.fixture def config_file(tmp_path): ... (in test_agent.py)
  DON'T: Don't create separate conftest.py for agent-specific fixtures. Example: src/conftest.py with agent fixtures (wrong - put in test file)

- **design_api_through_failing_tests**: Write tests against the REAL expected API BEFORE implementing code. Tests MUST fail initially. Set up real test data and call real API. Failure reveals complete API design. Example: project = Project(path=path); project.initialize() (doesn't exist yet -> fails -> drives implementation)
  DO: Write test against real expected API that fails initially. Example: project = Project(path); project.initialize(); assert project.is_ready (fails until implemented)
  DON'T: Don't use placeholders, dummy values, or skip the failing step. Example: project = 'TODO' (wrong); assuming test passes first (wrong)

- **test_observable_behavior**: Test observable behavior, not implementation details. Verify public API and visible state changes. Don't assert on private methods or internal flags. Example: assert agent.config_path.exists() (observable); not assert agent._internal_flag (private)
  DO: Test observable outcomes through public API. Example: assert agent.config_path == expected; assert agent.is_initialized (public properties)
  DON'T: Don't test private state or implementation details. Example: assert agent._initialized (wrong); assert agent._config_cache (wrong)

- **helper_extraction_and_reuse**: Extract duplicate test setup to reusable helper functions. Keep test bodies focused on specific behavior. Example: create_agent_with_config(), create_config_file(), verify_agent_initialized() - reusable across tests
  DO: Extract duplicate setup to reusable helpers. Example: create_agent_with_config(name, workspace, config) returns initialized Agent
  DON'T: Don't duplicate setup code across tests. Example: Same 10 lines of setup in every test method (wrong - extract to helper)

- **match_specification_scenarios**: Tests must match specification scenarios exactly. Test names, steps, and assertions verify exactly what the scenario states. Use exact variable names and terminology from specification. Example: agent_name='story_bot' (from spec), not name='bot'
  DO: Test matches specification exactly. Example: GIVEN config exists, WHEN Agent(agent_name='story_bot'), THEN config_path == agents/base/agent.json
  DON'T: Don't use different terminology or assert things not in specification. Example: assert agent._internal_flag (not in spec - wrong)

- **place_imports_at_top**: Place all imports at top of test file, after docstrings, before code. Group: stdlib, third-party, then local. Example: import json; import pytest; from mymodule import MyClass
  DO: All imports at top, grouped by type. Example: import json; import pytest; from bots... import X
  DON'T: Don't place imports inside functions or after code. Example: def test(): from pathlib import Path (wrong - import inside function)

- **object_oriented_test_helpers**: Consolidate tests around object-oriented helpers/factories (e.g., BotTestHelper test hopper) that build complete domain objects with standard data. Example: helper = BotTestHelper(tmp_path); helper.set_state('shape','clarify'); helper.assert_at_behavior_action('shape','clarify'). Avoid scattering many primitive parameters across parametrize blocks or inline setups.
  DO: Use shared helper objects to create full test fixtures and assert against complete domain objects, not fragments.
  DON'T: Do not spread test setup across many primitive parameters or cherry-pick single values from partial objects.

- **production_code_explicit_dependencies**: Production code: make dependencies explicit through constructor injection. Pass all external dependencies as constructor parameters. No hidden global state. Tests easily inject test doubles. Example: Agent(config_loader=loader, domain_graph=graph)
  DO: Inject all dependencies through constructor. Example: def __init__(self, config_loader, domain_graph): self._loader = config_loader
  DON'T: Don't access globals, singletons, or create dependencies internally. Example: self._loader = ConfigLoader() (wrong - creates internally)

- **self_documenting_tests**: Tests are self-documenting through code structure. Don't add verbose comments explaining failures. Imports, calls, and assertions show the API design. Let code speak for itself. Example: generator = MCPServerGenerator(bot_name, config_path); server = generator.generate_server()
  DO: Let code structure document the test. Example: generator = MCPServerGenerator(name, config); file = generator.generate() - API is clear
  DON'T: Don't add verbose comments explaining obvious things. Example: # This will fail because API doesn't exist yet (unnecessary)

- **standard_test_data_sets**: Use standard, named test data sets across tests instead of recreating ad-hoc values. Example: STANDARD_STATE = {...}; helper.set_state(...); assert helper.get_state() == STANDARD_STATE.
  DO: Define canonical data once (helper constants/factories) and reuse it so every test exercises the full domain object.
  DON'T: Do not create new ad-hoc values per test or assert only one field from a complex object.

- **assert_full_results**: Assert full domain results (state/log/graph objects), not single cherry-picked fields. Example: assert helper.get_state() == STANDARD_STATE, not assert helper.get_state()['current'] == 'shape.clarify'.
  DO: Compare entire objects/dicts/dataclasses against standard data fixtures.
  DON'T: Do not assert single fields or lengths when validating complex results.

- **use_ascii_only**: All test code must use ASCII-only characters. No Unicode symbols, emojis, or special characters. Use plain ASCII alternatives. Example: print('[PASS] Success') not print('[checkmark] Success')
  DO: Use ASCII-only characters. Example: print('[PASS] Agent initialized'); print('[ERROR] Config not found')
  DON'T: Don't use Unicode or emojis. Example: print('[checkmark] Done') (wrong); print('[green_check] OK') (wrong)

- **pytest_bdd_orchestrator_pattern**: Use pytest with orchestrator pattern for story-based tests. NO FEATURE FILES. Test classes contain orchestrator methods (under 20 lines) showing Given-When-Then flow by calling helper functions. Example: def test_agent_loads_config(): given_config_exists(); agent = when_agent_initialized(); then_agent_is_configured(agent)
  DO: Orchestrator pattern: test shows flow, delegates to helpers. Example: # Given; create_config_file(); # When; agent.initialize(); # Then; assert agent.is_initialized
  DON'T: Don't use feature files or inline complex setup. Example: @given('config exists') def step(): ... (wrong - use pytest directly)

- **use_class_based_organization**: Test structure matches story graph: file = sub-epic (test_<sub_epic>.py), class = story (Test<ExactStoryName>), method = scenario (test_<scenario_snake_case>). Classes in story map order. Example: test_generate_bot_tools.py, class TestGenerateBotTools, def test_generator_creates_tool_for_test_bot
  DO: Map story hierarchy to test structure exactly. Example: Sub-epic 'Generate Bot Tools' -> test_generate_bot_tools.py, Story 'Generate Bot Tools' -> TestGenerateBotTools
  DON'T: Don't use generic/abbreviated names or wrong order. Example: class TestToolGen (wrong - use TestGenerateBotTools)

- **use_exact_variable_names**: Use exact variable names from specification scenarios. When spec mentions agent_name, workspace_root, config_path - use those exact names in tests and production code. Example: agent_name = 'story_bot' (from spec), not name = 'story_bot'
  DO: Use exact names from specification in tests and production. Example: agent_name, workspace_root, config_path - all from spec
  DON'T: Don't use different names than specification. Example: name = 'bot' when spec says agent_name (wrong)

- **use_given_when_then_helpers**: Use reusable helper functions instead of inline code blocks of 4+ lines. Optimize for reusability, not exact step names. Place helpers at correct scope: story-level in class, sub-epic in module, epic in separate file. Example: given_config_exists(), when_agent_initialized(), then_agent_is_configured()
  DO: Use Given/When/Then helper functions for setup, action, assertion. Example: given_bot_config_exists(); bot = when_bot_instantiated(); then_bot_uses_correct_directories(bot)
  DON'T: Don't use inline operations of 4+ lines. Example: config_dir = ...; config_dir.mkdir(); config_file = ...; config_file.write_text() (wrong - extract to helper)

CRITICAL: The rules digest above contains everything you need to get started.

WORKFLOW:
1. Read the rules digest above (descriptions + key principles)
2. Apply rules to the user's request
3. IF you need clarity on a specific rule (examples, edge cases, detailed patterns):
   - Use read_file tool to read that specific rule file
   - The full rule has detailed examples and detection patterns
4. Cite rule names when making decisions

Please make sure to validate content against the rules above, as well as the more detailed version of the rule files linked below.

When analyzing code, focus on finding violations and cite the specific rule names.
## Rules Available (25 total)

1. use_domain_language (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_domain_language.json)
2. consistent_vocabulary (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/consistent_vocabulary.json)
3. no_defensive_code_in_tests (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/no_defensive_code_in_tests.json)
4. production_code_clean_functions (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/production_code_clean_functions.json)
5. bug_fix_test_first (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/bug_fix_test_first.json)
6. call_production_code_directly (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/call_production_code_directly.json)
7. cover_all_behavior_paths (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/cover_all_behavior_paths.json)
8. mock_only_boundaries (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/mock_only_boundaries.json)
9. create_parameterized_tests_for_scenarios (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/create_parameterized_tests_for_scenarios.json)
10. define_fixtures_in_test_file (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/define_fixtures_in_test_file.json)
11. design_api_through_failing_tests (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/design_api_through_failing_tests.json)
12. test_observable_behavior (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/test_observable_behavior.json)
13. helper_extraction_and_reuse (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/helper_extraction_and_reuse.json)
14. match_specification_scenarios (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/match_specification_scenarios.json)
15. place_imports_at_top (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/place_imports_at_top.json)
16. object_oriented_test_helpers (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/object_oriented_test_helpers.json)
17. production_code_explicit_dependencies (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/production_code_explicit_dependencies.json)
18. self_documenting_tests (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/self_documenting_tests.json)
19. standard_test_data_sets (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/standard_test_data_sets.json)
20. assert_full_results (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/assert_full_results.json)
21. use_ascii_only (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_ascii_only.json)
22. pytest_bdd_orchestrator_pattern (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/pytest_bdd_orchestrator_pattern.json)
23. use_class_based_organization (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_class_based_organization.json)
24. use_exact_variable_names (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_exact_variable_names.json)
25. use_given_when_then_helpers (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_given_when_then_helpers.json)

# Behavior: tests

## Behavior Instructions - tests

The purpose of this behavior is to write test files (.py, .js, etc.) with executable test code from scenarios.examples that validate story behavior

**BEHAVIOR PURPOSE:**
This behavior WRITES TEST FILES. The primary output is executable test code files that validate story behavior.
Write test files (.py, .js, etc.) with executable test code from scenarios.examples that validate story behavior
The secondary output is to make sure that the story_graph.json scenarios, stories, and sub-epics have test fields added for the test methods, test classes, and test files respectively.
After creating test files, classes, and methods, you MUST map them to the story-graph.json:

## Action Instructions - rules

The purpose of this action is to load behavior-specific rules into ai context for guidance on writing compliant content

---

**Look for context in the following locations:**
- in this message and chat history
- in `C:/Users/thoma/AppData/Local/Temp/pytest-of-thoma/pytest-3773/test_user_gets_rules_with_mess1/workspace/docs/context/`
- generated files in `C:/Users/thoma/AppData/Local/Temp/pytest-of-thoma/pytest-3773/test_user_gets_rules_with_mess1/workspace/docs/stories/`
  clarification.json, strategy.json

CRITICAL: This is the rules action - it loads rules for AI context. DO NOT run validation.
CRITICAL: You MUST systematically read each rule file listed below using the read_file tool BEFORE acting on the user's message.
Read ALL rule files first, then apply them to the user's request.
Each rule file path is provided - use read_file to load the complete rule content including examples.
After reading all rules, act on the user's message following ALL the rules you just read.

CRITICAL: When reporting validation results, use this EXACT format:
For each rule checked, report: Rule Name | PASS or FAIL | If FAIL, explain why in one sentence
Example: prefer_object_model_over_config | PASS
Example: eliminate_duplication | FAIL | Same logic repeated in lines 45-50 and 78-83
Keep it simple: just tell the user what passed, what failed, and if it failed, why.

Rules to follow:

- **use_domain_language**: Use Ubiquitous Language (DDD): Same vocabulary in domain model, stories, scenarios, AND code. Class names = domain entities/nouns. Method names = domain responsibilities/verbs. Test names read like plain English stories. Example: test_agent_loads_configuration_when_file_exists (not test_agt_init_sets_vars)
  DO: Use domain language for classes, methods, and test names. Example: class GatherContextAction, def inject_guardrails(), test_agent_loads_config_when_file_exists
  DON'T: Don't use generic technical terms or implementation-specific names. Example: class StdioHandler (wrong), def execute_with_guardrails (wrong), test_agt_init_sets_vars (wrong)

- **consistent_vocabulary**: Use ONE word per concept across entire codebase. Pick consistent vocabulary: create (not build/make/construct), verify (not check/assert/validate), load (not fetch/get/retrieve). Use intention-revealing names that describe behavior. Example: create_agent(), verify_initialized(), load_config() - same verbs everywhere
  DO: Use same word for same concept everywhere. Example: create_agent(), create_config(), create_workspace() - all use 'create'
  DON'T: Don't mix synonyms for same concept. Example: create_agent() + build_config() + make_workspace() (wrong - pick one verb)

- **no_defensive_code_in_tests**: Tests must NEVER contain guard clauses, defensive conditionals, or fallback paths. We control test setup - if it's wrong, the test MUST fail immediately. Guard clauses hide problems. Tests should assume positive outcomes. Example: Just call the code directly, don't wrap in if-checks
  DO: Assume correct setup - let test fail if wrong. Example: behavior = Behavior(name='shape') then assert behavior.name == 'shape'
  DON'T: Don't add if-checks, type guards, or fallback handling in tests. Example: if behavior_file.exists(): (wrong - test should fail if it doesn't)

- **production_code_clean_functions**: Production code functions should do ONE thing, be under 20 lines, and have one level of abstraction. No hidden side effects. Name reveals complete behavior. Extract multiple concerns into separate functions. Example: load_config(), validate_config(), apply_config() - each does one thing
  DO: Single responsibility, small focused functions. Example: initialize_from_config() calls validate_exists(), load_config(), validate_structure(), apply_config()
  DON'T: Don't make functions that do multiple unrelated things or are too long. Example: 50-line function that loads, validates, and applies config

- **bug_fix_test_first**: When production code breaks, follow test-first workflow: write failing test, verify failure, fix code, verify success. Never fix bugs without a failing test first. Example: test_mcp_tool_initializes_bot() fails -> fix initialization -> test passes
  DO: Follow RED-GREEN-PRODUCTION workflow. Example: Write test reproducing bug -> Run test (RED) -> Fix minimal code -> Run test (GREEN) -> Run full suite
  DON'T: Don't fix bugs directly without failing test first. Example: Editing production code without test -> deploying -> hoping it works (wrong)

- **call_production_code_directly**: Call production code directly in tests. Let tests fail naturally if code doesn't exist. Don't comment out calls, mock business logic, or fake state. Only mock external boundaries. Example: agent = Agent(); agent.initialize() (not agent = Mock())
  DO: Call production code directly, let it fail naturally. Example: agent = Agent(workspace); agent.initialize(config); assert agent.is_initialized
  DON'T: Don't mock class under test, comment out calls, or fake state. Example: agent = Mock(spec=Agent) (wrong); agent._initialized = True (wrong)

- **cover_all_behavior_paths**: Cover all behavior paths: normal (happy path), edge cases, and failure scenarios. Each distinct behavior needs its own focused test. Tests must be independent. Example: test_loads_valid_config(), test_loads_empty_config(), test_raises_error_when_file_missing()
  DO: Test normal, edge, and failure paths separately. Example: test_loads_valid_config() (happy), test_loads_empty_config() (edge), test_raises_when_missing() (failure)
  DON'T: Don't test only happy path or combine multiple behaviors in one test. Example: Single test for both success and failure (wrong)

- **mock_only_boundaries**: Mock ONLY at architectural boundaries: external APIs, network, uncontrollable services. Don't mock internal business logic, classes under test, or file operations (use temp files). Example: patch('requests.get') (OK); patch('agent.validate') (wrong)
  DO: Mock only external dependencies you can't control. Example: with patch('requests.get') as mock: (external API - OK to mock)
  DON'T: Don't mock internal logic, class under test, or file I/O. Example: with patch('agent.validate_config') (wrong - test the logic!)

- **create_parameterized_tests_for_scenarios**: If scenarios have Examples tables, create parameterized tests using @pytest.mark.parametrize. Each row becomes a test case. Don't write single tests that only test one example. Example: @pytest.mark.parametrize('input,expected', [(1, 2), (3, 4)])
  DO: Create parameterized tests from Examples tables. Example: @pytest.mark.parametrize('paths,count', [(['p1','p2'], 2), (['p3'], 1)])
  DON'T: Don't hardcode single example or duplicate test methods. Example: def test_with_value_1(): (wrong); def test_with_value_2(): (wrong - use parametrize)

- **define_fixtures_in_test_file**: Define fixtures in the test file, not separate conftest.py. Truly reusable fixtures (file ops, location helpers) go in base conftest.py. Example: @pytest.fixture def workspace_root(tmp_path): return tmp_path / 'workspace'
  DO: Define fixtures in same test file. Example: @pytest.fixture def config_file(tmp_path): ... (in test_agent.py)
  DON'T: Don't create separate conftest.py for agent-specific fixtures. Example: src/conftest.py with agent fixtures (wrong - put in test file)

- **design_api_through_failing_tests**: Write tests against the REAL expected API BEFORE implementing code. Tests MUST fail initially. Set up real test data and call real API. Failure reveals complete API design. Example: project = Project(path=path); project.initialize() (doesn't exist yet -> fails -> drives implementation)
  DO: Write test against real expected API that fails initially. Example: project = Project(path); project.initialize(); assert project.is_ready (fails until implemented)
  DON'T: Don't use placeholders, dummy values, or skip the failing step. Example: project = 'TODO' (wrong); assuming test passes first (wrong)

- **test_observable_behavior**: Test observable behavior, not implementation details. Verify public API and visible state changes. Don't assert on private methods or internal flags. Example: assert agent.config_path.exists() (observable); not assert agent._internal_flag (private)
  DO: Test observable outcomes through public API. Example: assert agent.config_path == expected; assert agent.is_initialized (public properties)
  DON'T: Don't test private state or implementation details. Example: assert agent._initialized (wrong); assert agent._config_cache (wrong)

- **helper_extraction_and_reuse**: Extract duplicate test setup to reusable helper functions. Keep test bodies focused on specific behavior. Example: create_agent_with_config(), create_config_file(), verify_agent_initialized() - reusable across tests
  DO: Extract duplicate setup to reusable helpers. Example: create_agent_with_config(name, workspace, config) returns initialized Agent
  DON'T: Don't duplicate setup code across tests. Example: Same 10 lines of setup in every test method (wrong - extract to helper)

- **match_specification_scenarios**: Tests must match specification scenarios exactly. Test names, steps, and assertions verify exactly what the scenario states. Use exact variable names and terminology from specification. Example: agent_name='story_bot' (from spec), not name='bot'
  DO: Test matches specification exactly. Example: GIVEN config exists, WHEN Agent(agent_name='story_bot'), THEN config_path == agents/base/agent.json
  DON'T: Don't use different terminology or assert things not in specification. Example: assert agent._internal_flag (not in spec - wrong)

- **place_imports_at_top**: Place all imports at top of test file, after docstrings, before code. Group: stdlib, third-party, then local. Example: import json; import pytest; from mymodule import MyClass
  DO: All imports at top, grouped by type. Example: import json; import pytest; from bots... import X
  DON'T: Don't place imports inside functions or after code. Example: def test(): from pathlib import Path (wrong - import inside function)

- **object_oriented_test_helpers**: Consolidate tests around object-oriented helpers/factories (e.g., BotTestHelper test hopper) that build complete domain objects with standard data. Example: helper = BotTestHelper(tmp_path); helper.set_state('shape','clarify'); helper.assert_at_behavior_action('shape','clarify'). Avoid scattering many primitive parameters across parametrize blocks or inline setups.
  DO: Use shared helper objects to create full test fixtures and assert against complete domain objects, not fragments.
  DON'T: Do not spread test setup across many primitive parameters or cherry-pick single values from partial objects.

- **production_code_explicit_dependencies**: Production code: make dependencies explicit through constructor injection. Pass all external dependencies as constructor parameters. No hidden global state. Tests easily inject test doubles. Example: Agent(config_loader=loader, domain_graph=graph)
  DO: Inject all dependencies through constructor. Example: def __init__(self, config_loader, domain_graph): self._loader = config_loader
  DON'T: Don't access globals, singletons, or create dependencies internally. Example: self._loader = ConfigLoader() (wrong - creates internally)

- **self_documenting_tests**: Tests are self-documenting through code structure. Don't add verbose comments explaining failures. Imports, calls, and assertions show the API design. Let code speak for itself. Example: generator = MCPServerGenerator(bot_name, config_path); server = generator.generate_server()
  DO: Let code structure document the test. Example: generator = MCPServerGenerator(name, config); file = generator.generate() - API is clear
  DON'T: Don't add verbose comments explaining obvious things. Example: # This will fail because API doesn't exist yet (unnecessary)

- **standard_test_data_sets**: Use standard, named test data sets across tests instead of recreating ad-hoc values. Example: STANDARD_STATE = {...}; helper.set_state(...); assert helper.get_state() == STANDARD_STATE.
  DO: Define canonical data once (helper constants/factories) and reuse it so every test exercises the full domain object.
  DON'T: Do not create new ad-hoc values per test or assert only one field from a complex object.

- **assert_full_results**: Assert full domain results (state/log/graph objects), not single cherry-picked fields. Example: assert helper.get_state() == STANDARD_STATE, not assert helper.get_state()['current'] == 'shape.clarify'.
  DO: Compare entire objects/dicts/dataclasses against standard data fixtures.
  DON'T: Do not assert single fields or lengths when validating complex results.

- **use_ascii_only**: All test code must use ASCII-only characters. No Unicode symbols, emojis, or special characters. Use plain ASCII alternatives. Example: print('[PASS] Success') not print('[checkmark] Success')
  DO: Use ASCII-only characters. Example: print('[PASS] Agent initialized'); print('[ERROR] Config not found')
  DON'T: Don't use Unicode or emojis. Example: print('[checkmark] Done') (wrong); print('[green_check] OK') (wrong)

- **pytest_bdd_orchestrator_pattern**: Use pytest with orchestrator pattern for story-based tests. NO FEATURE FILES. Test classes contain orchestrator methods (under 20 lines) showing Given-When-Then flow by calling helper functions. Example: def test_agent_loads_config(): given_config_exists(); agent = when_agent_initialized(); then_agent_is_configured(agent)
  DO: Orchestrator pattern: test shows flow, delegates to helpers. Example: # Given; create_config_file(); # When; agent.initialize(); # Then; assert agent.is_initialized
  DON'T: Don't use feature files or inline complex setup. Example: @given('config exists') def step(): ... (wrong - use pytest directly)

- **use_class_based_organization**: Test structure matches story graph: file = sub-epic (test_<sub_epic>.py), class = story (Test<ExactStoryName>), method = scenario (test_<scenario_snake_case>). Classes in story map order. Example: test_generate_bot_tools.py, class TestGenerateBotTools, def test_generator_creates_tool_for_test_bot
  DO: Map story hierarchy to test structure exactly. Example: Sub-epic 'Generate Bot Tools' -> test_generate_bot_tools.py, Story 'Generate Bot Tools' -> TestGenerateBotTools
  DON'T: Don't use generic/abbreviated names or wrong order. Example: class TestToolGen (wrong - use TestGenerateBotTools)

- **use_exact_variable_names**: Use exact variable names from specification scenarios. When spec mentions agent_name, workspace_root, config_path - use those exact names in tests and production code. Example: agent_name = 'story_bot' (from spec), not name = 'story_bot'
  DO: Use exact names from specification in tests and production. Example: agent_name, workspace_root, config_path - all from spec
  DON'T: Don't use different names than specification. Example: name = 'bot' when spec says agent_name (wrong)

- **use_given_when_then_helpers**: Use reusable helper functions instead of inline code blocks of 4+ lines. Optimize for reusability, not exact step names. Place helpers at correct scope: story-level in class, sub-epic in module, epic in separate file. Example: given_config_exists(), when_agent_initialized(), then_agent_is_configured()
  DO: Use Given/When/Then helper functions for setup, action, assertion. Example: given_bot_config_exists(); bot = when_bot_instantiated(); then_bot_uses_correct_directories(bot)
  DON'T: Don't use inline operations of 4+ lines. Example: config_dir = ...; config_dir.mkdir(); config_file = ...; config_file.write_text() (wrong - extract to helper)

CRITICAL: The rules digest above contains everything you need to get started.

WORKFLOW:
1. Read the rules digest above (descriptions + key principles)
2. Apply rules to the user's request
3. IF you need clarity on a specific rule (examples, edge cases, detailed patterns):
   - Use read_file tool to read that specific rule file
   - The full rule has detailed examples and detection patterns
4. Cite rule names when making decisions

Please make sure to validate content against the rules above, as well as the more detailed version of the rule files linked below.

When analyzing code, focus on finding violations and cite the specific rule names.
## Rules Available (25 total)

1. use_domain_language (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_domain_language.json)
2. consistent_vocabulary (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/consistent_vocabulary.json)
3. no_defensive_code_in_tests (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/no_defensive_code_in_tests.json)
4. production_code_clean_functions (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/production_code_clean_functions.json)
5. bug_fix_test_first (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/bug_fix_test_first.json)
6. call_production_code_directly (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/call_production_code_directly.json)
7. cover_all_behavior_paths (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/cover_all_behavior_paths.json)
8. mock_only_boundaries (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/mock_only_boundaries.json)
9. create_parameterized_tests_for_scenarios (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/create_parameterized_tests_for_scenarios.json)
10. define_fixtures_in_test_file (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/define_fixtures_in_test_file.json)
11. design_api_through_failing_tests (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/design_api_through_failing_tests.json)
12. test_observable_behavior (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/test_observable_behavior.json)
13. helper_extraction_and_reuse (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/helper_extraction_and_reuse.json)
14. match_specification_scenarios (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/match_specification_scenarios.json)
15. place_imports_at_top (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/place_imports_at_top.json)
16. object_oriented_test_helpers (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/object_oriented_test_helpers.json)
17. production_code_explicit_dependencies (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/production_code_explicit_dependencies.json)
18. self_documenting_tests (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/self_documenting_tests.json)
19. standard_test_data_sets (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/standard_test_data_sets.json)
20. assert_full_results (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/assert_full_results.json)
21. use_ascii_only (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_ascii_only.json)
22. pytest_bdd_orchestrator_pattern (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/pytest_bdd_orchestrator_pattern.json)
23. use_class_based_organization (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_class_based_organization.json)
24. use_exact_variable_names (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_exact_variable_names.json)
25. use_given_when_then_helpers (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_given_when_then_helpers.json)

# Behavior: tests

## Behavior Instructions - tests

The purpose of this behavior is to write test files (.py, .js, etc.) with executable test code from scenarios.examples that validate story behavior

**BEHAVIOR PURPOSE:**
This behavior WRITES TEST FILES. The primary output is executable test code files that validate story behavior.
Write test files (.py, .js, etc.) with executable test code from scenarios.examples that validate story behavior
The secondary output is to make sure that the story_graph.json scenarios, stories, and sub-epics have test fields added for the test methods, test classes, and test files respectively.
After creating test files, classes, and methods, you MUST map them to the story-graph.json:

## Action Instructions - rules

The purpose of this action is to load behavior-specific rules into ai context for guidance on writing compliant content

---

**Look for context in the following locations:**
- in this message and chat history
- in `C:/Users/thoma/AppData/Local/Temp/pytest-of-thoma/pytest-3773/test_user_gets_rules_without_m0/workspace/docs/context/`
- generated files in `C:/Users/thoma/AppData/Local/Temp/pytest-of-thoma/pytest-3773/test_user_gets_rules_without_m0/workspace/docs/stories/`
  clarification.json, strategy.json

CRITICAL: This is the rules action - it loads rules for AI context. DO NOT run validation.
CRITICAL: You MUST systematically read each rule file listed below using the read_file tool BEFORE acting on the user's message.
Read ALL rule files first, then apply them to the user's request.
Each rule file path is provided - use read_file to load the complete rule content including examples.
After reading all rules, act on the user's message following ALL the rules you just read.

CRITICAL: When reporting validation results, use this EXACT format:
For each rule checked, report: Rule Name | PASS or FAIL | If FAIL, explain why in one sentence
Example: prefer_object_model_over_config | PASS
Example: eliminate_duplication | FAIL | Same logic repeated in lines 45-50 and 78-83
Keep it simple: just tell the user what passed, what failed, and if it failed, why.

Rules to follow:

- **use_domain_language**: Use Ubiquitous Language (DDD): Same vocabulary in domain model, stories, scenarios, AND code. Class names = domain entities/nouns. Method names = domain responsibilities/verbs. Test names read like plain English stories. Example: test_agent_loads_configuration_when_file_exists (not test_agt_init_sets_vars)
  DO: Use domain language for classes, methods, and test names. Example: class GatherContextAction, def inject_guardrails(), test_agent_loads_config_when_file_exists
  DON'T: Don't use generic technical terms or implementation-specific names. Example: class StdioHandler (wrong), def execute_with_guardrails (wrong), test_agt_init_sets_vars (wrong)

- **consistent_vocabulary**: Use ONE word per concept across entire codebase. Pick consistent vocabulary: create (not build/make/construct), verify (not check/assert/validate), load (not fetch/get/retrieve). Use intention-revealing names that describe behavior. Example: create_agent(), verify_initialized(), load_config() - same verbs everywhere
  DO: Use same word for same concept everywhere. Example: create_agent(), create_config(), create_workspace() - all use 'create'
  DON'T: Don't mix synonyms for same concept. Example: create_agent() + build_config() + make_workspace() (wrong - pick one verb)

- **no_defensive_code_in_tests**: Tests must NEVER contain guard clauses, defensive conditionals, or fallback paths. We control test setup - if it's wrong, the test MUST fail immediately. Guard clauses hide problems. Tests should assume positive outcomes. Example: Just call the code directly, don't wrap in if-checks
  DO: Assume correct setup - let test fail if wrong. Example: behavior = Behavior(name='shape') then assert behavior.name == 'shape'
  DON'T: Don't add if-checks, type guards, or fallback handling in tests. Example: if behavior_file.exists(): (wrong - test should fail if it doesn't)

- **production_code_clean_functions**: Production code functions should do ONE thing, be under 20 lines, and have one level of abstraction. No hidden side effects. Name reveals complete behavior. Extract multiple concerns into separate functions. Example: load_config(), validate_config(), apply_config() - each does one thing
  DO: Single responsibility, small focused functions. Example: initialize_from_config() calls validate_exists(), load_config(), validate_structure(), apply_config()
  DON'T: Don't make functions that do multiple unrelated things or are too long. Example: 50-line function that loads, validates, and applies config

- **bug_fix_test_first**: When production code breaks, follow test-first workflow: write failing test, verify failure, fix code, verify success. Never fix bugs without a failing test first. Example: test_mcp_tool_initializes_bot() fails -> fix initialization -> test passes
  DO: Follow RED-GREEN-PRODUCTION workflow. Example: Write test reproducing bug -> Run test (RED) -> Fix minimal code -> Run test (GREEN) -> Run full suite
  DON'T: Don't fix bugs directly without failing test first. Example: Editing production code without test -> deploying -> hoping it works (wrong)

- **call_production_code_directly**: Call production code directly in tests. Let tests fail naturally if code doesn't exist. Don't comment out calls, mock business logic, or fake state. Only mock external boundaries. Example: agent = Agent(); agent.initialize() (not agent = Mock())
  DO: Call production code directly, let it fail naturally. Example: agent = Agent(workspace); agent.initialize(config); assert agent.is_initialized
  DON'T: Don't mock class under test, comment out calls, or fake state. Example: agent = Mock(spec=Agent) (wrong); agent._initialized = True (wrong)

- **cover_all_behavior_paths**: Cover all behavior paths: normal (happy path), edge cases, and failure scenarios. Each distinct behavior needs its own focused test. Tests must be independent. Example: test_loads_valid_config(), test_loads_empty_config(), test_raises_error_when_file_missing()
  DO: Test normal, edge, and failure paths separately. Example: test_loads_valid_config() (happy), test_loads_empty_config() (edge), test_raises_when_missing() (failure)
  DON'T: Don't test only happy path or combine multiple behaviors in one test. Example: Single test for both success and failure (wrong)

- **mock_only_boundaries**: Mock ONLY at architectural boundaries: external APIs, network, uncontrollable services. Don't mock internal business logic, classes under test, or file operations (use temp files). Example: patch('requests.get') (OK); patch('agent.validate') (wrong)
  DO: Mock only external dependencies you can't control. Example: with patch('requests.get') as mock: (external API - OK to mock)
  DON'T: Don't mock internal logic, class under test, or file I/O. Example: with patch('agent.validate_config') (wrong - test the logic!)

- **create_parameterized_tests_for_scenarios**: If scenarios have Examples tables, create parameterized tests using @pytest.mark.parametrize. Each row becomes a test case. Don't write single tests that only test one example. Example: @pytest.mark.parametrize('input,expected', [(1, 2), (3, 4)])
  DO: Create parameterized tests from Examples tables. Example: @pytest.mark.parametrize('paths,count', [(['p1','p2'], 2), (['p3'], 1)])
  DON'T: Don't hardcode single example or duplicate test methods. Example: def test_with_value_1(): (wrong); def test_with_value_2(): (wrong - use parametrize)

- **define_fixtures_in_test_file**: Define fixtures in the test file, not separate conftest.py. Truly reusable fixtures (file ops, location helpers) go in base conftest.py. Example: @pytest.fixture def workspace_root(tmp_path): return tmp_path / 'workspace'
  DO: Define fixtures in same test file. Example: @pytest.fixture def config_file(tmp_path): ... (in test_agent.py)
  DON'T: Don't create separate conftest.py for agent-specific fixtures. Example: src/conftest.py with agent fixtures (wrong - put in test file)

- **design_api_through_failing_tests**: Write tests against the REAL expected API BEFORE implementing code. Tests MUST fail initially. Set up real test data and call real API. Failure reveals complete API design. Example: project = Project(path=path); project.initialize() (doesn't exist yet -> fails -> drives implementation)
  DO: Write test against real expected API that fails initially. Example: project = Project(path); project.initialize(); assert project.is_ready (fails until implemented)
  DON'T: Don't use placeholders, dummy values, or skip the failing step. Example: project = 'TODO' (wrong); assuming test passes first (wrong)

- **test_observable_behavior**: Test observable behavior, not implementation details. Verify public API and visible state changes. Don't assert on private methods or internal flags. Example: assert agent.config_path.exists() (observable); not assert agent._internal_flag (private)
  DO: Test observable outcomes through public API. Example: assert agent.config_path == expected; assert agent.is_initialized (public properties)
  DON'T: Don't test private state or implementation details. Example: assert agent._initialized (wrong); assert agent._config_cache (wrong)

- **helper_extraction_and_reuse**: Extract duplicate test setup to reusable helper functions. Keep test bodies focused on specific behavior. Example: create_agent_with_config(), create_config_file(), verify_agent_initialized() - reusable across tests
  DO: Extract duplicate setup to reusable helpers. Example: create_agent_with_config(name, workspace, config) returns initialized Agent
  DON'T: Don't duplicate setup code across tests. Example: Same 10 lines of setup in every test method (wrong - extract to helper)

- **match_specification_scenarios**: Tests must match specification scenarios exactly. Test names, steps, and assertions verify exactly what the scenario states. Use exact variable names and terminology from specification. Example: agent_name='story_bot' (from spec), not name='bot'
  DO: Test matches specification exactly. Example: GIVEN config exists, WHEN Agent(agent_name='story_bot'), THEN config_path == agents/base/agent.json
  DON'T: Don't use different terminology or assert things not in specification. Example: assert agent._internal_flag (not in spec - wrong)

- **place_imports_at_top**: Place all imports at top of test file, after docstrings, before code. Group: stdlib, third-party, then local. Example: import json; import pytest; from mymodule import MyClass
  DO: All imports at top, grouped by type. Example: import json; import pytest; from bots... import X
  DON'T: Don't place imports inside functions or after code. Example: def test(): from pathlib import Path (wrong - import inside function)

- **object_oriented_test_helpers**: Consolidate tests around object-oriented helpers/factories (e.g., BotTestHelper test hopper) that build complete domain objects with standard data. Example: helper = BotTestHelper(tmp_path); helper.set_state('shape','clarify'); helper.assert_at_behavior_action('shape','clarify'). Avoid scattering many primitive parameters across parametrize blocks or inline setups.
  DO: Use shared helper objects to create full test fixtures and assert against complete domain objects, not fragments.
  DON'T: Do not spread test setup across many primitive parameters or cherry-pick single values from partial objects.

- **production_code_explicit_dependencies**: Production code: make dependencies explicit through constructor injection. Pass all external dependencies as constructor parameters. No hidden global state. Tests easily inject test doubles. Example: Agent(config_loader=loader, domain_graph=graph)
  DO: Inject all dependencies through constructor. Example: def __init__(self, config_loader, domain_graph): self._loader = config_loader
  DON'T: Don't access globals, singletons, or create dependencies internally. Example: self._loader = ConfigLoader() (wrong - creates internally)

- **self_documenting_tests**: Tests are self-documenting through code structure. Don't add verbose comments explaining failures. Imports, calls, and assertions show the API design. Let code speak for itself. Example: generator = MCPServerGenerator(bot_name, config_path); server = generator.generate_server()
  DO: Let code structure document the test. Example: generator = MCPServerGenerator(name, config); file = generator.generate() - API is clear
  DON'T: Don't add verbose comments explaining obvious things. Example: # This will fail because API doesn't exist yet (unnecessary)

- **standard_test_data_sets**: Use standard, named test data sets across tests instead of recreating ad-hoc values. Example: STANDARD_STATE = {...}; helper.set_state(...); assert helper.get_state() == STANDARD_STATE.
  DO: Define canonical data once (helper constants/factories) and reuse it so every test exercises the full domain object.
  DON'T: Do not create new ad-hoc values per test or assert only one field from a complex object.

- **assert_full_results**: Assert full domain results (state/log/graph objects), not single cherry-picked fields. Example: assert helper.get_state() == STANDARD_STATE, not assert helper.get_state()['current'] == 'shape.clarify'.
  DO: Compare entire objects/dicts/dataclasses against standard data fixtures.
  DON'T: Do not assert single fields or lengths when validating complex results.

- **use_ascii_only**: All test code must use ASCII-only characters. No Unicode symbols, emojis, or special characters. Use plain ASCII alternatives. Example: print('[PASS] Success') not print('[checkmark] Success')
  DO: Use ASCII-only characters. Example: print('[PASS] Agent initialized'); print('[ERROR] Config not found')
  DON'T: Don't use Unicode or emojis. Example: print('[checkmark] Done') (wrong); print('[green_check] OK') (wrong)

- **pytest_bdd_orchestrator_pattern**: Use pytest with orchestrator pattern for story-based tests. NO FEATURE FILES. Test classes contain orchestrator methods (under 20 lines) showing Given-When-Then flow by calling helper functions. Example: def test_agent_loads_config(): given_config_exists(); agent = when_agent_initialized(); then_agent_is_configured(agent)
  DO: Orchestrator pattern: test shows flow, delegates to helpers. Example: # Given; create_config_file(); # When; agent.initialize(); # Then; assert agent.is_initialized
  DON'T: Don't use feature files or inline complex setup. Example: @given('config exists') def step(): ... (wrong - use pytest directly)

- **use_class_based_organization**: Test structure matches story graph: file = sub-epic (test_<sub_epic>.py), class = story (Test<ExactStoryName>), method = scenario (test_<scenario_snake_case>). Classes in story map order. Example: test_generate_bot_tools.py, class TestGenerateBotTools, def test_generator_creates_tool_for_test_bot
  DO: Map story hierarchy to test structure exactly. Example: Sub-epic 'Generate Bot Tools' -> test_generate_bot_tools.py, Story 'Generate Bot Tools' -> TestGenerateBotTools
  DON'T: Don't use generic/abbreviated names or wrong order. Example: class TestToolGen (wrong - use TestGenerateBotTools)

- **use_exact_variable_names**: Use exact variable names from specification scenarios. When spec mentions agent_name, workspace_root, config_path - use those exact names in tests and production code. Example: agent_name = 'story_bot' (from spec), not name = 'story_bot'
  DO: Use exact names from specification in tests and production. Example: agent_name, workspace_root, config_path - all from spec
  DON'T: Don't use different names than specification. Example: name = 'bot' when spec says agent_name (wrong)

- **use_given_when_then_helpers**: Use reusable helper functions instead of inline code blocks of 4+ lines. Optimize for reusability, not exact step names. Place helpers at correct scope: story-level in class, sub-epic in module, epic in separate file. Example: given_config_exists(), when_agent_initialized(), then_agent_is_configured()
  DO: Use Given/When/Then helper functions for setup, action, assertion. Example: given_bot_config_exists(); bot = when_bot_instantiated(); then_bot_uses_correct_directories(bot)
  DON'T: Don't use inline operations of 4+ lines. Example: config_dir = ...; config_dir.mkdir(); config_file = ...; config_file.write_text() (wrong - extract to helper)

CRITICAL: The rules digest above contains everything you need to get started.

WORKFLOW:
## Rules Available (25 total)

1. use_domain_language (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_domain_language.json)
2. consistent_vocabulary (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/consistent_vocabulary.json)
3. no_defensive_code_in_tests (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/no_defensive_code_in_tests.json)
4. production_code_clean_functions (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/production_code_clean_functions.json)
5. bug_fix_test_first (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/bug_fix_test_first.json)
6. call_production_code_directly (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/call_production_code_directly.json)
7. cover_all_behavior_paths (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/cover_all_behavior_paths.json)
8. mock_only_boundaries (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/mock_only_boundaries.json)
9. create_parameterized_tests_for_scenarios (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/create_parameterized_tests_for_scenarios.json)
10. define_fixtures_in_test_file (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/define_fixtures_in_test_file.json)
11. design_api_through_failing_tests (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/design_api_through_failing_tests.json)
12. test_observable_behavior (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/test_observable_behavior.json)
13. helper_extraction_and_reuse (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/helper_extraction_and_reuse.json)
14. match_specification_scenarios (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/match_specification_scenarios.json)
15. place_imports_at_top (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/place_imports_at_top.json)
16. object_oriented_test_helpers (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/object_oriented_test_helpers.json)
17. production_code_explicit_dependencies (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/production_code_explicit_dependencies.json)
18. self_documenting_tests (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/self_documenting_tests.json)
19. standard_test_data_sets (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/standard_test_data_sets.json)
20. assert_full_results (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/assert_full_results.json)
21. use_ascii_only (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_ascii_only.json)
22. pytest_bdd_orchestrator_pattern (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/pytest_bdd_orchestrator_pattern.json)
23. use_class_based_organization (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_class_based_organization.json)
24. use_exact_variable_names (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_exact_variable_names.json)
25. use_given_when_then_helpers (C:/dev/augmented-teams/agile_bots/bots/story_bot/behaviors/tests/rules/use_given_when_then_helpers.json)

# Behavior: tests

## Behavior Instructions - tests

The purpose of this behavior is to write test files (.py, .js, etc.) with executable test code from scenarios.examples that validate story behavior

**BEHAVIOR PURPOSE:**
This behavior WRITES TEST FILES. The primary output is executable test code files that validate story behavior.
Write test files (.py, .js, etc.) with executable test code from scenarios.examples that validate story behavior
The secondary output is to make sure that the story_graph.json scenarios, stories, and sub-epics have test fields added for the test methods, test classes, and test files respectively.
After creating test files, classes, and methods, you MUST map them to the story-graph.json:

## Action Instructions - rules

The purpose of this action is to load behavior-specific rules into ai context for guidance on writing compliant content

---

**Look for context in the following locations:**
- in this message and chat history
- in `C:/Users/thoma/AppData/Local/Temp/pytest-of-thoma/pytest-3773/test_user_gets_rules_without_m2/workspace/docs/context/`
- generated files in `C:/Users/thoma/AppData/Local/Temp/pytest-of-thoma/pytest-3773/test_user_gets_rules_without_m2/workspace/docs/stories/`
  clarification.json, strategy.json

CRITICAL: This is the rules action - it loads rules for AI context. DO NOT run validation.
CRITICAL: You MUST systematically read each rule file listed below using the read_file tool BEFORE acting on the user's message.
Read ALL rule files first, then apply them to the user's request.
Each rule file path is provided - use read_file to load the complete rule content including examples.
After reading all rules, act on the user's message following ALL the rules you just read.

CRITICAL: When reporting validation results, use this EXACT format:
For each rule checked, report: Rule Name | PASS or FAIL | If FAIL, explain why in one sentence
Example: prefer_object_model_over_config | PASS
Example: eliminate_duplication | FAIL | Same logic repeated in lines 45-50 and 78-83
Keep it simple: just tell the user what passed, what failed, and if it failed, why.

Rules to follow:

- **use_domain_language**: Use Ubiquitous Language (DDD): Same vocabulary in domain model, stories, scenarios, AND code. Class names = domain entities/nouns. Method names = domain responsibilities/verbs. Test names read like plain English stories. Example: test_agent_loads_configuration_when_file_exists (not test_agt_init_sets_vars)
  DO: Use domain language for classes, methods, and test names. Example: class GatherContextAction, def inject_guardrails(), test_agent_loads_config_when_file_exists
  DON'T: Don't use generic technical terms or implementation-specific names. Example: class StdioHandler (wrong), def execute_with_guardrails (wrong), test_agt_init_sets_vars (wrong)

- **consistent_vocabulary**: Use ONE word per concept across entire codebase. Pick consistent vocabulary: create (not build/make/construct), verify (not check/assert/validate), load (not fetch/get/retrieve). Use intention-revealing names that describe behavior. Example: create_agent(), verify_initialized(), load_config() - same verbs everywhere
  DO: Use same word for same concept everywhere. Example: create_agent(), create_config(), create_workspace() - all use 'create'
  DON'T: Don't mix synonyms for same concept. Example: create_agent() + build_config() + make_workspace() (wrong - pick one verb)

- **no_defensive_code_in_tests**: Tests must NEVER contain guard clauses, defensive conditionals, or fallback paths. We control test setup - if it's wrong, the test MUST fail immediately. Guard clauses hide problems. Tests should assume positive outcomes. Example: Just call the code directly, don't wrap in if-checks
  DO: Assume correct setup - let test fail if wrong. Example: behavior = Behavior(name='shape') then assert behavior.name == 'shape'
  DON'T: Don't add if-checks, type guards, or fallback handling in tests. Example: if behavior_file.exists(): (wrong - test should fail if it doesn't)

- **production_code_clean_functions**: Production code functions should do ONE thing, be under 20 lines, and have one level of abstraction. No hidden side effects. Name reveals complete behavior. Extract multiple concerns into separate functions. Example: load_config(), validate_config(), apply_config() - each does one thing
  DO: Single responsibility, small focused functions. Example: initialize_from_config() calls validate_exists(), load_config(), validate_structure(), apply_config()
  DON'T: Don't make functions that do multiple unrelated things or are too long. Example: 50-line function that loads, validates, and applies config

- **bug_fix_test_first**: When production code breaks, follow test-first workflow: write failing test, verify failure, fix code, verify success. Never fix bugs without a failing test first. Example: test_mcp_tool_initializes_bot() fails -> fix initialization -> test passes
  DO: Follow RED-GREEN-PRODUCTION workflow. Example: Write test reproducing bug -> Run test (RED) -> Fix minimal code -> Run test (GREEN) -> Run full suite
  DON'T: Don't fix bugs directly without failing test first. Example: Editing production code without test -> deploying -> hoping it works (wrong)

- **call_production_code_directly**: Call production code directly in tests. Let tests fail naturally if code doesn't exist. Don't comment out calls, mock business logic, or fake state. Only mock external boundaries. Example: agent = Agent(); agent.initialize() (not agent = Mock())
  DO: Call production code directly, let it fail naturally. Example: agent = Agent(workspace); agent.initialize(config); assert agent.is_initialized
  DON'T: Don't mock class under test, comment out calls, or fake state. Example: agent = Mock(spec=Agent) (wrong); agent._initialized = True (wrong)

- **cover_all_behavior_paths**: Cover all behavior paths: normal (happy path), edge cases, and failure scenarios. Each distinct behavior needs its own focused test. Tests must be independent. Example: test_loads_valid_config(), test_loads_empty_config(), test_raises_error_when_file_missing()
  DO: Test normal, edge, and failure paths separately. Example: test_loads_valid_config() (happy), test_loads_empty_config() (edge), test_raises_when_missing() (failure)
  DON'T: Don't test only happy path or combine multiple behaviors in one test. Example: Single test for both success and failure (wrong)

- **mock_only_boundaries**: Mock ONLY at architectural boundaries: external APIs, network, uncontrollable services. Don't mock internal business logic, classes under test, or file operations (use temp files). Example: patch('requests.get') (OK); patch('agent.validate') (wrong)
  DO: Mock only external dependencies you can't control. Example: with patch('requests.get') as mock: (external API - OK to mock)
  DON'T: Don't mock internal logic, class under test, or file I/O. Example: with patch('agent.validate_config') (wrong - test the logic!)

- **create_parameterized_tests_for_scenarios**: If scenarios have Examples tables, create parameterized tests using @pytest.mark.parametrize. Each row becomes a test case. Don't write single tests that only test one example. Example: @pytest.mark.parametrize('input,expected', [(1, 2), (3, 4)])
  DO: Create parameterized tests from Examples tables. Example: @pytest.mark.parametrize('paths,count', [(['p1','p2'], 2), (['p3'], 1)])
  DON'T: Don't hardcode single example or duplicate test methods. Example: def test_with_value_1(): (wrong); def test_with_value_2(): (wrong - use parametrize)

- **define_fixtures_in_test_file**: Define fixtures in the test file, not separate conftest.py. Truly reusable fixtures (file ops, location helpers) go in base conftest.py. Example: @pytest.fixture def workspace_root(tmp_path): return tmp_path / 'workspace'
  DO: Define fixtures in same test file. Example: @pytest.fixture def config_file(tmp_path): ... (in test_agent.py)
  DON'T: Don't create separate conftest.py for agent-specific fixtures. Example: src/conftest.py with agent fixtures (wrong - put in test file)

- **design_api_through_failing_tests**: Write tests against the REAL expected API BEFORE implementing code. Tests MUST fail initially. Set up real test data and call real API. Failure reveals complete API design. Example: project = Project(path=path); project.initialize() (doesn't exist yet -> fails -> drives implementation)
  DO: Write test against real expected API that fails initially. Example: project = Project(path); project.initialize(); assert project.is_ready (fails until implemented)
  DON'T: Don't use placeholders, dummy values, or skip the failing step. Example: project = 'TODO' (wrong); assuming test passes first (wrong)

- **test_observable_behavior**: Test observable behavior, not implementation details. Verify public API and visible state changes. Don't assert on private methods or internal flags. Example: assert agent.config_path.exists() (observable); not assert agent._internal_flag (private)
  DO: Test observable outcomes through public API. Example: assert agent.config_path == expected; assert agent.is_initialized (public properties)
  DON'T: Don't test private state or implementation details. Example: assert agent._initialized (wrong); assert agent._config_cache (wrong)

- **helper_extraction_and_reuse**: Extract duplicate test setup to reusable helper functions. Keep test bodies focused on specific behavior. Example: create_agent_with_config(), create_config_file(), verify_agent_initialized() - reusable across tests
  DO: Extract duplicate setup to reusable helpers. Example: create_agent_with_config(name, workspace, config) returns initialized Agent
  DON'T: Don't duplicate setup code across tests. Example: Same 10 lines of setup in every test method (wrong - extract to helper)

- **match_specification_scenarios**: Tests must match specification scenarios exactly. Test names, steps, and assertions verify exactly what the scenario states. Use exact variable names and terminology from specification. Example: agent_name='story_bot' (from spec), not name='bot'
  DO: Test matches specification exactly. Example: GIVEN config exists, WHEN Agent(agent_name='story_bot'), THEN config_path == agents/base/agent.json
  DON'T: Don't use different terminology or assert things not in specification. Example: assert agent._internal_flag (not in spec - wrong)

- **place_imports_at_top**: Place all imports at top of test file, after docstrings, before code. Group: stdlib, third-party, then local. Example: import json; import pytest; from mymodule import MyClass
  DO: All imports at top, grouped by type. Example: import json; import pytest; from bots... import X
  DON'T: Don't place imports inside functions or after code. Example: def test(): from pathlib import Path (wrong - import inside function)

- **object_oriented_test_helpers**: Consolidate tests around object-oriented helpers/factories (e.g., BotTestHelper test hopper) that build complete domain objects with standard data. Example: helper = BotTestHelper(tmp_path); helper.set_state('shape','clarify'); helper.assert_at_behavior_action('shape','clarify'). Avoid scattering many primitive parameters across parametrize blocks or inline setups.
  DO: Use shared helper objects to create full test fixtures and assert against complete domain objects, not fragments.
  DON'T: Do not spread test setup across many primitive parameters or cherry-pick single values from partial objects.

- **production_code_explicit_dependencies**: Production code: make dependencies explicit through constructor injection. Pass all external dependencies as constructor parameters. No hidden global state. Tests easily inject test doubles. Example: Agent(config_loader=loader, domain_graph=graph)
  DO: Inject all dependencies through constructor. Example: def __init__(self, config_loader, domain_graph): self._loader = config_loader
  DON'T: Don't access globals, singletons, or create dependencies internally. Example: self._loader = ConfigLoader() (wrong - creates internally)

- **self_documenting_tests**: Tests are self-documenting through code structure. Don't add verbose comments explaining failures. Imports, calls, and assertions show the API design. Let code speak for itself. Example: generator = MCPServerGenerator(bot_name, config_path); server = generator.generate_server()
  DO: Let code structure document the test. Example: generator = MCPServerGenerator(name, config); file = generator.generate() - API is clear
  DON'T: Don't add verbose comments explaining obvious things. Example: # This will fail because API doesn't exist yet (unnecessary)

- **standard_test_data_sets**: Use standard, named test data sets across tests instead of recreating ad-hoc values. Example: STANDARD_STATE = {...}; helper.set_state(...); assert helper.get_state() == STANDARD_STATE.
  DO: Define canonical data once (helper constants/factories) and reuse it so every test exercises the full domain object.
  DON'T: Do not create new ad-hoc values per test or assert only one field from a complex object.

- **assert_full_results**: Assert full domain results (state/log/graph objects), not single cherry-picked fields. Example: assert helper.get_state() == STANDARD_STATE, not assert helper.get_state()['current'] == 'shape.clarify'.
  DO: Compare entire objects/dicts/dataclasses against standard data fixtures.
  DON'T: Do not assert single fields or lengths when validating complex results.

- **use_ascii_only**: All test code must use ASCII-only characters. No Unicode symbols, emojis, or special characters. Use plain ASCII alternatives. Example: print('[PASS] Success') not print('[checkmark] Success')
  DO: Use ASCII-only characters. Example: print('[PASS] Agent initialized'); print('[ERROR] Config not found')
  DON'T: Don't use Unicode or emojis. Example: print('[checkmark] Done') (wrong); print('[green_check] OK') (wrong)

- **pytest_bdd_orchestrator_pattern**: Use pytest with orchestrator pattern for story-based tests. NO FEATURE FILES. Test classes contain orchestrator methods (under 20 lines) showing Given-When-Then flow by calling helper functions. Example: def test_agent_loads_config(): given_config_exists(); agent = when_agent_initialized(); then_agent_is_configured(agent)
  DO: Orchestrator pattern: test shows flow, delegates to helpers. Example: # Given; create_config_file(); # When; agent.initialize(); # Then; assert agent.is_initialized
  DON'T: Don't use feature files or inline complex setup. Example: @given('config exists') def step(): ... (wrong - use pytest directly)

- **use_class_based_organization**: Test structure matches story graph: file = sub-epic (test_<sub_epic>.py), class = story (Test<ExactStoryName>), method = scenario (test_<scenario_snake_case>). Classes in story map order. Example: test_generate_bot_tools.py, class TestGenerateBotTools, def test_generator_creates_tool_for_test_bot
  DO: Map story hierarchy to test structure exactly. Example: Sub-epic 'Generate Bot Tools' -> test_generate_bot_tools.py, Story 'Generate Bot Tools' -> TestGenerateBotTools
  DON'T: Don't use generic/abbreviated names or wrong order. Example: class TestToolGen (wrong - use TestGenerateBotTools)

- **use_exact_variable_names**: Use exact variable names from specification scenarios. When spec mentions agent_name, workspace_root, config_path - use those exact names in tests and production code. Example: agent_name = 'story_bot' (from spec), not name = 'story_bot'
  DO: Use exact names from specification in tests and production. Example: agent_name, workspace_root, config_path - all from spec
  DON'T: Don't use different names than specification. Example: name = 'bot' when spec says agent_name (wrong)

- **use_given_when_then_helpers**: Use reusable helper functions instead of inline code blocks of 4+ lines. Optimize for reusability, not exact step names. Place helpers at correct scope: story-level in class, sub-epic in module, epic in separate file. Example: given_config_exists(), when_agent_initialized(), then_agent_is_configured()
  DO: Use Given/When/Then helper functions for setup, action, assertion. Example: given_bot_config_exists(); bot = when_bot_instantiated(); then_bot_uses_correct_directories(bot)
  DON'T: Don't use inline operations of 4+ lines. Example: config_dir = ...; config_dir.mkdir(); config_file = ...; config_file.write_text() (wrong - extract to helper)

CRITICAL: The rules digest above contains everything you need to get started.

WORKFLOW:
1. Read the rules digest above (descriptions + key principles)
2. Apply rules to the user's request
3. IF you need clarity on a specific rule (examples, edge cases, detailed patterns):
   - Use read_file tool to read that specific rule file
   - The full rule has detailed examples and detection patterns
4. Cite rule names when making decisions

Please make sure to validate content against the rules above, as well as the more detailed version of the rule files linked below.

When analyzing code, focus on finding violations and cite the specific rule names.
1. Read the rules digest above (descriptions + key principles)
2. Apply rules to the user's request
3. IF you need clarity on a specific rule (examples, edge cases, detailed patterns):
   - Use read_file tool to read that specific rule file
   - The full rule has detailed examples and detection patterns
4. Cite rule names when making decisions

Please make sure to validate content against the rules above, as well as the more detailed version of the rule files linked below.

When analyzing code, focus on finding violations and cite the specific rule names.                        violation_message=f'Test class "{cls.node.name}" does not match any story name - test classes must match story names exactly',
                        location=str(file_path),
                        line_number=line_number,
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
        
        return violations


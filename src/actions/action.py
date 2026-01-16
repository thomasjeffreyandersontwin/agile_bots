from pathlib import Path
from typing import Dict, Any, Optional, TYPE_CHECKING, List, Type
import json
import logging
import re
import sys
import traceback
from .activity_tracker import ActivityTracker, ActionState
from .behavior_action_status_builder import BehaviorActionStatusBuilder
from ..instructions.context_data_injector import ContextDataInjector
from ..instructions.instructions import Instructions
from .action_context import ActionContext
from ..scope import Scope
from ..instructions.reminders import inject_reminder_to_instructions
from ..bot.workspace import get_base_actions_directory
from ..utils import read_json_file
if TYPE_CHECKING:
    from ..bot.bot import Bot
    from ..bot.behavior import Behavior
    from ..bot.behaviors import Behaviors
logger = logging.getLogger(__name__)

class Action:
    context_class: Type[ActionContext] = ActionContext

    def __init__(self, behavior: 'Behavior', action_config: Dict[str, Any]=None, action_name: str=None):
        self.behavior = behavior
        self.action_config = action_config
        action_name = action_name or self._derive_action_name_from_class()
        self._action_name = action_name
        self._activity_tracker = ActivityTracker(behavior.bot_paths, behavior.bot_name)
        self._workflow_status_builder = BehaviorActionStatusBuilder(behavior)
        self._context_data_injector = ContextDataInjector(behavior)
        self._base_config = self._load_base_config()
        if action_config:
            self._apply_action_config()
        self._initialize_properties()

    def _load_base_config(self) -> Dict[str, Any]:
        final_action_name = self.action_name
        base_actions_dir = get_base_actions_directory()
        base_config_path = base_actions_dir / final_action_name / 'action_config.json'
        base_config = read_json_file(base_config_path)
        base_config['name'] = final_action_name
        return base_config

    def _apply_action_config(self) -> None:
        action_config = self.action_config
        if 'order' in action_config:
            self._base_config['order'] = action_config['order']
        self._base_config['custom_class'] = action_config.get('action_class') or action_config.get('custom_class')
        if 'next_action' in action_config:
            self._base_config['next_action'] = action_config['next_action']
        if 'auto_confirm' in action_config:
            self._base_config['auto_confirm'] = action_config['auto_confirm']
        if 'skip_confirm' in action_config:
            self._base_config['skip_confirm'] = action_config['skip_confirm']
        if 'skip_confirm' in action_config:
            self._base_config['skip_confirm'] = action_config['skip_confirm']

    def _initialize_properties(self) -> None:
        self.order = self._base_config.get('order', 0)
        self.next_action = self._base_config.get('next_action')
        self.action_class = self._base_config.get('action_class') or self._base_config.get('custom_class')
        self.workflow = self._base_config.get('workflow', True)
        self.auto_confirm = self._base_config.get('auto_confirm', False)
        self.skip_confirm = self._base_config.get('skip_confirm', False)
        self.skip_confirm = self._base_config.get('skip_confirm', False)

    def _derive_action_name_from_class(self) -> str:
        class_name = self.__class__.__name__
        if class_name.endswith('Action'):
            base_name = class_name[:-6]
        else:
            base_name = class_name
        snake_case = re.sub('(?<!^)(?=[A-Z])', '_', base_name).lower()
        normalization_map = {'render_output': 'render', 'build_knowledge': 'build', 'validate_rules': 'validate', 'clarify_context': 'clarify'}
        return normalization_map.get(snake_case, snake_case)

    @property
    def action_name(self) -> str:
        return self._action_name

    @action_name.setter
    def action_name(self, value: str):
        raise AttributeError("action_name is read-only. It's derived from the class name.")

    @property
    def description(self) -> str:
        return self._base_config.get('description', '')
    
    @property
    def help(self) -> Dict[str, Any]:
        import dataclasses
        from typing import get_origin
        
        help_dict = {
            'description': self.description,
            'parameters': []
        }
        
        if hasattr(self.__class__, 'context_class'):
            context_class = self.__class__.context_class
            if dataclasses.is_dataclass(context_class):
                for field in dataclasses.fields(context_class):
                    param_info = {
                        'name': field.name,
                        'cli_name': f'--{field.name.replace("_", "-")}',
                        'type': self._get_type_string(field.type),
                        'description': self._get_parameter_description(field.name)
                    }
                    help_dict['parameters'].append(param_info)
        
        return help_dict
    
    def _get_type_string(self, python_type) -> str:
        if python_type is type(None):
            return "none"
        if python_type == str:
            return "string"
        elif python_type == Path:
            return "path"
        elif python_type == int:
            return "int"
        elif python_type == float:
            return "float"
        elif python_type == bool:
            return "bool"
        elif python_type == dict:
            return "dict"
        elif python_type == list:
            return "list"
        
        from typing import get_origin
        origin = get_origin(python_type)
        if origin is dict:
            return "dict"
        elif origin is list:
            return "list"
        elif origin is tuple:
            return "tuple"
        elif origin is set:
            return "set"
        
        return "value"
    
    def _get_parameter_description(self, param_name: str) -> str:
        """Get meaningful description for a parameter by delegating to domain objects."""
        from .clarify.requirements_clarifications import RequirementsClarifications
        from .strategy.strategy_decision import StrategyDecision
        from ..scope import Scope
        
        # Registry mapping parameter name patterns to domain object description methods
        description_registry = [
            (['answers', 'key_questions_answered'], RequirementsClarifications.get_answers_parameter_description),
            (['evidence_provided', 'evidence'], RequirementsClarifications.get_evidence_parameter_description),
            (['choices', 'decisions_made', 'decisions'], StrategyDecision.get_decisions_parameter_description),
            (['assumptions', 'assumptions_made'], StrategyDecision.get_assumptions_parameter_description),
            (['scope'], Scope.get_parameter_description),
        ]
        
        # Check each pattern in registry
        for patterns, description_method in description_registry:
            if any(pattern in param_name for pattern in patterns):
                return description_method()
        
        # Handle path/directory separately (not a domain object)
        if 'path' in param_name or 'directory' in param_name:
            return "Path to working directory or file"
        
        return "Optional parameter"

    def _inject_clarification_data(self, instructions: Dict[str, Any]) -> list:
        return self._context_data_injector.inject_clarification_data(instructions)

    def _inject_strategy_data(self, instructions: Dict[str, Any]) -> list:
        return self._context_data_injector.inject_strategy_data(instructions)

    def _inject_context_files(self, instructions: Dict[str, Any]) -> list:
        return self._context_data_injector.inject_context_files(instructions)

    def get_workflow_status_breadcrumbs(self) -> list:
        return self._workflow_status_builder.get_behavior_action_status_breadcrumbs()

    def _replace_context_placeholders(self, instructions_list: List[str]) -> List[str]:
        replacements = {
            '{project_area}': str(self.behavior.bot_paths.workspace_directory),
            '{bot}': str(self.behavior.bot_paths.bot_directory),
            '{behavior}': self.behavior.name
        }
        
        result = []
        for instruction in instructions_list:
            replaced = instruction
            for placeholder, value in replacements.items():
                replaced = replaced.replace(placeholder, value)
            result.append(replaced)
        return result
    
    def _load_scope_from_state(self) -> Optional[Scope]:
        if hasattr(self.behavior, 'bot') and self.behavior.bot:
            return self.behavior.bot._scope
        return Scope(self.behavior.bot_paths.workspace_directory, self.behavior.bot_paths)
    
    @property
    def instructions(self) -> Instructions:
        base_instructions = self._base_config.get('instructions', [])
        
        if isinstance(base_instructions, list):
            base_instructions = self._replace_context_placeholders(base_instructions)
        
        scope = self._load_scope_from_state()
        
        inst = Instructions(
            base_instructions if isinstance(base_instructions, list) else [],
            bot_paths=self.behavior.bot_paths,
            scope=scope
        )
        
        context_instructions = []
        injected_data = {}
        try:
            context_instructions.extend(self._inject_clarification_data(injected_data))
            context_instructions.extend(self._inject_strategy_data(injected_data))
        except FileNotFoundError as e:
            logger.debug(f'Clarification or strategy data files not found: {e}')
            raise
        context_instructions.extend(self._inject_context_files(injected_data))
        
        for key, value in injected_data.items():
            inst._data[key] = value
        
        for line in reversed(inst.context_sources_text):
            inst._data['base_instructions'].insert(0, line)
        inst._data['base_instructions'].insert(len(inst.context_sources_text), "")
        
        for line in reversed(context_instructions):
            inst._data['base_instructions'].insert(len(inst.context_sources_text) + 1, line)
        
        
        return inst

    @property
    def tracker(self) -> ActivityTracker:
        return self._activity_tracker

    @property
    def base_actions_dir(self) -> Path:
        return get_base_actions_directory()

    @property
    def working_dir(self) -> Path:
        return self.behavior.bot_paths.workspace_directory

    @property
    def bot_dir(self) -> Path:
        return self.behavior.bot_paths.bot_directory

    def track_activity_on_start(self):
        state = ActionState(self.behavior.bot_name, self.behavior.name, self.action_name)
        self.tracker.track_start(state)

    def track_activity_on_completion(self, outputs: dict=None, duration: int=None):
        state = ActionState(self.behavior.bot_name, self.behavior.name, self.action_name, outputs=outputs, duration=duration)
        self.tracker.track_completion(state)

    def execute(self, context: ActionContext = None) -> Dict[str, Any]:
        self.track_activity_on_start()
        if context is None:
            context = self.context_class()
        try:
            result = self.do_execute(context)
            
            result = self._finalize_display_content(result)
            
            if not result.get('_background_execution', False):
                self.track_activity_on_completion(outputs=result)
            return self._inject_reminders_if_final(result)
        except Exception as e:
            self._handle_execution_error(e, {})
            raise
    
    def _finalize_display_content(self, result: Dict[str, Any]) -> Dict[str, Any]:
        if 'instructions' not in result or not isinstance(result['instructions'], dict):
            return result
        
        instructions_dict = result['instructions']
        
        display_content_list = instructions_dict.get('display_content', [])
        if not display_content_list:
            return result
        
        inst = Instructions(bot_paths=self.behavior.bot_paths)
        for line in display_content_list:
            inst.add_display(line)
        
        display_file = inst.write_display_to_file('status.md')
        if display_file:
            if 'base_instructions' not in instructions_dict:
                instructions_dict['base_instructions'] = []
            instructions_dict['base_instructions'].append('')
            instructions_dict['base_instructions'].append(f'CRITICAL: You MUST read the file `{display_file}` and display its ENTIRE contents in a markdown code fence to the user.')
            instructions_dict['base_instructions'].append(f'Use the read_file tool to read `{display_file}` and then display the full contents.')
            instructions_dict['base_instructions'].append(f'DO NOT just reference the file - actually READ it and SHOW its contents to the user.')
        
        return result

    def _handle_execution_error(self, e: Exception, parameters: Dict[str, Any]) -> None:
        error_type = type(e).__name__
        error_message = str(e)
        full_traceback = traceback.format_exc()
        error_instructions = self._build_error_instructions(error_type, error_message, full_traceback, parameters)
        self.track_activity_on_completion(outputs={'error': error_message})
        print('\n'.join(error_instructions), file=sys.stdout)
        sys.stdout.flush()

    def _build_error_instructions(self, error_type: str, error_message: str, full_traceback: str, parameters: Dict[str, Any]) -> List[str]:
        return ['', '=' * 70, '**ERROR OCCURRED DURING ACTION EXECUTION**', '=' * 70, '', f'**Exception Type:** {error_type}', f'**Exception Message:** {error_message}', '', '**Full Traceback:**', '-' * 70, full_traceback, '-' * 70, '', '**Action Details:**', f"- Behavior: {(self.behavior.name if self.behavior else 'unknown')}", f'- Action: {self.action_name}', f'- Parameters: {parameters}', '=' * 70, '', '**AI ASSISTANT: YOU MUST DISPLAY THE ABOVE ERROR TO THE USER.**', '']

    def _inject_reminders_if_final(self, result: Dict[str, Any]) -> Dict[str, Any]:
        if not self.behavior or not self.behavior.actions:
            return result
        action_names = self.behavior.actions.names
        if not action_names or self.action_name != action_names[-1]:
            return result
        if not self.behavior.bot:
            if hasattr(self.behavior, 'actions') and hasattr(self.behavior.actions, 'behavior'):
                behavior_from_actions = self.behavior.actions.behavior
                if hasattr(behavior_from_actions, 'bot_paths'):
                    logger.debug(f'Behavior {self.behavior.name} has no bot reference - reminder will be skipped. This may indicate the behavior was not created through Bot.__init__')
                return result
        reminder = self.behavior.actions._get_next_behavior_reminder()
        if not reminder:
            logger.debug(f'Reminder is empty for action {self.action_name} in behavior {(self.behavior.name if self.behavior else None)}. behavior.bot={(self.behavior.bot if self.behavior else None)}, behavior.bot.behaviors.names={(self.behavior.bot.behaviors.names if self.behavior and self.behavior.bot else None)}')
            return result
        if 'instructions' not in result:
            result['instructions'] = {}
        instructions = result['instructions']
        if isinstance(instructions, dict):
            base_instructions = instructions.get('base_instructions', [])
            if not base_instructions and isinstance(self.instructions, dict) and ('base_instructions' in self.instructions):
                instructions['base_instructions'] = list(self.instructions['base_instructions'])
                result['instructions'] = instructions
        return inject_reminder_to_instructions(result, reminder)

    def get_instructions(self, context: ActionContext = None) -> Instructions:
        if context is None:
            context = self.context_class()
        
        self._save_guardrails_if_provided(context)
        
        if hasattr(context, 'scope') and context.scope:
            context.scope.apply_to_bot()
        
        instructions = self.instructions.copy()
        
        if self.action_config and 'instructions' in self.action_config:
            behavior_instructions = self.action_config.get('instructions', [])
            if behavior_instructions:
                if isinstance(behavior_instructions, list):
                    instructions._data['base_instructions'].extend(behavior_instructions)
                elif isinstance(behavior_instructions, str):
                    instructions._data['base_instructions'].append(behavior_instructions)
        
        self._load_behavior_guardrails(instructions)
        
        self._prepare_instructions(instructions, context)
        
        self._add_behavior_action_metadata(instructions)
        
        self._build_display_content(instructions)
        
        return instructions
    
    def _save_guardrails_if_provided(self, context: ActionContext):
        if hasattr(context, 'answers') and context.answers:
            try:
                from .clarify.requirements_clarifications import RequirementsClarifications
                from .clarify.required_context import RequiredContext
                
                required_context = None
                if hasattr(self, 'required_context'):
                    required_context = self.required_context
                elif self.behavior and hasattr(self.behavior, 'folder'):
                    required_context = RequiredContext(self.behavior.folder)
                
                if required_context:
                    clarifications = RequirementsClarifications(
                        behavior_name=self.behavior.name,
                        bot_paths=self.behavior.bot_paths,
                        required_context=required_context,
                        key_questions_answered=context.answers,
                        evidence_provided=getattr(context, 'evidence_provided', {}),
                        context=getattr(context, 'context', None)
                    )
                    clarifications.save()
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f'Failed to save clarification data: {e}')
        
        decisions = getattr(context, 'decisions_made', None) or getattr(context, 'decisions', None)
        if decisions:
            try:
                from .strategy.strategy_decision import StrategyDecision
                from .strategy.strategy import Strategy
                from pathlib import Path
                
                strategy_obj = None
                if self.behavior and hasattr(self.behavior, 'folder'):
                    strategy_obj = Strategy(Path(self.behavior.folder))
                
                if strategy_obj:
                    strategy_decision = StrategyDecision(
                        behavior_name=self.behavior.name,
                        bot_paths=self.behavior.bot_paths,
                        strategy=strategy_obj,
                        decisions_made=decisions,
                        assumptions_made=getattr(context, 'assumptions', [])
                    )
                    strategy_decision.save()
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f'Failed to save strategy data: {e}')
    
    def _load_behavior_guardrails(self, instructions):
        try:
            if not self.behavior or not hasattr(self.behavior, 'guardrails'):
                return
            
            guardrails_obj = self.behavior.guardrails
            if hasattr(guardrails_obj, 'required_context'):
                required_context = guardrails_obj.required_context
                if hasattr(required_context, 'instructions'):
                    if 'guardrails' not in instructions._data:
                        instructions.set('guardrails', {'required_context': required_context.instructions})
        except Exception:
            pass
    
        self._load_all_saved_guardrails(instructions)
    
    def _load_all_saved_guardrails(self, instructions):
        if not self.behavior:
            return
        
        try:
            from .clarify.requirements_clarifications import RequirementsClarifications
            from .clarify.required_context import RequiredContext
            
            required_context = None
            if hasattr(self.behavior, 'guardrails') and hasattr(self.behavior.guardrails, 'required_context'):
                required_context = self.behavior.guardrails.required_context
            else:
                required_context = RequiredContext(self.behavior.folder)
            
            clarifications = RequirementsClarifications(
                behavior_name=self.behavior.name,
                bot_paths=self.behavior.bot_paths,
                required_context=required_context,
                key_questions_answered={},
                evidence_provided={}
            )
            saved_clarifications = clarifications.load()
            if saved_clarifications and self.behavior.name in saved_clarifications:
                instructions.set('clarification', saved_clarifications[self.behavior.name])
        except Exception as e:
            import logging
            logging.getLogger(__name__).debug(f'Could not load saved clarifications: {e}')
        
        try:
            from .strategy.strategy_decision import StrategyDecision
            from .strategy.strategy import Strategy
            
            strategy = Strategy(self.behavior.folder)
            strategy_data = strategy.instructions
            
            saved_strategy = StrategyDecision.load_all(self.behavior.bot_paths)
            saved_behavior_data = saved_strategy.get(self.behavior.name, {}) if saved_strategy else {}
            
            combined_strategy_criteria = {}
            combined_assumptions = {}
            
            if strategy_data:
                criteria_template = strategy_data.get('strategy_criteria', {})
                if criteria_template:
                    combined_strategy_criteria['criteria'] = criteria_template
                
                assumptions_template = strategy_data.get('assumptions', {})
                if isinstance(assumptions_template, dict):
                    if 'typical_assumptions' in assumptions_template:
                        combined_assumptions['typical_assumptions'] = assumptions_template.get('typical_assumptions', [])
                    else:
                        combined_assumptions['typical_assumptions'] = assumptions_template
                elif isinstance(assumptions_template, list):
                    combined_assumptions['typical_assumptions'] = assumptions_template
            
            saved_decisions = saved_behavior_data.get('decisions', {})
            if saved_decisions:
                combined_strategy_criteria['decisions_made'] = saved_decisions
            
            saved_assumptions = saved_behavior_data.get('assumptions', [])
            if saved_assumptions:
                combined_assumptions['assumptions_made'] = saved_assumptions
            
            transformed_strategy = {}
            if combined_strategy_criteria:
                transformed_strategy['strategy_criteria'] = combined_strategy_criteria
            if combined_assumptions:
                transformed_strategy['assumptions'] = combined_assumptions
            
            if transformed_strategy:
                instructions.set('strategy', transformed_strategy)
        except Exception as e:
            import logging
            logging.getLogger(__name__).debug(f'Could not load saved strategy decisions: {e}')
    
    def _add_behavior_action_metadata(self, instructions):
        if self.behavior:
            behavior_data = {
                'name': self.behavior.name if hasattr(self.behavior, 'name') else 'unknown',
                'description': self.behavior.description if hasattr(self.behavior, 'description') else '',
                'instructions': []
            }
            
            if hasattr(self.behavior, 'instructions') and self.behavior.instructions:
                behavior_instructions = self.behavior.instructions
                if isinstance(behavior_instructions, list):
                    behavior_data['instructions'] = list(behavior_instructions)
                elif isinstance(behavior_instructions, str):
                    behavior_data['instructions'] = [behavior_instructions]
            
            instructions.set('behavior_metadata', behavior_data)
            instructions.set('behavior_instructions', behavior_data)
        
        action_data = {
            'name': self.action_name if hasattr(self, 'action_name') else 'unknown',
            'description': self.description if hasattr(self, 'description') else '',
            'instructions': []
        }
        
        if self.action_config and 'instructions' in self.action_config:
            behavior_action_instructions = self.action_config.get('instructions', [])
            if behavior_action_instructions:
                if isinstance(behavior_action_instructions, list):
                    action_data['instructions'] = list(behavior_action_instructions)
                elif isinstance(behavior_action_instructions, str):
                    action_data['instructions'] = [behavior_action_instructions]
        
        instructions.set('action_metadata', action_data)
        instructions.set('action_instructions', action_data)
    
    def _build_display_content(self, instructions: Instructions):
        from agile_bots.src.instructions.markdown_instructions import MarkdownInstructions

        temp_instructions = instructions.copy()
        temp_instructions._display_content = []
        
        markdown_adapter = MarkdownInstructions(temp_instructions)
        markdown_output = markdown_adapter.serialize()

        for line in markdown_output.split('\n'):
            instructions.add_display(line)
    
    def _prepare_instructions(self, instructions, context: ActionContext):
        pass
    
    def _format_behavior_section(self, output_lines: list):
        """Format behavior instructions section."""
        if not self.behavior:
            return
        
        behavior_name = self.behavior.name if hasattr(self.behavior, 'name') else 'unknown'
        output_lines.append(f"**Behavior Instructions - {behavior_name}**")
        
        if hasattr(self.behavior, 'description') and self.behavior.description:
            output_lines.append(f"The purpose of this behavior is to {self.behavior.description.lower()}")
            output_lines.append("")
        
        if hasattr(self.behavior, 'instructions') and self.behavior.instructions:
            behavior_instructions = self.behavior.instructions
            if isinstance(behavior_instructions, list):
                output_lines.extend(behavior_instructions)
            elif isinstance(behavior_instructions, str):
                output_lines.append(behavior_instructions)
            output_lines.append("")
    
    def _format_action_section(self, output_lines: list):
        """Format action instructions section."""
        action_name = self.action_name if hasattr(self, 'action_name') else 'unknown'
        output_lines.append(f"**Action Instructions - {action_name}**")
        
        if hasattr(self, 'description') and self.description:
            output_lines.append(f"The purpose of this action is to {self.description.lower()}")
            output_lines.append("")
        
        if self.action_config and 'instructions' in self.action_config:
            behavior_action_instructions = self.action_config.get('instructions', [])
            if behavior_action_instructions:
                output_lines.extend(behavior_action_instructions)
                output_lines.append("")
    
    def _format_key_questions(self, key_questions, output_lines: list):
        """Format key questions section."""
        if not key_questions:
            return
        
        output_lines.append("")
        output_lines.append("**Key Questions:**")
        
        if isinstance(key_questions, list):
            for question in key_questions:
                output_lines.append(f"- {question}")
        elif isinstance(key_questions, dict):
            for question_key, question_text in key_questions.items():
                output_lines.append(f"- **{question_key}**: {question_text}")
    
    def _format_evidence(self, evidence, output_lines: list):
        """Format evidence section."""
        if not evidence:
            return
        
        output_lines.append("")
        output_lines.append("**Evidence:**")
        
        if isinstance(evidence, list):
            output_lines.append(', '.join(evidence))
        elif isinstance(evidence, dict):
            for evidence_key, evidence_desc in evidence.items():
                output_lines.append(f"- **{evidence_key}**: {evidence_desc}")
    
    def _format_guardrails_section(self, guardrails_dict: dict, output_lines: list):
        """Format guardrails section with required context."""
        if not guardrails_dict:
            return
        
        required_context = guardrails_dict.get('required_context', {})
        if not required_context:
            return
        
        key_questions = required_context.get('key_questions', [])
        evidence = required_context.get('evidence', [])
        
        self._format_key_questions(key_questions, output_lines)
        self._format_evidence(evidence, output_lines)
    
    def _format_instructions_for_display(self, instructions) -> str:
        """Format instructions for display by building sections."""
        instructions_dict = instructions.to_dict()
        output_lines = []
        
        self._format_behavior_section(output_lines)
        self._format_action_section(output_lines)
        
        output_lines.append("---")
        output_lines.append("")
        
        base_instructions = instructions_dict.get('base_instructions', [])
        output_lines.extend(base_instructions)
        
        guardrails_dict = instructions_dict.get('guardrails', {})
        self._format_guardrails_section(guardrails_dict, output_lines)
        
        display_content = instructions_dict.get('display_content', [])
        if display_content:
            output_lines.append("")
            output_lines.extend(display_content)
        
        return "\n".join(output_lines)

    def do_execute(self, context: ActionContext = None) -> Dict[str, Any]:
        raise NotImplementedError('Subclasses must implement do_execute()')
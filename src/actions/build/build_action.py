from pathlib import Path
from typing import Dict, Any, Optional, Type
import logging
from ..action import Action
from ..action_context import ActionContext, ScopeActionContext
from .story_graph_data import StoryGraphData
from .story_graph_spec import StoryGraphSpec
from .story_graph_template import StoryGraphTemplate
from ...scope.action_scope import ActionScope
from ..validate.validate_action import ValidateRulesAction
logger = logging.getLogger(__name__)

class BuildStoryGraphAction(Action):
    context_class: Type[ActionContext] = ScopeActionContext

    def __init__(self, behavior=None, action_config=None):
        super().__init__(behavior=behavior, action_config=action_config)
        self._story_graph_data = StoryGraphData(self.behavior)

    @property
    def action_name(self) -> str:
        return 'build'

    @action_name.setter
    def action_name(self, value: str):
        raise AttributeError('action_name is read-only for BuildStoryGraphAction')

    @property
    def story_graph_data(self) -> Optional[StoryGraphData]:
        self._story_graph_data = StoryGraphData(self.behavior)
        return self._story_graph_data

    @property
    def story_graph_spec(self) -> Optional[StoryGraphSpec]:
        return self.story_graph_data.story_graph_spec

    @property
    def story_graph_template(self) -> Optional[StoryGraphTemplate]:
        return self.story_graph_data.story_graph_template

    @property
    def rules(self):
        return ValidateRulesAction(behavior=self.behavior, action_config=None)

    def _prepare_instructions(self, instructions, context: ScopeActionContext):
        instructions.update(self.story_graph_data.instructions)
        
        action_scope = ActionScope.from_context(context, self.behavior.bot_paths)
        instructions.set('scope', action_scope.scope)
        story_names = action_scope.get_story_names(self.story_graph_spec.story_graph.content)
        instructions.set('scope_story_names', list(story_names) if story_names else [])
        
        if self.story_graph_template:
            if self.story_graph_template.template_path:
                template_path_value = str(self.story_graph_template.template_path.resolve())
            elif self.story_graph_spec.template_filename:
                kg_dir = self.behavior.bot_paths.bot_directory / 'behaviors' / self.behavior.name / 'content' / 'story_graph'
                template_path_value = str((kg_dir / self.story_graph_spec.template_filename).resolve())
            else:
                template_path_value = None
            
            instructions.set('story_graph_template', {
                'template_path': template_path_value,
                'exists': self.story_graph_template.exists
            })
        if self.story_graph_spec.config_data:
            output_file_path = self.story_graph_spec.story_graph.path
            instructions.set('story_graph_config', {
                'output': self.story_graph_spec.output_filename,
                'path': str(output_file_path.parent),
                'template': self.story_graph_spec.template_filename
            })
        
        self._add_update_instructions(instructions)
        
        self._replace_schema_placeholders(instructions)
        
        self.inject_rules(instructions)
        
        self._replace_content_with_file_references(instructions)
    
    def do_execute(self, context: ScopeActionContext = None):
        result = self.get_instructions(context)
        return result

    def _add_update_instructions(self, instructions) -> None:
        file_exists = self.story_graph_spec.story_graph.path.exists()
        instructions.set('existing_file', {'path': str(self.story_graph_spec.story_graph.path), 'exists': file_exists})
        
        if file_exists:
            instructions.set('update_mode', True)
            instructions.set('update_instructions', {'mode': 'update_existing', 'message': f"**CRITICAL: Output file '{self.story_graph_spec.story_graph.path.name}' already exists. You MUST UPDATE this existing file by adding/modifying only the content needed for this behavior. DO NOT create a new file.**", 'existing_file_path': str(self.story_graph_spec.story_graph.path), 'preserve_existing': self._get_preserve_existing(self.story_graph_spec.story_graph), 'add_or_modify': self._determine_add_or_modify_content()})
        else:
            instructions.set('create_mode', True)
            instructions.set('create_instructions', {'mode': 'create_new', 'message': f"**CRITICAL: Output file '{self.story_graph_spec.story_graph.path.name}' does not exist. You MUST CREATE this file with the complete structure based on the provided template and rules.**", 'output_file_path': str(self.story_graph_spec.story_graph.path)})

    def _get_preserve_existing(self, story_graph) -> list:
        return [item for item in ['epics' if story_graph.has_epics else None, 'increments' if story_graph.has_increments else None, 'domain_concepts' if story_graph.has_domain_concepts else None] if item is not None]

    def _determine_add_or_modify_content(self) -> list:
        behavior_to_content = {'shape': [], 'prioritization': ['increments'], 'discovery': ['story refinements', 'increments', 'domain_concepts'], 'exploration': ['acceptance_criteria', 'domain_concepts'], 'scenarios': ['scenarios', 'domain_concepts'], 'tests': ['test_implementations', 'domain_concepts']}
        return behavior_to_content.get(self.behavior.name, [])
    
    def _replace_schema_placeholders(self, instructions) -> None:
        base_instructions = instructions.get('base_instructions', [])
        new_instructions = []
        
        template = self.story_graph_template
        description_lines_list = []
        schema_explanation_lines = []
        
        if template and template.exists:
            template_path = template.template_path
            if template_path:
                bot_dir = self.behavior.bot_paths.bot_directory
                try:
                    if template_path.is_absolute():
                        try:
                            rel_path = template_path.relative_to(bot_dir)
                            template_reference = f"{self.behavior.bot_name}/{str(rel_path).replace('\\', '/')}"
                        except ValueError:
                            template_reference = f"{self.behavior.bot_name}/behaviors/{self.behavior.name}/content/story_graph/{template_path.name}"
                    else:
                        template_reference = f"{self.behavior.bot_name}/{str(template_path).replace('\\', '/')}"
                except Exception:
                    template_reference = f"{self.behavior.bot_name}/behaviors/{self.behavior.name}/content/story_graph/{template_path.name if template_path else 'template.json'}"
            else:
                template_reference = f"{self.behavior.bot_name}/behaviors/{self.behavior.name}/content/story_graph/template.json"
            
            template_content = template.template_content
            if isinstance(template_content, dict) and '_explanation' in template_content:
                explanation = template_content['_explanation']
                if isinstance(explanation, dict):
                    for key, value in explanation.items():
                        if isinstance(value, str):
                            schema_explanation_lines.append(f"{key}: {value}")
                        else:
                            schema_explanation_lines.append(f"{key}: {str(value)}")
            
            output_filename = self.story_graph_spec.output_filename if self.story_graph_spec else 'story-graph.json'
            output_path = str(self.story_graph_spec.story_graph.path.parent) if self.story_graph_spec else ''
            
            description_lines_list = [
                f"Review the template file at `{template_reference}`. It shows the exact structure (fields, nesting, types) that your story graph output must follow during this behavior. Read this file to understand the required schema.",
                "",
                f"Create `{output_filename}` if it does not exist. Place file at `{output_path}/`. Using the template for guidance.",
                "",
                f"If the file already exists then make SAFE edits only. Preserve existing structure and content. Add or modify only what is necessary. Do NOT overwrite indiscriminately unless explicitly asked. When adding nodes to the graph follow the template and do not add extra elements that you might see in other nodes, they will be added as a part of later behaviors."
            ]
        
        for line in base_instructions:
            if isinstance(line, str):
                if '{{schema}}' in line:
                    if schema_explanation_lines:
                        new_instructions.extend(schema_explanation_lines)
                    else:
                        pass
                elif '{{description}}' in line:
                    if description_lines_list:
                        new_instructions.extend(description_lines_list)
                    else:
                        pass
                else:
                    new_instructions.append(line)
            else:
                new_instructions.append(line)
        
        instructions._data['base_instructions'] = new_instructions

    def inject_rules(self, instructions) -> None:
        validate_action = self.rules
        rules_obj = validate_action.rules
        rules_text = rules_obj.formatted_rules_digest()
        rules_data = validate_action.inject_behavior_specific_rules()
        all_rules = rules_data.get('validation_rules', [])
        
        existing_instructions = instructions.get('base_instructions', [])
        new_instructions = []
        rules_section = []
        
        schema_path = self.behavior.bot_paths.workspace_directory / 'docs' / 'stories' / 'story-graph.json'
        
        for line in existing_instructions:
            if isinstance(line, str):
                if '{{rules}}' in line:
                    continue
                if '{{schema}}' in line:
                    line = line.replace('{{schema}}', f'**Schema:** Story graph template at `{schema_path}`')
                if '{{description}}' in line:
                    line = line.replace('{{description}}', f'**Task:** Build {self.behavior.name} story graph from clarification and strategy data')
            new_instructions.append(line)
        
        if rules_text != 'No validation rules found.':
            rules_lines = rules_text.split('\n')
            rules_section.extend(rules_lines)
        
        if rules_section:
            while new_instructions and new_instructions[-1] == '':
                new_instructions.pop()
            new_instructions.append('')
            new_instructions.append('When building or adding to the story graph follow these rules,')
            new_instructions.extend(rules_section)
        
        instructions._data['base_instructions'] = new_instructions
        instructions.set('rules', all_rules)
    
    def _replace_content_with_file_references(self, instructions) -> None:
        bot_dir = self.behavior.bot_paths.bot_directory
        
        
        
        if 'rules' in instructions._data and instructions._data['rules']:
            all_rules = instructions._data['rules']
            rule_files = []
            bots_dir = self.behavior.bot_paths.python_workspace_root / 'agile_bots' / 'bots'
            
            for rule in all_rules:
                rule_path = None
                if isinstance(rule, dict):
                    rule_file = rule.get('rule_file', '')
                    if rule_file:
                        rule_path = str(bots_dir / rule_file)
                elif isinstance(rule, str):
                    rule_path = str(bots_dir / rule)
                
                if rule_path:
                    rule_files.append(rule_path)
            
            instructions._data['rules'] = rule_files
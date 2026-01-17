from typing import Dict, Any, Type
from actions.action import Action
from actions.action_context import ActionContext, RulesActionContext
from rules.rules import Rules
from rules.rules_digest_guidance import RulesDigestGuidance

class RulesAction(Action):
    context_class: Type[ActionContext] = RulesActionContext

    def do_execute(self, context: RulesActionContext) -> Dict[str, Any]:
        instructions = self.instructions.copy()
        rules = Rules(behavior=self.behavior, bot_paths=self.behavior.bot_paths)
        rules_digest = rules.formatted_rules_digest()
        rule_names = self._get_rule_names(rules)
        
        self._add_rules_list_to_display(instructions, rule_names, rules)
        self._add_user_message(instructions, context.message)
        self._add_rules_context(instructions, rules_digest, rule_names)
        
        return {
            'instructions': instructions.to_dict()
        }
    
    def _get_rule_names(self, rules: Rules) -> list:
        return [rule.name for rule in rules]
    
    def _add_rules_list_to_display(self, instructions, rule_names: list, rules: Rules) -> None:
        instructions.add_display("")
        instructions.add_display(f"## Rules Available ({len(rule_names)} total)")
        instructions.add_display("")
        rule_map = {rule.name: rule for rule in rules}
        for idx, rule_name in enumerate(rule_names, 1):
            rule = rule_map.get(rule_name)
            display_line = self._format_rule_display_line(idx, rule_name, rule)
            instructions.add_display(display_line)
        instructions.add_display("")
    
    def _format_rule_display_line(self, idx: int, rule_name: str, rule) -> str:
        if not rule:
            return f"{idx}. {rule_name}"
        
        if hasattr(rule, '_rule_file_path'):
            file_path = str(rule._rule_file_path).replace('\\', '/')
            return f"{idx}. {rule_name} ({file_path})"
        
        if hasattr(rule, 'rule_file'):
            return f"{idx}. {rule_name} ({rule.rule_file})"
        
        return f"{idx}. {rule_name}"
    
    def _add_user_message(self, instructions, message: str) -> None:
        if not message:
            return
        instructions.add("")
        instructions.add("**User Request:**")
        instructions.add(message)
        instructions.add("")
    
    def _add_rules_context(self, instructions, rules_digest: str, rule_names: list) -> None:
        instructions.add("")
        instructions.add(rules_digest)
        instructions.add("")
        RulesDigestGuidance().add_to(instructions)


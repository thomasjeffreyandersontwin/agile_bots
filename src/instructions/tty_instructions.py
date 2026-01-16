
from agile_bots.src.cli.adapters import TTYAdapter
from agile_bots.src.instructions.instructions import Instructions

class TTYInstructions(TTYAdapter):
    
    def __init__(self, instructions: Instructions):
        self.instructions = instructions
    
    def serialize(self) -> str:
        instructions_dict = self.instructions.to_dict()
        output_lines = []
        
        behavior_metadata = instructions_dict.get('behavior_metadata', {})
        if behavior_metadata:
            behavior_name = behavior_metadata.get('name', 'unknown')
            output_lines.append(f"{self.add_bold(f'Behavior Instructions - {behavior_name}')}")
            
            behavior_description = behavior_metadata.get('description', '')
            if behavior_description:
                output_lines.append(f"The purpose of this behavior is to {behavior_description.lower()}")
                output_lines.append("")
            
            behavior_instructions = behavior_metadata.get('instructions', [])
            if behavior_instructions:
                if isinstance(behavior_instructions, list):
                    output_lines.extend(behavior_instructions)
                elif isinstance(behavior_instructions, str):
                    output_lines.append(behavior_instructions)
                output_lines.append("")
        
        action_metadata = instructions_dict.get('action_metadata', {})
        if action_metadata:
            action_name = action_metadata.get('name', 'unknown')
            output_lines.append(f"{self.add_bold(f'Action Instructions - {action_name}')}")
            
            action_description = action_metadata.get('description', '')
            if action_description:
                output_lines.append(f"The purpose of this action is to {action_description.lower()}")
                output_lines.append("")
            
            action_instructions = action_metadata.get('instructions', [])
            if action_instructions:
                output_lines.extend(action_instructions)
                output_lines.append("")
        
        output_lines.append("---")
        output_lines.append("")
        
        base_instructions = instructions_dict.get('base_instructions', [])
        output_lines.extend(base_instructions)
        
        clarification_data = instructions_dict.get('clarification', {})
        guardrails_dict = instructions_dict.get('guardrails', {})
        
        saved_answers = {}
        saved_evidence_provided = {}
        if clarification_data:
            key_questions_data = clarification_data.get('key_questions', {})
            if isinstance(key_questions_data, dict):
                saved_answers = key_questions_data.get('answers', {})
            
            evidence_data = clarification_data.get('evidence', {})
            if isinstance(evidence_data, dict):
                saved_evidence_provided = evidence_data.get('provided', {})
        
        if saved_answers:
            output_lines.append("")
            output_lines.append(self.add_bold("Key Questions:"))
            for question, answer in saved_answers.items():
                output_lines.append(f"- {self.add_bold(f'{question}:')} {answer}")
        elif guardrails_dict:
            if hasattr(self.instructions, '_guardrails') and self.instructions._guardrails:
                from agile_bots.src.cli.adapter_factory import AdapterFactory
                guardrails_adapter = AdapterFactory.create(self.instructions._guardrails, 'tty')
                output_lines.append(guardrails_adapter.serialize())
            else:
                required_context = guardrails_dict.get('required_context', {})
                if required_context:
                    key_questions = required_context.get('key_questions', [])
                    if key_questions:
                        output_lines.append("")
                        output_lines.append(self.add_bold("Key Questions:"))
                        if isinstance(key_questions, list):
                            for question in key_questions:
                                output_lines.append(f"- {question}")
                        elif isinstance(key_questions, dict):
                            for question_key, question_text in key_questions.items():
                                output_lines.append(f"- {self.add_bold(f'{question_key}:')} {question_text}")
        
        if saved_evidence_provided:
            output_lines.append("")
            output_lines.append(self.add_bold("Evidence:"))
            for evidence_key, evidence_content in saved_evidence_provided.items():
                output_lines.append(f"- {self.add_bold(f'{evidence_key}:')} {evidence_content}")
        elif guardrails_dict and not hasattr(self.instructions, '_guardrails'):
            required_context = guardrails_dict.get('required_context', {})
            if required_context:
                evidence = required_context.get('evidence', [])
                if evidence:
                    output_lines.append("")
                    output_lines.append(self.add_bold("Evidence:"))
                    if isinstance(evidence, list):
                        output_lines.append(', '.join(evidence))
                    elif isinstance(evidence, dict):
                        for evidence_key, evidence_desc in evidence.items():
                            output_lines.append(f"- {self.add_bold(f'{evidence_key}:')} {evidence_desc}")
        
        
        strategy_criteria = instructions_dict.get('strategy_criteria', {})
        strategy_data = instructions_dict.get('strategy', {})
        assumptions = instructions_dict.get('assumptions', {})
        
        if strategy_data and 'strategy_criteria' in strategy_data:
            strategy_criteria = strategy_criteria or strategy_data['strategy_criteria']
        
        saved_decisions = {}
        if strategy_criteria:
            saved_decisions = strategy_criteria.get('decisions', {}) or strategy_criteria.get('decisions_made', {})
        
        if strategy_data and 'assumptions' in strategy_data:
            assumptions = assumptions or strategy_data['assumptions']
        
        saved_assumptions = []
        if isinstance(assumptions, dict):
            saved_assumptions = assumptions.get('assumptions', []) or assumptions.get('assumptions_made', [])
        elif isinstance(assumptions, list):
            saved_assumptions = assumptions
        
        if hasattr(self.instructions, '_strategy') and self.instructions._strategy:
            from agile_bots.src.cli.adapter_factory import AdapterFactory
            strategy_adapter = AdapterFactory.create(self.instructions._strategy, 'tty')
            output_lines.append(strategy_adapter.serialize())
        elif saved_decisions or saved_assumptions or strategy_criteria or assumptions:
            
            if saved_decisions:
                output_lines.append("")
                output_lines.append(self.add_bold("Decisions:"))
                output_lines.append(self.add_bold("Your Decisions:"))
                for decision_key, decision_value in saved_decisions.items():
                    output_lines.append("")
                    output_lines.append(f"{self.add_bold(f'{decision_key}:')}")
                    if isinstance(decision_value, list):
                        for item in decision_value:
                            output_lines.append(f"  - {item}")
                    else:
                        output_lines.append(f"  {decision_value}")
            elif strategy_criteria:
                output_lines.append("")
                output_lines.append(self.add_bold("Decisions:"))
                
                criteria_template = strategy_criteria.get('criteria', {})
                if criteria_template:
                    for criteria_key, criteria_data in criteria_template.items():
                        output_lines.append("")
                        question = criteria_data.get('question', '')
                        if question:
                            output_lines.append(f"{self.add_bold(f'{criteria_key}:')} {question}")
                        else:
                            output_lines.append(self.add_bold(f"{criteria_key}:"))
                        
                        selected_value = saved_decisions.get(criteria_key) if saved_decisions else None
                        
                        options = criteria_data.get('options', [])
                        if options:
                            for option in options:
                                output_lines.extend(self._format_strategy_option(option, selected_value))
            
            if saved_assumptions:
                output_lines.append("")
                output_lines.append(self.add_bold("Assumptions:"))
                output_lines.append(self.add_bold("Your Assumptions:"))
                for assumption in saved_assumptions:
                    output_lines.append(f"- {assumption}")
            elif isinstance(assumptions, dict):
                typical_assumptions = assumptions.get('typical_assumptions', [])
                if typical_assumptions:
                    output_lines.append("")
                    output_lines.append(self.add_bold("Assumptions:"))
                    for assumption in typical_assumptions:
                        output_lines.append(f"- {assumption}")
        
        display_content = instructions_dict.get('display_content', [])
        if display_content:
            output_lines.append("")
            output_lines.extend(display_content)
        
        return "\n".join(output_lines)
    
    def _format_strategy_option(self, option, selected_value=None) -> list:
        lines = []
        option_text = option if isinstance(option, str) else option.get('description', option.get('name', ''))
        
        is_selected = False
        if selected_value:
            if isinstance(selected_value, list):
                is_selected = option_text in selected_value
            else:
                is_selected = option_text == selected_value or option_text.startswith(selected_value.split(' – ')[0])
        
        if isinstance(option, dict):
            name = option.get('name', '')
            description = option.get('description', '')
            if name:
                marker = "  ✓ " if is_selected else "  - "
                lines.append(f"{marker}{self.add_bold(name) if is_selected else name}")
                if description:
                    lines.append(f"    {description}")
            elif description:
                marker = "  ✓ " if is_selected else "  - "
                lines.append(f"{marker}{self.add_bold(description) if is_selected else description}")
        elif isinstance(option, str):
            marker = "  ✓ " if is_selected else "  - "
            lines.append(f"{marker}{self.add_bold(option) if is_selected else option}")
        return lines
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        parts = text.split(maxsplit=1)
        verb = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""
        return verb, args

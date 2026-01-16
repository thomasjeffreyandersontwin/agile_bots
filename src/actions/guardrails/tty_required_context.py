
from agile_bots.src.cli.adapters import TTYAdapter

class TTYRequiredContext(TTYAdapter):
    
    def __init__(self, required_context):
        self.required_context = required_context
    
    def serialize(self) -> str:
        lines = []
        
        key_questions = self.required_context.key_questions.questions
        if key_questions:
            lines.append("")
            lines.append(self.add_bold("Key Questions:"))
            if isinstance(key_questions, list):
                for question in key_questions:
                    lines.append(f"- {question}")
            elif isinstance(key_questions, dict):
                for question_key, question_text in key_questions.items():
                    lines.append(f"- {self.add_bold(f'{question_key}:')} {question_text}")
        
        evidence_list = self.required_context.evidence.evidence_list
        if evidence_list:
            lines.append("")
            lines.append(self.add_bold("Evidence:"))
            if isinstance(evidence_list, list):
                # Show as comma-delimited list
                lines.append(', '.join(evidence_list))
            elif isinstance(evidence_list, dict):
                for evidence_key, evidence_desc in evidence_list.items():
                    lines.append(f"- {self.add_bold(f'{evidence_key}:')} {evidence_desc}")
        
        return '\n'.join(lines)
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        parts = text.split(maxsplit=1)
        verb = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""
        return verb, args

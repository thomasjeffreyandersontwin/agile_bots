
from pathlib import Path
from cli.adapters import MarkdownAdapter
from scope.scope import Scope

class MarkdownScope(MarkdownAdapter):
    
    def __init__(self, scope: Scope, workspace_directory: Path = None):
        self.scope = scope
        self.workspace_directory = workspace_directory or Path.cwd()
    
    def serialize(self) -> str:
        lines = []
        
        lines.append(self.format_header(2, "🎯 Scope"))
        lines.append("")
        
        if self.scope.type.value == 'all':
            filter_display = "all (entire project)"
        else:
            filter_display = ', '.join(self.scope.value) if isinstance(self.scope.value, list) else str(self.scope.value) if self.scope.value else "all"
        
        lines.append(f"**🎯 Current Scope:** {filter_display}")
        lines.append("")
        
        results = self.scope.results
        
        if results is None:
            lines.append("(no scope set)")
        else:
            self._add_results_to_lines(lines, results)
        
        lines.append("")
        lines.append("To change scope (pick ONE - setting a new scope replaces the previous):")
        lines.append(self.format_list_item("`scope all` - Clear scope, work on entire project"))
        lines.append(self.format_list_item("`scope \"Story Name\"` - Filter by story (replaces any file scope)"))
        lines.append(self.format_list_item("`scope \"file:C:/path/to/**/*.py\"` - Filter by files (replaces any story scope)"))
        lines.append("")
        lines.append("---")
        lines.append("")
        
        return ''.join(lines)
    
    
    def _add_results_to_lines(self, lines: list, results) -> None:
        from story_graph.story_graph import StoryGraph
        
        if isinstance(results, StoryGraph):
            from cli.adapter_factory import AdapterFactory
            story_graph_adapter = AdapterFactory.create(results, 'markdown')
            lines.append(story_graph_adapter.serialize())
            return
        
        if isinstance(results, list):
            if results:
                for file_path in sorted(results):
                    formatted_path = self._format_file_path(file_path)
                    lines.append(self.format_list_item(formatted_path))
            else:
                lines.append("(no files found)")
    
    def _format_file_path(self, file_path: Path) -> str:
        try:
            rel_path = file_path.relative_to(self.scope.workspace_directory)
            return str(rel_path)
        except ValueError:
            return str(file_path)
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from utils import parse_command_text
        return parse_command_text(text)


from cli.adapters import MarkdownAdapter
from story_graph.story_graph import StoryGraph

class MarkdownStoryGraph(MarkdownAdapter):
    
    def __init__(self, story_graph: StoryGraph):
        self.story_graph = story_graph
    
    def serialize(self) -> str:
        lines = []
        
        lines.append(self.format_header(2, "Story Graph"))
        lines.append("")
        
        lines.append(f"**Path:** `{self.story_graph.path}`")
        lines.append("")
        lines.append(f"**Epic Count:** {self.story_graph.epic_count}")
        lines.append("")
        
        features = []
        if self.story_graph.has_increments:
            features.append("Increments")
        if self.story_graph.has_domain_concepts:
            features.append("Domain Concepts")
        
        if features:
            lines.append(f"**Features:** {', '.join(features)}")
            lines.append("")
        
        content = self.story_graph.content
        if content and 'epics' in content:
            lines.append(self.format_header(3, "Epics"))
            lines.append("")
            
            for epic in content['epics']:
                epic_name = epic.get('name', 'Unknown')
                lines.append(f"- 🎯  **{epic_name}**")
                
                for sub_epic in epic.get('sub_epics', []):
                    self._render_sub_epic(sub_epic, lines, indent_level=1)
                
                lines.append("")
        
        return ''.join(lines)
    
    def _render_sub_epic(self, sub_epic: dict, lines: list, indent_level: int):
        sub_epic_name = sub_epic.get('name', 'Unknown')
        indent = "  " * (indent_level + 1)
        lines.append(f"{indent}- ⚙️  {sub_epic_name}")
        
        for story_group in sub_epic.get('story_groups', []):
            for story in story_group.get('stories', []):
                self._render_story(story, lines, indent_level + 2)
        
        # Render nested sub-epics
        for nested_sub_epic in sub_epic.get('sub_epics', []):
            self._render_sub_epic(nested_sub_epic, lines, indent_level + 1)
    
    def _render_story(self, story: dict, lines: list, indent_level: int):
        story_name = story.get('name', 'Unknown')
        story_indent = "  " * indent_level
        lines.append(f"{story_indent}- 📝  {story_name}")
        
        # Render scenarios if they exist
        scenarios = story.get('scenarios', [])
        if scenarios:
            scenario_indent = "  " * (indent_level + 1)
            for scenario in scenarios:
                scenario_name = scenario.get('name', 'Unknown')
                lines.append(f"{scenario_indent}- 🎬  {scenario_name}")
    
    
    def parse_command_text(self, text: str) -> tuple[str, str]:
        from utils import parse_command_text
        return parse_command_text(text)

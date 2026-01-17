
from typing import List, Dict, Any, Optional, Iterator, Union

class StoryNode:
    
    def __init__(self, data: Dict[str, Any], epic_idx: int, sub_epic_path: Optional[List[int]] = None, 
                 story_group_idx: Optional[int] = None, story_idx: Optional[int] = None):
        self.data = data
        self.epic_idx = epic_idx
        self.sub_epic_path = sub_epic_path or []
        self.story_group_idx = story_group_idx
        self.story_idx = story_idx
        self._new_node: Optional[NewStoryNode] = None
    
    @property
    def children(self) -> List['StoryNode']:
        return []
    
    @property
    def name(self) -> str:
        return self.data.get('name', '')
    
    def map_location(self, field: str = 'name') -> str:
        if isinstance(self, Epic):
            return f"epics[{self.epic_idx}].{field}"
        elif isinstance(self, SubEpic):
            if self.sub_epic_path:
                path_str = "".join([f".sub_epics[{idx}]" for idx in self.sub_epic_path])
                return f"epics[{self.epic_idx}]{path_str}.{field}"
            else:
                return f"epics[{self.epic_idx}].{field}"
        elif isinstance(self, Story):
            path_parts = [f"epics[{self.epic_idx}]"]
            if self.sub_epic_path:
                for idx in self.sub_epic_path:
                    path_parts.append(f"sub_epics[{idx}]")
            if self.story_group_idx is not None:
                path_parts.append(f"story_groups[{self.story_group_idx}]")
            path_parts.append(f"stories[{self.story_idx}]")
            path_parts.append(field)
            return ".".join(path_parts)
        return ""

class Epic(StoryNode):
    
    @property
    def children(self) -> List[StoryNode]:
        children = []
        
        sub_epics = self.data.get('sub_epics', [])
        for sub_epic_idx, sub_epic_data in enumerate(sub_epics):
            sub_epic = SubEpic(sub_epic_data, self.epic_idx, [sub_epic_idx])
            children.append(sub_epic)
        
        story_groups = self.data.get('story_groups', [])
        for story_group_idx, story_group_data in enumerate(story_groups):
            story_group = StoryGroup(story_group_data, self.epic_idx, None, story_group_idx)
            children.append(story_group)
        
        return children

    @property
    def all_stories(self) -> List['Story']:
        stories: List['Story'] = []

        def _collect(node: StoryNode):
            if isinstance(node, Story):
                stories.append(node)
            for child in node.children:
                _collect(child)

        _collect(self)
        return stories

class SubEpic(StoryNode):
    
    @property
    def children(self) -> List[StoryNode]:
        children = []
        
        nested_sub_epics = self.data.get('sub_epics', [])
        for nested_sub_epic_idx, nested_sub_epic_data in enumerate(nested_sub_epics):
            nested_sub_epic_path = self.sub_epic_path + [nested_sub_epic_idx]
            nested_sub_epic = SubEpic(nested_sub_epic_data, self.epic_idx, nested_sub_epic_path)
            children.append(nested_sub_epic)
        
        story_groups = self.data.get('story_groups', [])
        for story_group_idx, story_group_data in enumerate(story_groups):
            story_group = StoryGroup(story_group_data, self.epic_idx, self.sub_epic_path, story_group_idx)
            children.append(story_group)
        
        return children

class StoryGroup(StoryNode):
    
    @property
    def children(self) -> List[StoryNode]:
        children = []
        stories = self.data.get('stories', [])
        
        for story_idx, story_data in enumerate(stories):
            story = Story(story_data, self.epic_idx, self.sub_epic_path, self.story_group_idx, story_idx)
            children.append(story)
        
        return children

class ScenarioBase:
    
    @property
    def steps(self) -> List[str]:
        steps_value = self.data.get('steps', '')
        if isinstance(steps_value, str):
            return [s.strip() for s in steps_value.split('\n') if s.strip()]
        return steps_value if isinstance(steps_value, list) else []
    
    @property
    def default_test_method(self) -> str:
        scenario_name = self.name
        if not scenario_name:
            return ""
        words = scenario_name.split()
        method_name = "_".join(word.lower() for word in words)
        return f"test_{method_name}"

class Scenario(ScenarioBase):
    
    def __init__(self, data: Dict[str, Any], story: 'Story', scenario_idx: int):
        self.data = data
        self.story = story
        self.scenario_idx = scenario_idx
    
    @property
    def name(self) -> str:
        return self.data.get('name', '')
    
    @property
    def type(self) -> str:
        return self.data.get('type', '')
    
    @property
    def background(self) -> List[str]:
        return self.data.get('background', [])
    
    @property
    def test_method(self) -> Optional[str]:
        return self.data.get('test_method')
    
    def map_location(self, field: str = 'name') -> str:
        story_location = self.story.map_location('scenarios')
        return f"{story_location}[{self.scenario_idx}].{field}"

class ScenarioOutline(ScenarioBase):
    
    def __init__(self, data: Dict[str, Any], story: 'Story', scenario_outline_idx: int):
        self.data = data
        self.story = story
        self.scenario_outline_idx = scenario_outline_idx
    
    @property
    def name(self) -> str:
        return self.data.get('name', '')
    
    @property
    def type(self) -> str:
        return self.data.get('type', '')
    
    @property
    def background(self) -> List[str]:
        return self.data.get('background', [])
    
    @property
    def examples(self) -> Dict[str, Any]:
        return self.data.get('examples', {})
    
    @property
    def examples_columns(self) -> List[str]:
        return self.examples.get('columns', [])
    
    @property
    def examples_rows(self) -> List[List[str]]:
        return self.examples.get('rows', [])
    
    @property
    def test_method(self) -> Optional[str]:
        return self.data.get('test_method')
    
    def map_location(self, field: str = 'name') -> str:
        story_location = self.story.map_location('scenario_outlines')
        return f"{story_location}[{self.scenario_outline_idx}].{field}"

class Story(StoryNode):
    
    @property
    def sizing(self) -> Any:
        return self.data.get('sizing')
    
    @property
    def users(self) -> List[str]:
        return self.data.get('users', [])
    
    @property
    def story_type(self) -> str:
        return self.data.get('story_type', '')
    
    @property
    def connector(self) -> Optional[str]:
        return self.data.get('connector')
    
    @property
    def sequential_order(self) -> int:
        return self.data.get('sequential_order', 0)
    
    @property
    def scenarios(self) -> List[Scenario]:
        scenarios_data = self.data.get('scenarios', [])
        return [Scenario(scenario_data, self, scenario_idx) 
                for scenario_idx, scenario_data in enumerate(scenarios_data)]
    
    @property
    def scenario_outlines(self) -> List[ScenarioOutline]:
        scenario_outlines_data = self.data.get('scenario_outlines', [])
        return [ScenarioOutline(scenario_outline_data, self, scenario_outline_idx)
                for scenario_outline_idx, scenario_outline_data in enumerate(scenario_outlines_data)]
    
    @property
    def test_class(self) -> Optional[str]:
        return self.data.get('test_class')
    
    @property
    def default_test_class(self) -> str:
        name = self.name
        if not name:
            return ""
        words = name.split()
        class_name = "".join(word.capitalize() for word in words)
        return f"Test{class_name}"

class StoryMap:
    
    def __init__(self, story_graph: Dict[str, Any]):
        self.story_graph = story_graph
    
    @classmethod
    def from_bot(cls, bot: Any) -> 'StoryMap':
        from pathlib import Path
        import json
        
        if hasattr(bot, 'bot_paths') and hasattr(bot.bot_paths, 'bot_directory'):
            bot_directory = Path(bot.bot_paths.bot_directory)
        elif hasattr(bot, 'bot_directory'):
            bot_directory = Path(bot.bot_directory)
        elif isinstance(bot, (str, Path)):
            bot_directory = Path(bot)
        else:
            raise TypeError(f"Expected bot with bot_paths.bot_directory, bot_directory attribute, or Path/str, got {type(bot)}")
        
        story_graph_path = bot_directory / 'docs' / 'stories' / 'story-graph.json'
        
        if not story_graph_path.exists():
            raise FileNotFoundError(f"Story graph not found at {story_graph_path}")
        
        with open(story_graph_path, 'r', encoding='utf-8') as f:
            story_graph = json.load(f)
        
        return cls(story_graph)
    
    def epics(self) -> List[Epic]:
        epics_data = self.story_graph.get('epics', [])
        return [Epic(epic_data, epic_idx) for epic_idx, epic_data in enumerate(epics_data)]
    
    def find_epic_by_name(self, epic_name: str) -> 'Epic':
        for epic in self.epics():
            if epic.name == epic_name:
                return epic
        return None
    
    def walk(self, node: StoryNode) -> Iterator[StoryNode]:
        yield node
        for child in node.children:
            yield from self.walk(child)

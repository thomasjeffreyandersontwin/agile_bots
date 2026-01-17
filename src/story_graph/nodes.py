from abc import ABC, abstractmethod
from typing import List, Iterator, Optional, Dict, Any, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from pathlib import Path
import json
from story_graph.domain import DomainConcept, StoryUser

@dataclass
class StoryNode(ABC):
    name: str
    sequential_order: Optional[float] = None

    def __post_init__(self):
        self._children: List['StoryNode'] = []

    @property
    @abstractmethod
    def children(self) -> List['StoryNode']:
        pass

    def __iter__(self) -> Iterator['StoryNode']:
        return iter(self.children)

    def __repr__(self) -> str:
        order = f', order={self.sequential_order}' if self.sequential_order is not None else ''
        return f"{self.__class__.__name__}(name='{self.name}'{order})"

    @staticmethod
    def _parse_steps_from_data(steps_value: Any) -> List[str]:
        if isinstance(steps_value, str):
            return [s.strip() for s in steps_value.split('\n') if s.strip()]
        elif isinstance(steps_value, list):
            return steps_value
        else:
            return []

    @staticmethod
    def _add_steps_to_node(node: 'StoryNode', step_strings: List[str]) -> None:
        for step_idx, step_text in enumerate(step_strings):
            step = Step(name=step_text, text=step_text, sequential_order=float(step_idx + 1), _parent=node)
            node._children.append(step)

    @staticmethod
    def _generate_default_test_method_name(name: str) -> str:
        if not name:
            return ''
        words = name.split()
        method_name = '_'.join((word.lower() for word in words))
        return f'test_{method_name}'

    def _filter_children_by_type(self, target_type: type) -> List['StoryNode']:
        return [child for child in self._children if isinstance(child, target_type)]

@dataclass
class Epic(StoryNode):
    domain_concepts: Optional[List[DomainConcept]] = None

    def __post_init__(self):
        super().__post_init__()
        if self.sequential_order is not None:
            self.sequential_order = None
        if self.domain_concepts is None:
            self.domain_concepts = []
        self._children: List['StoryNode'] = []

    @property
    def children(self) -> List['StoryNode']:
        return self._children

    @property
    def all_stories(self) -> List['Story']:
        stories = []
        for child in self.children:
            if isinstance(child, Story):
                stories.append(child)
            elif isinstance(child, (SubEpic, StoryGroup)):
                stories.extend(self._get_stories_from_node(child))
        return stories

    def _get_stories_from_node(self, node: StoryNode) -> List['Story']:
        stories = []
        for child in node.children:
            if isinstance(child, Story):
                stories.append(child)
            elif hasattr(child, 'children'):
                stories.extend(self._get_stories_from_node(child))
        return stories

    def find_sub_epic_by_name(self, sub_epic_name: str) -> Optional['SubEpic']:
        for child in self.children:
            if isinstance(child, SubEpic) and child.name == sub_epic_name:
                return child
        return None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Epic':
        domain_concepts = [DomainConcept.from_dict(dc) for dc in data.get('domain_concepts', [])]
        epic = cls(name=data.get('name', ''), domain_concepts=domain_concepts)
        for sub_epic_data in data.get('sub_epics', []):
            sub_epic = SubEpic.from_dict(sub_epic_data, parent=epic)
            epic._children.append(sub_epic)
        for story_group_data in data.get('story_groups', []):
            story_group = StoryGroup.from_dict(story_group_data, parent=epic)
            epic._children.append(story_group)
        return epic

@dataclass
class SubEpic(StoryNode):
    sequential_order: float
    _parent: Optional[StoryNode] = field(default=None, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if self.sequential_order is None:
            raise ValueError('SubEpic requires sequential_order')
        self._children: List['StoryNode'] = []

    @property
    def children(self) -> List['StoryNode']:
        return self._children

    @classmethod
    def from_dict(cls, data: Dict[str, Any], parent: Optional[StoryNode]=None) -> 'SubEpic':
        sequential_order = data.get('sequential_order')
        if sequential_order is None:
            raise ValueError('SubEpic requires sequential_order')
        sub_epic = cls(name=data.get('name', ''), sequential_order=float(sequential_order), _parent=parent)
        for nested_sub_epic_data in data.get('sub_epics', []):
            nested_sub_epic = SubEpic.from_dict(nested_sub_epic_data, parent=sub_epic)
            sub_epic._children.append(nested_sub_epic)
        for story_group_data in data.get('story_groups', []):
            story_group = StoryGroup.from_dict(story_group_data, parent=sub_epic)
            sub_epic._children.append(story_group)
        return sub_epic

@dataclass
class StoryGroup(StoryNode):
    sequential_order: float
    group_type: str = 'and'
    connector: Optional[str] = None
    _parent: Optional[StoryNode] = field(default=None, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if self.sequential_order is None:
            raise ValueError('StoryGroup requires sequential_order')
        self._children: List['StoryNode'] = []

    @property
    def children(self) -> List['StoryNode']:
        return self._children

    @classmethod
    def from_dict(cls, data: Dict[str, Any], parent: Optional[StoryNode]=None) -> 'StoryGroup':
        sequential_order = data.get('sequential_order', 1.0)
        story_group = cls(name=data.get('name', ''), sequential_order=float(sequential_order), group_type=data.get('type', 'and'), connector=data.get('connector'), _parent=parent)
        for story_data in data.get('stories', []):
            story = Story.from_dict(story_data, parent=story_group)
            story_group._children.append(story)
        return story_group

@dataclass
class Story(StoryNode):
    sequential_order: float
    connector: Optional[str] = None
    story_type: str = 'user'
    users: Optional[List[StoryUser]] = None
    test_file: Optional[str] = None
    test_class: Optional[str] = None
    _parent: Optional[StoryNode] = field(default=None, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if self.sequential_order is None:
            raise ValueError('Story requires sequential_order')
        if self.users is None:
            self.users = []
        self._children: List['StoryNode'] = []

    @property
    def children(self) -> List['StoryNode']:
        return self._children

    @property
    def scenarios(self) -> List['Scenario']:
        return [child for child in self._children if isinstance(child, Scenario)]

    @property
    def scenario_outlines(self) -> List['ScenarioOutline']:
        return [child for child in self._children if isinstance(child, ScenarioOutline)]

    @property
    def acceptance_criteria(self) -> List['AcceptanceCriteria']:
        return [child for child in self._children if isinstance(child, AcceptanceCriteria)]

    @property
    def default_test_class(self) -> str:
        if not self.name:
            return ''
        words = self.name.split()
        class_name = ''.join((word.capitalize() for word in words))
        return f'Test{class_name}'

    @classmethod
    def from_dict(cls, data: Dict[str, Any], parent: Optional[StoryNode]=None) -> 'Story':
        sequential_order = data.get('sequential_order')
        if sequential_order is None:
            raise ValueError('Story requires sequential_order')
        users = [StoryUser.from_str(u) for u in data.get('users', [])]
        story = cls(name=data.get('name', ''), sequential_order=float(sequential_order), connector=data.get('connector'), story_type=data.get('story_type', 'user'), users=users, test_file=data.get('test_file'), test_class=data.get('test_class'), _parent=parent)
        acceptance_criteria_data = data.get('acceptance_criteria', [])
        for idx, ac_data in enumerate(acceptance_criteria_data):
            ac = AcceptanceCriteria.from_dict(ac_data, index=idx, parent=story)
            story._children.append(ac)
        scenarios_data = data.get('scenarios', [])
        for idx, scenario_data in enumerate(scenarios_data):
            scenario = Scenario.from_dict(scenario_data, index=idx, parent=story)
            story._children.append(scenario)
        scenario_outlines_data = data.get('scenario_outlines', [])
        for idx, scenario_outline_data in enumerate(scenario_outlines_data):
            scenario_outline = ScenarioOutline.from_dict(scenario_outline_data, index=idx, parent=story)
            story._children.append(scenario_outline)
        return story

@dataclass
class Scenario(StoryNode):
    sequential_order: float
    type: str = ''
    background: List[str] = field(default_factory=list)
    test_method: Optional[str] = None
    _parent: Optional[StoryNode] = field(default=None, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if self.sequential_order is None:
            raise ValueError('Scenario requires sequential_order')
        self._children: List['StoryNode'] = []

    @property
    def children(self) -> List['StoryNode']:
        return self._children

    @property
    def steps(self) -> List['Step']:
        return self._filter_children_by_type(Step)

    @property
    def default_test_method(self) -> str:
        return StoryNode._generate_default_test_method_name(self.name)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], index: int=0, parent: Optional[StoryNode]=None) -> 'Scenario':
        sequential_order = float(data.get('sequential_order', index + 1))
        scenario = cls(name=data.get('name', ''), sequential_order=sequential_order, type=data.get('type', ''), background=data.get('background', []), test_method=data.get('test_method'), _parent=parent)
        cls._add_steps_to_node(scenario, cls._parse_steps_from_data(data.get('steps', '')))
        return scenario

@dataclass
class ScenarioOutline(StoryNode):
    sequential_order: float
    type: str = ''
    background: List[str] = field(default_factory=list)
    examples: Dict[str, Any] = field(default_factory=dict)
    test_method: Optional[str] = None
    _parent: Optional[StoryNode] = field(default=None, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if self.sequential_order is None:
            raise ValueError('ScenarioOutline requires sequential_order')
        self._children: List['StoryNode'] = []

    @property
    def children(self) -> List['StoryNode']:
        return self._children

    @property
    def steps(self) -> List['Step']:
        return self._filter_children_by_type(Step)

    @property
    def examples_columns(self) -> List[str]:
        return self.examples.get('columns', [])

    @property
    def examples_rows(self) -> List[List[str]]:
        return self.examples.get('rows', [])

    @property
    def default_test_method(self) -> str:
        return StoryNode._generate_default_test_method_name(self.name)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], index: int=0, parent: Optional[StoryNode]=None) -> 'ScenarioOutline':
        sequential_order = float(data.get('sequential_order', index + 1))
        scenario_outline = cls(name=data.get('name', ''), sequential_order=sequential_order, type=data.get('type', ''), background=data.get('background', []), examples=data.get('examples', {}), test_method=data.get('test_method'), _parent=parent)
        cls._add_steps_to_node(scenario_outline, cls._parse_steps_from_data(data.get('steps', '')))
        return scenario_outline

@dataclass
class AcceptanceCriteria(StoryNode):
    text: str = ''
    sequential_order: float = 0.0
    _parent: Optional[StoryNode] = field(default=None, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if self.sequential_order is None:
            raise ValueError('AcceptanceCriteria requires sequential_order')

    @property
    def children(self) -> List['StoryNode']:
        return []

    @classmethod
    def from_dict(cls, data: Union[str, Dict[str, Any]], index: int=0, parent: Optional[StoryNode]=None) -> 'AcceptanceCriteria':
        if isinstance(data, str):
            text = data
            sequential_order = float(index + 1)
        else:
            text = data.get('description', data.get('text', ''))
            sequential_order = float(data.get('sequential_order', index + 1))
        return cls(name=text, text=text, sequential_order=sequential_order, _parent=parent)

@dataclass
class Step(StoryNode):
    text: str = ''
    sequential_order: float = 0.0
    _parent: Optional[StoryNode] = field(default=None, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if self.sequential_order is None:
            raise ValueError('Step requires sequential_order')

    @property
    def children(self) -> List['StoryNode']:
        return []

class StoryMap:

    def __init__(self, story_graph: Dict[str, Any]):
        self.story_graph = story_graph
        self._epics: List[Epic] = []
        for epic_data in story_graph.get('epics', []):
            self._epics.append(Epic.from_dict(epic_data))

    @classmethod
    def from_bot(cls, bot: Any) -> 'StoryMap':
        if hasattr(bot, 'bot_paths') and hasattr(bot.bot_paths, 'bot_directory'):
            bot_directory = Path(bot.bot_paths.bot_directory)
        elif hasattr(bot, 'bot_directory'):
            bot_directory = Path(bot.bot_directory)
        elif isinstance(bot, (str, Path)):
            bot_directory = Path(bot)
        else:
            raise TypeError(f'Expected bot with bot_paths.bot_directory, bot_directory attribute, or Path/str, got {type(bot)}')
        story_graph_path = bot_directory / 'docs' / 'stories' / 'story-graph.json'
        if not story_graph_path.exists():
            raise FileNotFoundError(f'Story graph not found at {story_graph_path}')
        with open(story_graph_path, 'r', encoding='utf-8') as f:
            story_graph = json.load(f)
        return cls(story_graph)

    @property
    def epics(self) -> List[Epic]:
        return self._epics

    def walk(self, node: StoryNode) -> Iterator[StoryNode]:
        yield node
        for child in node.children:
            yield from self.walk(child)

    @property
    def all_stories(self) -> List['Story']:
        stories = []
        for epic in self._epics:
            for node in self.walk(epic):
                if isinstance(node, Story):
                    stories.append(node)
        return stories

    @property
    def all_scenarios(self) -> List['Scenario']:
        scenarios = []
        for epic in self._epics:
            for node in self.walk(epic):
                if isinstance(node, Story):
                    scenarios.extend(node.scenarios)
        return scenarios

    @property
    def all_domain_concepts(self) -> List[DomainConcept]:
        concepts = []
        for epic in self._epics:
            if epic.domain_concepts:
                concepts.extend(epic.domain_concepts)
        return concepts

    def filter_by_epic_names(self, epic_names: set) -> 'StoryMap':
        filtered_epics = [e for e in self._epics if e.name in epic_names]
        filtered_graph = {'epics': [self._epic_to_dict(e) for e in filtered_epics]}
        return StoryMap(filtered_graph)

    def filter_by_story_names(self, story_names: set) -> List['Story']:
        stories = []
        for epic in self._epics:
            for node in self.walk(epic):
                if isinstance(node, Story) and node.name in story_names:
                    stories.append(node)
        return stories

    def find_epic_by_name(self, epic_name: str) -> Optional[Epic]:
        for epic in self._epics:
            if epic.name == epic_name:
                return epic
        return None

    def find_story_by_name(self, story_name: str) -> Optional['Story']:
        for epic in self._epics:
            for node in self.walk(epic):
                if isinstance(node, Story) and node.name == story_name:
                    return node
        return None

    def _epic_to_dict(self, epic: Epic) -> Dict[str, Any]:
        return {
            'name': epic.name,
            'domain_concepts': [dc.__dict__ for dc in epic.domain_concepts] if epic.domain_concepts else [],
            'sub_epics': [self._sub_epic_to_dict(child) for child in epic.children if isinstance(child, SubEpic)],
            'story_groups': [self._story_group_to_dict(child) for child in epic.children if isinstance(child, StoryGroup)]
        }

    def _sub_epic_to_dict(self, sub_epic: SubEpic) -> Dict[str, Any]:
        return {
            'name': sub_epic.name,
            'sequential_order': sub_epic.sequential_order,
            'sub_epics': [self._sub_epic_to_dict(child) for child in sub_epic.children if isinstance(child, SubEpic)],
            'story_groups': [self._story_group_to_dict(child) for child in sub_epic.children if isinstance(child, StoryGroup)]
        }

    def _story_group_to_dict(self, story_group: StoryGroup) -> Dict[str, Any]:
        return {
            'name': story_group.name,
            'sequential_order': story_group.sequential_order,
            'type': story_group.group_type,
            'connector': story_group.connector,
            'stories': [self._story_to_dict(child) for child in story_group.children if isinstance(child, Story)]
        }

    def _story_to_dict(self, story: Story) -> Dict[str, Any]:
        return {
            'name': story.name,
            'sequential_order': story.sequential_order,
            'connector': story.connector,
            'story_type': story.story_type,
            'users': [str(u) for u in story.users] if story.users else [],
            'test_file': story.test_file,
            'test_class': story.test_class
        }
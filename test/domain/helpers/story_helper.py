"""
Story Test Helper
Handles story graph, story map, epics, scenarios testing
"""
import json
from pathlib import Path
from .base_helper import BaseHelper


class StoryTestHelper(BaseHelper):
    """Helper for story graph and story map testing"""
    
    def create_story_graph(self, graph_data: dict = None, docs_path: str = 'docs/stories', filename: str = 'story-graph.json') -> Path:
        """Create test story-graph.json in workspace.
        
        Args:
            graph_data: Story graph dict (default: {'epics': []})
            docs_path: Relative path from workspace to docs directory
            filename: Story graph filename
        
        Returns:
            Path to created story graph file
        """
        if graph_data is None:
            graph_data = {'epics': []}
        
        docs_dir = self.parent.workspace / docs_path
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        story_graph_file = docs_dir / filename
        story_graph_file.write_text(json.dumps(graph_data, indent=2), encoding='utf-8')
        return story_graph_file
    
    def simple_story_graph(self) -> dict:
        """Return simple story graph data for testing."""
        return {
            "epics": [
                {
                    "name": "Build Knowledge",
                    "sequential_order": 1,
                    "sub_epics": [
                        {
                            "name": "Load Story Graph",
                            "sequential_order": 1,
                            "sub_epics": [],
                            "story_groups": [
                                {
                                    "type": "and",
                                    "connector": None,
                                    "stories": [
                                        {
                                            "name": "Load Story Graph Into Memory",
                                            "sequential_order": 1,
                                            "connector": None,
                                            "users": ["Story Bot"],
                                            "story_type": "user",
                                            "sizing": "5 days",
                                            "scenarios": [
                                                {
                                                    "name": "Story graph file exists",
                                                    "type": "happy_path",
                                                    "background": ["Given story graph file exists"],
                                                    "steps": [
                                                        "When story graph is loaded",
                                                        "Then story map is created with epics"
                                                    ]
                                                },
                                                {
                                                    "name": "Story graph file missing",
                                                    "type": "error_case",
                                                    "background": [],
                                                    "steps": [
                                                        "When story graph file does not exist",
                                                        "Then FileNotFoundError is raised"
                                                    ]
                                                }
                                            ],
                                            "scenario_outlines": [
                                                {
                                                    "name": "Load story graph with different formats",
                                                    "type": "happy_path",
                                                    "background": ["Given story graph file exists"],
                                                    "steps": [
                                                        "When story graph is loaded from \"<file_path>\"",
                                                        "Then story map contains \"<expected_epics>\" epics"
                                                    ],
                                                    "examples": {
                                                        "columns": ["file_path", "expected_epics"],
                                                        "rows": [
                                                            ["story-graph.json", "2"],
                                                            ["story-graph-v2.json", "3"]
                                                        ]
                                                    }
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                    "story_groups": []
                }
            ]
        }
    
    def create_story_map(self, story_graph_data: dict = None):
        """Create StoryMap from story graph data."""
        from scanners.story_map import StoryMap
        if story_graph_data is None:
            story_graph_data = self.simple_story_graph()
        return StoryMap(story_graph_data)
    
    def sample_story_graph(self) -> dict:
        """Return a reusable sample story graph for scope filtering tests."""
        return {
            'epics': [
                {
                    'name': 'Epic A',
                    'sub_epics': [
                        {
                            'name': 'Sub-Epic A1',
                            'story_groups': [
                                {
                                    'type': 'and',
                                    'connector': None,
                                    'stories': [
                                        {'name': 'Story A1'},
                                        {'name': 'Story A2'}
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    'name': 'Epic B',
                    'sub_epics': [
                        {
                            'name': 'Sub-Epic B1',
                            'story_groups': [
                                {
                                    'type': 'and',
                                    'connector': None,
                                    'stories': [
                                        {'name': 'Story B1'},
                                        {'name': 'Story B2'}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ],
            'increments': [
                {
                    'name': 'Increment 1',
                    'priority': 1,
                    'epics': [
                        {
                            'name': 'Epic A',
                            'sub_epics': [
                                {
                                    'name': 'Sub-epic A1',
                                    'stories': [
                                        {'name': 'Story A1'},
                                        {'name': 'Story A2'}
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    'name': 'Increment 2',
                    'priority': 2,
                    'epics': [
                        {
                            'name': 'Epic B',
                            'sub_epics': [
                                {
                                    'name': 'Sub-epic B1',
                                    'stories': [
                                        {'name': 'Story B1'},
                                        {'name': 'Story B2'}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    
    def story_graph_dict(self, minimal=False, scope_type=None, epic=None):
        """Return story graph dictionary for testing."""
        if minimal:
            return {
                "epics": [
                    {
                        "name": "Places Order",
                        "sub_epics": [
                            {
                                "name": "Validates Payment",
                                "story_groups": [
                                    {
                                        "stories": [
                                            {
                                                "name": "Place Order",
                                                "scenarios": []
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        elif scope_type == 'multiple_test_files':
            return {
                "epics": [
                    {
                        "name": "Manage Orders",
                        "sub_epics": [
                            {
                                "name": "Create Order",
                                "story_groups": [
                                    {
                                        "stories": [
                                            {
                                                "name": "Place Order",
                                                "scenarios": []
                                            },
                                            {
                                                "name": "Cancel Order",
                                                "scenarios": []
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        elif epic == 'mob':
            return {
                "epics": [
                    {
                        "name": "Manage Mobs",
                        "sequential_order": 1,
                        "estimated_stories": 6,
                        "domain_concepts": [
                            {
                                "name": "Mob",
                                "responsibilities": [
                                    {
                                        "name": "Groups minions together for coordinated action",
                                        "collaborators": ["Minion"]
                                    }
                                ]
                            }
                        ],
                        "sub_epics": []
                    }
                ]
            }
        else:
            return {
                "epics": [
                    {
                        "name": "Test Epic",
                        "sequential_order": 1,
                        "sub_epics": [],
                        "story_groups": []
                    }
                ]
            }
    
    def story_graph_with_epics_and_increments(self) -> dict:
        """Return test story graph with epics and increments."""
        return {
            'epics': [
                {
                    'name': 'Epic A',
                    'sub_epics': [
                        {
                            'name': 'Sub-epic A1',
                            'story_groups': [
                                {
                                    'stories': [
                                        {'name': 'Story A1'},
                                        {'name': 'Story A2'}
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    'name': 'Epic B',
                    'sub_epics': [
                        {
                            'name': 'Sub-epic B1',
                            'story_groups': [
                                {
                                    'stories': [
                                        {'name': 'Story B1'},
                                        {'name': 'Story B2'}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ],
            'increments': [
                {
                    'name': 'Increment 1',
                    'priority': 1,
                    'epics': [
                        {
                            'name': 'Epic A',
                            'sub_epics': [
                                {
                                    'name': 'Sub-epic A1',
                                    'stories': [
                                        {'name': 'Story A1'},
                                        {'name': 'Story A2'}
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    'name': 'Increment 2',
                    'priority': 2,
                    'epics': [
                        {
                            'name': 'Epic B',
                            'sub_epics': [
                                {
                                    'name': 'Sub-epic B1',
                                    'stories': [
                                        {'name': 'Story B1'},
                                        {'name': 'Story B2'}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    
    def access_story_item(self, item_type, source, **access_params):
        """Access item from story map source."""
        index = access_params.get('index', 0)
        name = access_params.get('name')
        
        if item_type == 'epics':
            return source.epics()
        elif item_type == 'epic':
            if hasattr(source, 'epics'):
                epics = source.epics()
            else:
                epics = source
            return epics[index] if index is not None else epics[0]
        elif item_type == 'sub_epic':
            epics = source if isinstance(source, list) else source.epics()
            return epics[0].children[0]
        elif item_type == 'story':
            if name:
                epic = source if hasattr(source, 'children') else source.epics()[0]
                for sub_epic in epic.children:
                    for story_group in sub_epic.children:
                        for story in story_group.children:
                            if story.name == name:
                                return story
                raise ValueError(f"Story '{name}' not found")
            elif hasattr(source, 'epics'):
                return source.epics()[0].children[0].children[0].children[0]
            elif hasattr(source, 'children'):
                return source.children[0].children[0].children[0]
            else:
                return source[0].children[0].children[0].children[0]
        elif item_type == 'scenario':
            if name:
                story = source if hasattr(source, 'scenarios') else self.access_story_item('story', source)
                for scenario in story.scenarios:
                    if scenario.name == name:
                        return scenario
                raise ValueError(f"Scenario '{name}' not found")
            elif hasattr(source, 'scenarios'):
                return source.scenarios[index]
            else:
                story = self.access_story_item('story', source)
                return story.scenarios[index]
        elif item_type == 'scenario_outline':
            if name:
                scenario = source if hasattr(source, 'examples_columns') else self.access_story_item('scenario', source)
                for outline in scenario.scenario_outlines if hasattr(scenario, 'scenario_outlines') else []:
                    if outline.name == name:
                        return outline
                raise ValueError(f"Scenario outline '{name}' not found")
            elif hasattr(source, 'scenario_outlines'):
                return source.scenario_outlines[index]
            else:
                story = self.access_story_item('story', source)
                return story.scenario_outlines[index]
        else:
            raise ValueError(f"Unknown item_type: {item_type}")
    
    def assert_nodes_match(self, nodes, expected_count=None, expected_names=None):
        """Assert nodes match expected count and names."""
        if expected_count is not None:
            assert len(nodes) == expected_count, f"Expected {expected_count} nodes, got {len(nodes)}"
        if expected_names is not None:
            actual_names = [node.name for node in nodes]
            assert actual_names == expected_names, f"Expected names {expected_names}, got {actual_names}"
    
    def assert_children_match(self, parent, expected_count=None, expected_names=None):
        """Assert children match expected count and names."""
        children = parent.children
        if expected_count is not None:
            assert len(children) == expected_count, f"Expected {expected_count} children, got {len(children)}"
        if expected_names is not None:
            actual_names = [child.name for child in children]
            assert actual_names == expected_names, f"Expected names {expected_names}, got {actual_names}"
    
    def assert_stories_match(self, expected, actual):
        """Assert stories match expected."""
        if isinstance(expected, set) and isinstance(actual, set):
            assert expected == actual, f"Expected {expected}, got {actual}"
        elif isinstance(expected, list) and isinstance(actual, list):
            assert set(expected) == set(actual), f"Expected {expected}, got {actual}"
        else:
            assert expected == actual, f"Expected {expected}, got {actual}"
    
    def assert_scenarios_match(self, story, expected_count=None, expected_names=None):
        """Assert scenarios match expected count and names."""
        scenarios = story.scenarios
        if expected_count is not None:
            assert len(scenarios) == expected_count, f"Expected {expected_count} scenarios, got {len(scenarios)}"
        if expected_names is not None:
            actual_names = [scenario.name for scenario in scenarios]
            assert actual_names == expected_names, f"Expected names {expected_names}, got {actual_names}"
    
    def assert_scenario_outlines_match(self, scenario, expected_count=None, expected_names=None):
        """Assert scenario outlines match expected count and names."""
        from scanners.story_map import Story
        if isinstance(scenario, Story):
            outlines = scenario.scenario_outlines
        else:
            outlines = scenario.scenario_outlines if hasattr(scenario, 'scenario_outlines') else []
        if expected_count is not None:
            assert len(outlines) == expected_count, f"Expected {expected_count} scenario outlines, got {len(outlines)}"
        if expected_names is not None:
            actual_names = [outline.name for outline in outlines]
            assert actual_names == expected_names, f"Expected names {expected_names}, got {actual_names}"
    
    def assert_story_map_matches(self, story_map_or_epics, epic_name=None):
        """Assert story map matches expected epic."""
        from scanners.story_map import Epic
        
        if isinstance(story_map_or_epics, list):
            epics = story_map_or_epics
            assert len(epics) == 1, f"Expected 1 epic, got {len(epics)}"
            assert isinstance(epics[0], Epic), f"Expected Epic instance, got {type(epics[0])}"
            expected_name = epic_name if epic_name is not None else "Build Knowledge"
            assert epics[0].name == expected_name, \
                f"Expected epic name '{expected_name}', got '{epics[0].name}'"
            return epics[0]
        else:
            epics_list = story_map_or_epics.epics()
            assert len(epics_list) == 1, f"Expected 1 epic, got {len(epics_list)}"
            expected_name = epic_name if epic_name is not None else "Test Epic"
            assert epics_list[0].name == expected_name, \
                f"Expected epic name '{expected_name}', got '{epics_list[0].name}'"
    
    def assert_map_location_matches(self, item, item_type=None, field=None):
        """Assert map location correctness for story map items."""
        from scanners.story_map import Epic, SubEpic, Story, Scenario, ScenarioOutline
        
        if item_type is None:
            if isinstance(item, Epic):
                item_type = 'epic'
            elif isinstance(item, SubEpic):
                item_type = 'sub_epic'
            elif isinstance(item, Story):
                item_type = 'story'
            elif isinstance(item, Scenario):
                item_type = 'scenario'
            elif isinstance(item, ScenarioOutline):
                item_type = 'scenario_outline'
        
        expected_locations = {
            'epic': {
                None: "epics[0].name",
                'sequential_order': "epics[0].sequential_order"
            },
            'sub_epic': {
                None: "epics[0].sub_epics[0].name"
            },
            'story': {
                None: "epics[0].sub_epics[0].story_groups[0].stories[0].name",
                'sizing': "epics[0].sub_epics[0].story_groups[0].stories[0].sizing"
            },
            'scenario': {
                None: "epics[0].sub_epics[0].story_groups[0].stories[0].scenarios[0].name"
            },
            'scenario_outline': {
                None: "epics[0].sub_epics[0].story_groups[0].stories[0].scenario_outlines[0].name"
            }
        }
        
        expected_default = expected_locations.get(item_type, {}).get(None)
        assert item.map_location() == expected_default, \
            f"Expected map_location() == '{expected_default}', got '{item.map_location()}'"
        
        if item_type == 'epic':
            expected_seq = expected_locations.get(item_type, {}).get('sequential_order')
            assert item.map_location('sequential_order') == expected_seq, \
                f"Expected map_location('sequential_order') == '{expected_seq}', got '{item.map_location('sequential_order')}'"
        elif item_type == 'story' and field == 'sizing':
            expected_sizing = expected_locations.get(item_type, {}).get('sizing')
            assert item.map_location('sizing') == expected_sizing, \
                f"Expected map_location('sizing') == '{expected_sizing}', got '{item.map_location('sizing')}'"
    
    def given_story_graph(self, story_graph: dict = None, docs_path: str = 'docs/stories', filename: str = 'story-graph.json') -> Path:
        """Create story graph file in workspace."""
        if story_graph is None:
            story_graph = {'epics': []}
        
        docs_dir = self.parent.workspace / docs_path
        docs_dir.mkdir(parents=True, exist_ok=True)
        story_graph_file = docs_dir / filename
        story_graph_file.write_text(json.dumps(story_graph, indent=2), encoding='utf-8')
        return story_graph_file
    
    def given_story_graph_dict(self, minimal=False, scope_type=None, epic=None):
        """Return story graph dictionary for testing (alias for story_graph_dict)."""
        return self.story_graph_dict(minimal, scope_type, epic)
    
    def when_item_accessed(self, item_type, source, **access_params):
        """Access item from source (alias for access_story_item)."""
        return self.access_story_item(item_type, source, **access_params)

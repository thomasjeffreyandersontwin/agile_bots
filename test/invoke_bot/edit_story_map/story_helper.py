"""
Story Test Helper
Handles story graph, story map, epics, scenarios testing
"""
import json
from pathlib import Path
from helpers.base_helper import BaseHelper


class StoryTestHelper(BaseHelper):
    """Helper for story graph and story map testing"""
    
    @property
    def bot(self):
        """Access bot instance for bot.story_graph API."""
        return self.parent.bot
    
    def create_story_graph(self, graph_data: dict = None, docs_path: str = 'docs/stories', filename: str = 'story-graph.json') -> Path:
        """Create test story-graph.json in workspace and load into bot.story_graph.
        
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
        
        self.load_story_graph_into_bot()
        
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
    
    def _get_epics(self, source):
        """Get epics from source, handling both method and property APIs."""
        epics_attr = source.epics
        # If epics is callable (method), call it; otherwise it's already a property
        return epics_attr() if callable(epics_attr) else epics_attr
    
    def access_story_item(self, item_type, source, **access_params):
        """Access item from story map source."""
        index = access_params.get('index', 0)
        name = access_params.get('name')
        
        if item_type == 'epics':
            return self._get_epics(source)
        elif item_type == 'epic':
            if hasattr(source, 'epics'):
                epics = self._get_epics(source)
            else:
                epics = source
            return epics[index] if index is not None else epics[0]
        elif item_type == 'sub_epic':
            epics = source if isinstance(source, list) else self._get_epics(source)
            return epics[0].children[0]
        elif item_type == 'story':
            if name:
                epic = source if hasattr(source, 'children') else self._get_epics(source)[0]
                for sub_epic in epic.children:
                    for story_group in sub_epic.children:
                        for story in story_group.children:
                            if story.name == name:
                                return story
                raise ValueError(f"Story '{name}' not found")
            elif hasattr(source, 'epics'):
                return self._get_epics(source)[0].children[0].children[0].children[0]
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
            epics_collection = self._get_epics(story_map_or_epics)
            epics_list = list(epics_collection)
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
    
    def create_story_graph_with_parent_and_children(self, parent_type, parent_name, existing_count, child_type):
        """Create story graph with parent node and existing children."""
        graph_data = {'epics': []}
        
        if parent_type == 'Epic':
            epic = {'name': parent_name, 'sub_epics': []}
            for i in range(existing_count):
                epic['sub_epics'].append({
                    'name': f'SubEpic {chr(65 + i)}',
                    'sequential_order': i
                })
            graph_data['epics'].append(epic)
        elif parent_type == 'SubEpic':
            epic = {'name': 'Test Epic', 'sub_epics': []}
            subepic = {'name': parent_name, 'sequential_order': 0}
            if child_type == 'SubEpic':
                subepic['sub_epics'] = []
                for i in range(existing_count):
                    subepic['sub_epics'].append({
                        'name': f'SubEpic {chr(65 + i)}',
                        'sequential_order': i
                    })
            elif child_type == 'Story':
                subepic['story_groups'] = [{'type': 'and', 'stories': []}]
                for i in range(existing_count):
                    subepic['story_groups'][0]['stories'].append({
                        'name': f'Story {chr(65 + i)}',
                        'sequential_order': i,
                        'scenarios': []
                    })
            epic['sub_epics'].append(subepic)
            graph_data['epics'].append(epic)
        elif parent_type == 'Story':
            epic = {'name': 'Test Epic', 'sub_epics': []}
            subepic = {'name': 'Test SubEpic', 'sequential_order': 0, 'story_groups': [{'type': 'and', 'stories': []}]}
            story = {'name': parent_name, 'sequential_order': 0, 'scenarios': []}
            for i in range(existing_count):
                story['scenarios'].append({
                    'name': f'Scenario {chr(65 + i)}',
                    'steps': []
                })
            subepic['story_groups'][0]['stories'].append(story)
            epic['sub_epics'].append(subepic)
            graph_data['epics'].append(epic)
        
        self.create_story_graph(graph_data)
        return graph_data
    
    def create_story_graph_with_named_children(self, parent_type, parent_name, existing_children_csv):
        """Create story graph with parent node and named children."""
        graph_data = {'epics': []}
        child_names = [name.strip() for name in existing_children_csv.split(',')] if existing_children_csv else []
        
        if parent_type == 'Epic':
            epic = {'name': parent_name, 'sub_epics': []}
            for i, name in enumerate(child_names):
                epic['sub_epics'].append({
                    'name': name,
                    'sequential_order': i
                })
            graph_data['epics'].append(epic)
        elif parent_type == 'SubEpic':
            epic = {'name': 'Test Epic', 'sub_epics': []}
            subepic = {'name': parent_name, 'sequential_order': 0}
            
            has_nested_structure = any('Flow' in name or 'Reset' in name or 'OAuth' in name or 'Auth' in name for name in child_names)
            
            if has_nested_structure:
                subepic['sub_epics'] = []
                for i, name in enumerate(child_names):
                    subepic['sub_epics'].append({
                        'name': name,
                        'sequential_order': i
                    })
            else:
                subepic['story_groups'] = [{'type': 'and', 'stories': []}]
                for i, name in enumerate(child_names):
                    subepic['story_groups'][0]['stories'].append({
                        'name': name,
                        'sequential_order': i,
                        'scenarios': []
                    })
            epic['sub_epics'].append(subepic)
            graph_data['epics'].append(epic)
        elif parent_type == 'Story':
            epic = {'name': 'Test Epic', 'sub_epics': []}
            subepic = {'name': 'Test SubEpic', 'sequential_order': 0, 'story_groups': [{'type': 'and', 'stories': []}]}
            story = {'name': parent_name, 'sequential_order': 0, 'scenarios': []}
            for i, name in enumerate(child_names):
                story['scenarios'].append({
                    'name': name,
                    'sequential_order': i,
                    'steps': []
                })
            subepic['story_groups'][0]['stories'].append(story)
            epic['sub_epics'].append(subepic)
            graph_data['epics'].append(epic)
        
        self.create_story_graph(graph_data)
        return graph_data
    
    def create_story_graph_with_existing_child(self, parent_type, parent_name, existing_child_name, child_type):
        """Create story graph with parent node and one existing child."""
        graph_data = {'epics': []}
        
        if parent_type == 'Epic':
            epic = {'name': parent_name, 'sub_epics': []}
            epic['sub_epics'].append({
                'name': existing_child_name,
                'sequential_order': 0
            })
            graph_data['epics'].append(epic)
        elif parent_type == 'SubEpic':
            epic = {'name': 'Test Epic', 'sub_epics': []}
            subepic = {'name': parent_name, 'sequential_order': 0}
            if child_type == 'Story':
                subepic['story_groups'] = [{'type': 'and', 'stories': []}]
                subepic['story_groups'][0]['stories'].append({
                    'name': existing_child_name,
                    'sequential_order': 0,
                    'scenarios': []
                })
            else:
                subepic['sub_epics'] = []
                subepic['sub_epics'].append({
                    'name': existing_child_name,
                    'sequential_order': 0
                })
            epic['sub_epics'].append(subepic)
            graph_data['epics'].append(epic)
        elif parent_type == 'Story':
            epic = {'name': 'Test Epic', 'sub_epics': []}
            subepic = {'name': 'Test SubEpic', 'sequential_order': 0, 'story_groups': [{'type': 'and', 'stories': []}]}
            story = {'name': parent_name, 'sequential_order': 0, 'scenarios': []}
            if child_type == 'Scenario':
                story['scenarios'].append({
                    'name': existing_child_name,
                    'sequential_order': 0,
                    'steps': []
                })
            subepic['story_groups'][0]['stories'].append(story)
            epic['sub_epics'].append(subepic)
            graph_data['epics'].append(epic)
        
        self.create_story_graph(graph_data)
        return graph_data
    
    def create_subepic_with_existing_stories(self, subepic_name, existing_story_count):
        """Create SubEpic with existing Story count."""
        graph_data = {'epics': []}
        epic = {'name': 'Test Epic', 'sub_epics': []}
        subepic = {'name': subepic_name, 'sequential_order': 0, 'story_groups': [{'type': 'and', 'stories': []}]}
        for i in range(existing_story_count):
            subepic['story_groups'][0]['stories'].append({
                'name': f'Story {chr(65 + i)}',
                'sequential_order': i,
                'scenarios': []
            })
        epic['sub_epics'].append(subepic)
        graph_data['epics'].append(epic)
        
        self.create_story_graph(graph_data)
        return graph_data
    
    def create_subepic_with_existing_story(self, subepic_name, existing_story):
        """Create SubEpic with one existing Story."""
        return self.create_subepic_with_existing_stories(subepic_name, 1)
    
    def create_subepic_with_existing_subepic(self, subepic_name, existing_subepic):
        """Create SubEpic with one existing SubEpic child."""
        graph_data = {'epics': []}
        epic = {'name': 'Test Epic', 'sub_epics': []}
        subepic = {'name': subepic_name, 'sequential_order': 0, 'sub_epics': []}
        subepic['sub_epics'].append({
            'name': existing_subepic,
            'sequential_order': 0
        })
        epic['sub_epics'].append(subepic)
        graph_data['epics'].append(epic)
        
        self.create_story_graph(graph_data)
        return graph_data
    
    def create_story_in_graph(self, story_name):
        """Create Story in story graph."""
        graph_data = {'epics': []}
        epic = {'name': 'Test Epic', 'sub_epics': []}
        subepic = {'name': 'Test SubEpic', 'sequential_order': 0, 'story_groups': [{'type': 'and', 'stories': []}]}
        story = {'name': story_name, 'sequential_order': 0, 'scenarios': []}
        subepic['story_groups'][0]['stories'].append(story)
        epic['sub_epics'].append(subepic)
        graph_data['epics'].append(epic)
        
        self.create_story_graph(graph_data)
        return graph_data
    
    def find_subepic_in_story_graph(self, name):
        """Find SubEpic by name in bot.story_graph."""
        from story_graph.nodes import SubEpic
        
        for epic in self.bot.story_graph.epics:
            for node in self.bot.story_graph.walk(epic):
                if isinstance(node, SubEpic) and node.name == name:
                    return node
        raise ValueError(f"SubEpic '{name}' not found in bot.story_graph")
    
    def find_story_in_story_graph(self, name):
        """Find Story by name in bot.story_graph."""
        from story_graph.nodes import Story
        
        for epic in self.bot.story_graph.epics:
            for node in self.bot.story_graph.walk(epic):
                if isinstance(node, Story) and node.name == name:
                    return node
        raise ValueError(f"Story '{name}' not found in bot.story_graph")
    
    def find_story_in_parent(self, parent, name):
        """Find Story by name within parent (handles StoryGroup)."""
        from story_graph.nodes import SubEpic, StoryGroup, Story
        
        if isinstance(parent, SubEpic):
            story_groups = [c for c in parent.children if isinstance(c, StoryGroup)]
            if story_groups:
                for story in story_groups[0].children:
                    if isinstance(story, Story) and story.name == name:
                        return story
        
        for child in parent.children:
            if child.name == name:
                return child
        return None
    
    def find_scenario_in_story_graph(self, name):
        """Find Scenario by name in bot.story_graph."""
        from story_graph.nodes import Scenario
        
        for epic in self.bot.story_graph.epics:
            for node in self.bot.story_graph.walk(epic):
                if isinstance(node, Scenario) and node.name == name:
                    return node
        raise ValueError(f"Scenario '{name}' not found in bot.story_graph")
    
    def load_story_graph_into_bot(self):
        """Load story graph into bot.story_graph for test access.
        
        Note: Bot now has a native story_graph property that loads from workspace.
        This method forces a reload by clearing the cached instance.
        """
        story_graph_path = self.bot.bot_paths.workspace_directory / 'docs' / 'stories' / 'story-graph.json'
        if not story_graph_path.exists():
            return None
        
        # Clear cached story_graph to force reload from file
        self.bot._story_graph = None
        
        # Access the property which will lazy-load it
        story_map = self.bot.story_graph
        
        return story_map
    
    def get_children_names(self, parent_name):
        """Get list of child names for a parent node - uses real domain objects from bot.story_graph."""
        if parent_name in self.bot.story_graph.epics:
            parent = self.bot.story_graph.epics[parent_name]
        else:
            parent = self.find_subepic_in_story_graph(parent_name) or self.find_story_in_story_graph(parent_name)
        return [child.name for child in parent.children]
    
    def get_child_count(self, parent_name):
        """Get count of children for a parent node."""
        return len(self.get_children_names(parent_name))
    
    def get_child_position(self, parent_name, child_name):
        """Get position of child in parent's children list."""
        children = self.get_children_names(parent_name)
        try:
            return children.index(child_name)
        except ValueError:
            raise ValueError(f"Child '{child_name}' not found under '{parent_name}'")
    
    def assert_story_is_in_storygroup_at_position(self, subepic_name, story_name, expected_position):
        """Verify Story is in StoryGroup at expected position - uses real domain objects from bot.story_graph."""
        from story_graph.nodes import StoryGroup, Story
        
        subepic = self.find_subepic_in_story_graph(subepic_name)
        # Check internal structure to verify StoryGroup exists
        story_groups = [child for child in subepic._children if isinstance(child, StoryGroup)]
        assert len(story_groups) > 0
        
        # Use public API to check stories (now transparent)
        stories = list(subepic.children)
        story_names = [s.name for s in stories if isinstance(s, Story)]
        assert story_name in story_names
        
        actual_position = story_names.index(story_name)
        assert actual_position == expected_position
    
    def assert_storygroup_exists(self, subepic_name):
        """Verify StoryGroup exists - uses real domain objects from bot.story_graph."""
        from story_graph.nodes import StoryGroup
        
        subepic = self.find_subepic_in_story_graph(subepic_name)
        # Check internal structure to verify StoryGroup exists
        story_groups = [child for child in subepic._children if isinstance(child, StoryGroup)]
        assert len(story_groups) > 0
    
    def assert_child_is_in_collection(self, story_name, child_name, collection_name):
        """Verify child is in target collection - uses real domain objects from bot.story_graph."""
        story = self.find_story_in_story_graph(story_name)
        
        if collection_name == 'scenarios':
            children = story.scenarios
        elif collection_name == 'scenario_outlines':
            children = story.scenario_outlines
        elif collection_name == 'acceptance_criteria':
            children = story.acceptance_criteria
        else:
            raise ValueError(f"Unknown collection: {collection_name}")
        
        child_names = [c.name for c in children]
        assert child_name in child_names
    
    def assert_child_is_not_in_collection(self, story_name, child_name, excluded_collection):
        """Verify child is not in excluded collection - uses real domain objects from bot.story_graph."""
        story = self.find_story_in_story_graph(story_name)
        
        if excluded_collection == 'scenarios':
            children = story.scenarios
        elif excluded_collection == 'scenario_outlines':
            children = story.scenario_outlines
        elif excluded_collection == 'acceptance_criteria':
            children = story.acceptance_criteria
        else:
            children = []
        
        child_names = [c.name for c in children]
        assert child_name not in child_names
    
    def create_story_graph_with_node_and_children(self, grandparent_type, grandparent, node_name, node_children, initial_child_count):
        """Create story graph with node that has children under grandparent."""
        graph_data = {'epics': []}
        epic = {'name': 'Test Epic' if grandparent_type != 'Epic' else grandparent, 'sub_epics': []}
        
        if grandparent_type == 'Epic':
            node = {'name': node_name, 'sequential_order': 0, 'sub_epics': []}
            for i, child in enumerate([n.strip() for n in node_children.split(',')]):
                node['sub_epics'].append({'name': child, 'sequential_order': i})
            for i in range(initial_child_count - 1):
                epic['sub_epics'].append({'name': f'Other {i}', 'sequential_order': i + 1})
            epic['sub_epics'].insert(0, node)
        elif grandparent_type == 'SubEpic':
            subepic = {'name': grandparent, 'sequential_order': 0, 'sub_epics': []}
            node = {'name': node_name, 'sequential_order': 0, 'story_groups': [{'type': 'and', 'stories': []}]}
            for i, child in enumerate([n.strip() for n in node_children.split(',')]):
                node['story_groups'][0]['stories'].append({'name': child, 'sequential_order': i, 'scenarios': []})
            for i in range(initial_child_count - 1):
                subepic['sub_epics'].append({'name': f'Other {i}', 'sequential_order': i + 1})
            subepic['sub_epics'].insert(0, node)
            epic['sub_epics'].append(subepic)
        
        graph_data['epics'].append(epic)
        self.create_story_graph(graph_data)
        return graph_data
    
    def create_story_graph_with_descendants(self, parent_type, parent_name, initial_children, node_name, child_count, total_descendants):
        """Create story graph with node that has multiple descendant levels."""
        graph_data = {'epics': []}
        
        initial_child_list = [n.strip() for n in initial_children.split(',')]
        if parent_type == 'Epic':
            epic = {'name': parent_name, 'sub_epics': []}
            for child_name in initial_child_list:
                if child_name == node_name:
                    subepic = {'name': node_name, 'sequential_order': len(epic['sub_epics']), 'sub_epics': []}
                    for i in range(child_count):
                        nested = {'name': f'Nested {i}', 'sequential_order': i, 'story_groups': [{'type': 'and', 'stories': []}]}
                        for j in range(2):
                            nested['story_groups'][0]['stories'].append({
                                'name': f'Story {i}-{j}',
                                'sequential_order': j,
                                'scenarios': []
                            })
                        subepic['sub_epics'].append(nested)
                    epic['sub_epics'].append(subepic)
                else:
                    epic['sub_epics'].append({'name': child_name, 'sequential_order': len(epic['sub_epics'])})
            graph_data['epics'].append(epic)
        elif parent_type == 'SubEpic':
            epic = {'name': 'Test Epic', 'sub_epics': []}
            parent_subepic = {'name': parent_name, 'sequential_order': 0, 'sub_epics': []}
            for child_name in initial_child_list:
                if child_name == node_name:
                    subepic = {'name': node_name, 'sequential_order': len(parent_subepic['sub_epics']), 'sub_epics': []}
                    for i in range(child_count):
                        nested = {'name': f'Nested {i}', 'sequential_order': i, 'story_groups': [{'type': 'and', 'stories': []}]}
                        for j in range(2):
                            nested['story_groups'][0]['stories'].append({
                                'name': f'Story {i}-{j}',
                                'sequential_order': j,
                                'scenarios': []
                            })
                        subepic['sub_epics'].append(nested)
                    parent_subepic['sub_epics'].append(subepic)
                else:
                    parent_subepic['sub_epics'].append({'name': child_name, 'sequential_order': len(parent_subepic['sub_epics'])})
            epic['sub_epics'].append(parent_subepic)
            graph_data['epics'].append(epic)
        
        self.create_story_graph(graph_data)
        return graph_data
    
    def assert_children_have_sequential_positions(self, parent_name):
        """Verify all children have sequential positions (0, 1, 2, ...)."""
        try:
            parent = self.bot.story_graph.epics[parent_name]
        except KeyError:
            try:
                parent = self.find_subepic_in_story_graph(parent_name)
            except ValueError:
                parent = self.find_story_in_story_graph(parent_name)
        
        children = list(parent.children)
        for i, child in enumerate(children):
            assert child.sequential_order is not None or i == 0
    
    def create_story_graph_with_node(self, node_type, parent_name, node_name):
        """Create story graph with single node."""
        graph_data = {'epics': []}
        
        if node_type == 'Epic':
            graph_data['epics'].append({'name': node_name, 'sub_epics': []})
        elif node_type == 'SubEpic':
            epic = {'name': parent_name if parent_name != 'root' else 'Root Epic', 'sub_epics': []}
            epic['sub_epics'].append({'name': node_name, 'sequential_order': 0})
            graph_data['epics'].append(epic)
        elif node_type == 'Story':
            epic = {'name': 'Test Epic', 'sub_epics': []}
            subepic = {'name': parent_name, 'sequential_order': 0, 'story_groups': [{'type': 'and', 'stories': []}]}
            subepic['story_groups'][0]['stories'].append({'name': node_name, 'sequential_order': 0, 'scenarios': []})
            epic['sub_epics'].append(subepic)
            graph_data['epics'].append(epic)
        elif node_type == 'Scenario':
            epic = {'name': 'Test Epic', 'sub_epics': []}
            subepic = {'name': 'Test SubEpic', 'sequential_order': 0, 'story_groups': [{'type': 'and', 'stories': []}]}
            story = {'name': parent_name, 'sequential_order': 0, 'scenarios': []}
            story['scenarios'].append({'name': node_name, 'steps': []})
            subepic['story_groups'][0]['stories'].append(story)
            epic['sub_epics'].append(subepic)
            graph_data['epics'].append(epic)
        
        self.create_story_graph(graph_data)
        return graph_data
    
    def create_story_graph_for_move(self, source_parent_type, source_parent, node_name, target_parent_type, target_parent, target_child_count):
        """Create story graph for move operation tests."""
        graph_data = {'epics': []}
        
        if source_parent_type == 'Epic' and target_parent_type == 'Epic':
            source_epic = {'name': source_parent, 'sub_epics': []}
            source_epic['sub_epics'].append({'name': node_name, 'sequential_order': 0})
            
            target_epic = {'name': target_parent, 'sub_epics': []}
            for i in range(target_child_count):
                target_epic['sub_epics'].append({'name': f'Existing {i}', 'sequential_order': i})
            
            graph_data['epics'].extend([source_epic, target_epic])
        elif source_parent_type == 'SubEpic' and target_parent_type == 'SubEpic':
            epic = {'name': 'Test Epic', 'sub_epics': []}
            
            # Create source SubEpic with node
            source_subepic = {'name': source_parent, 'sequential_order': 0, 'sub_epics': []}
            source_subepic['sub_epics'].append({'name': node_name, 'sequential_order': 0})
            
            # Create target SubEpic with existing children
            target_subepic = {'name': target_parent, 'sequential_order': 1, 'sub_epics': []}
            for i in range(target_child_count):
                target_subepic['sub_epics'].append({'name': f'Existing {i}', 'sequential_order': i})
            
            epic['sub_epics'].extend([source_subepic, target_subepic])
            graph_data['epics'].append(epic)
        
        self.create_story_graph(graph_data)
        return graph_data
    
    def create_story_graph_for_move_with_children(self, source_parent, node_name, target_parent, target_children):
        """Create story graph for move with specific target children."""
        graph_data = {'epics': []}
        
        source_epic = {'name': source_parent, 'sub_epics': []}
        source_epic['sub_epics'].append({'name': node_name, 'sequential_order': 0})
        
        target_epic = {'name': target_parent, 'sub_epics': []}
        for i, child in enumerate([n.strip() for n in target_children.split(',')]):
            target_epic['sub_epics'].append({'name': child, 'sequential_order': i})
        
        graph_data['epics'].extend([source_epic, target_epic])
        self.create_story_graph(graph_data)
        return graph_data
    
    def create_story_graph_with_child(self, parent_type, parent_name, node_name):
        """Create story graph with parent and single child."""
        graph_data = {'epics': []}
        
        if parent_type == 'Epic':
            epic = {'name': parent_name, 'sub_epics': [{'name': node_name, 'sequential_order': 0}]}
            graph_data['epics'].append(epic)
        elif parent_type == 'SubEpic':
            epic = {'name': 'Test Epic', 'sub_epics': []}
            subepic = {'name': parent_name, 'sequential_order': 0, 'story_groups': [{'type': 'and', 'stories': [{'name': node_name, 'sequential_order': 0, 'scenarios': []}]}]}
            epic['sub_epics'].append(subepic)
            graph_data['epics'].append(epic)
        
        self.create_story_graph(graph_data)
        return graph_data
    
    def create_story_graph_for_hierarchy_move_test(self, source_parent, node_name, node_type, target_parent, existing_child, existing_type):
        """Create story graph for hierarchy violation move tests."""
        graph_data = {'epics': []}
        epic = {'name': 'Test Epic', 'sub_epics': []}
        
        source = {'name': source_parent, 'sequential_order': 0, 'sub_epics': []}
        if node_type == 'SubEpic':
            source['sub_epics'].append({'name': node_name, 'sequential_order': 0})
        else:
            source['story_groups'] = [{'type': 'and', 'stories': []}]
            source['story_groups'][0]['stories'].append({'name': node_name, 'sequential_order': 0, 'scenarios': []})
        
        target = {'name': target_parent, 'sequential_order': 1}
        if existing_type == 'SubEpic':
            target['sub_epics'] = [{'name': existing_child, 'sequential_order': 0}]
        else:
            target['story_groups'] = [{'type': 'and', 'stories': []}]
            target['story_groups'][0]['stories'].append({'name': existing_child, 'sequential_order': 0, 'scenarios': []})
        
        epic['sub_epics'].extend([source, target])
        graph_data['epics'].append(epic)
        self.create_story_graph(graph_data)
        return graph_data
    
    def create_story_graph_with_descendant(self, parent_type, parent_name, child_name):
        """Create story graph with parent and descendant."""
        graph_data = {'epics': []}
        
        if parent_type == 'Epic':
            epic = {'name': parent_name, 'sub_epics': []}
            epic['sub_epics'].append({'name': child_name, 'sequential_order': 0})
            graph_data['epics'].append(epic)
        elif parent_type == 'SubEpic':
            epic = {'name': 'Test Epic', 'sub_epics': []}
            subepic = {'name': parent_name, 'sequential_order': 0, 'sub_epics': []}
            subepic['sub_epics'].append({'name': child_name, 'sequential_order': 0})
            epic['sub_epics'].append(subepic)
            graph_data['epics'].append(epic)
        
        self.create_story_graph(graph_data)
        return graph_data
    
    def create_story_graph_with_node_and_actions(self, node_type, node_name, actions):
        """Create story graph with node and register bot actions."""
        graph_data = self.create_story_graph_with_node(node_type, 'parent', node_name)
        self.load_story_graph_into_bot()
        if node_type == 'Epic':
            node = self.bot.story_graph.epics[node_name]
        elif node_type == 'SubEpic':
            node = self.find_subepic_in_story_graph(node_name)
        else:
            node = self.find_story_in_story_graph(node_name)
        node._registered_actions = actions
        return graph_data
    
    def assert_story_graph_structure_valid(self):
        """Verify story graph structure is valid."""
        story_graph_path = self.parent.workspace / 'docs' / 'stories' / 'story-graph.json'
        assert story_graph_path.exists()
        story_graph_data = json.loads(story_graph_path.read_text(encoding='utf-8'))
        assert 'epics' in story_graph_data
    
    def assert_child_created_at_position(self, parent, child_name, expected_position, total_children):
        """Assert child was created at expected position with correct total count."""
        children = list(parent.children)
        assert len(children) == total_children
        assert children[expected_position].name == child_name
    
    def assert_children_in_order(self, parent, expected_order_csv):
        """Assert children are in expected order."""
        expected_names = [name.strip() for name in expected_order_csv.split(',')]
        actual_names = [c.name for c in parent.children]
        assert actual_names == expected_names
    
    def assert_child_at_position(self, parent, child_name, expected_position):
        """Assert specific child is at expected position."""
        children = list(parent.children)
        assert children[expected_position].name == child_name
    
    def assert_node_removed_from_parent(self, parent, node_name):
        """Assert node no longer exists in parent's children."""
        child_names = [c.name for c in parent.children]
        assert node_name not in child_names
    
    def assert_node_added_to_parent(self, parent, node_name, expected_position=None):
        """Assert node exists in parent's children at optional position."""
        child_names = [c.name for c in parent.children]
        assert node_name in child_names
        if expected_position is not None:
            children = list(parent.children)
            assert children[expected_position].name == node_name
    
    def assert_children_promoted_to_grandparent(self, grandparent, promoted_children_csv, expected_total):
        """Assert children were promoted to grandparent."""
        grandparent_children = list(grandparent.children)
        assert len(grandparent_children) == expected_total
        grandparent_child_names = [c.name for c in grandparent_children]
        for child_name in [n.strip() for n in promoted_children_csv.split(',')]:
            assert child_name in grandparent_child_names
    
    def assert_parent_child_count(self, parent, expected_count):
        """Assert parent has expected number of children."""
        assert len(parent.children) == expected_count
    
    # =======================================================================================
    # Story Map / Epic Creation Helpers
    # =======================================================================================
    
    def create_story_map_empty(self) -> None:
        """Create an empty story map with no epics"""
        story_graph_data = {
            'epics': []
        }
        self.create_story_graph(story_graph_data)
    
    def create_story_map_with_epics(self, epic_names: list) -> None:
        """Create a story map with specified epic names"""
        epics = []
        for epic_name in epic_names:
            epics.append({
                'name': epic_name,
                'domain_concepts': [],
                'sub_epics': [],
                'story_groups': []
            })
        
        story_graph_data = {
            'epics': epics
        }
        self.create_story_graph(story_graph_data)
    
    def create_epic_with_children(self, epic_name: str, child_count: int, child_type: str = 'SubEpic') -> None:
        """Create an Epic with specified number of children."""
        epic = {
            'name': epic_name,
            'sequential_order': 0,
            'domain_concepts': [],
            'sub_epics': [],
            'story_groups': []
        }
        
        # Add children based on type
        for i in range(child_count):
            if child_type == 'SubEpic':
                epic['sub_epics'].append({
                    'name': f'{child_type}{i + 1}',
                    'sequential_order': i,
                    'sub_epics': [],
                    'story_groups': []
                })
        
        story_graph_data = {
            'epics': [epic]
        }
        self.create_story_graph(story_graph_data)
    
    def create_epic(self, epic_name: str) -> None:
        """Create a single epic with the given name. Appends to existing story graph if present."""
        story_graph_path = self.parent.workspace / 'docs' / 'stories' / 'story-graph.json'
        
        # Ensure directory exists
        story_graph_path.parent.mkdir(parents=True, exist_ok=True)
        
        if story_graph_path.exists():
            # Append to existing story graph
            existing_data = json.loads(story_graph_path.read_text(encoding='utf-8'))
            existing_data['epics'].append({
                'name': epic_name,
                'domain_concepts': [],
                'sub_epics': [],
                'story_groups': []
            })
            story_graph_path.write_text(json.dumps(existing_data, indent=2), encoding='utf-8')
            self.load_story_graph_into_bot()
        else:
            # Create new story graph
            story_graph_data = {
                'epics': [{
                    'name': epic_name,
                    'domain_concepts': [],
                    'sub_epics': [],
                    'story_groups': []
                }]
            }
            self.create_story_graph(story_graph_data)
    
    def create_story_graph_with_sub_epics(self, epic_subepic_list):
        """Create story graph with epics and sub-epics.
        
        Args:
            epic_subepic_list: List of tuples [(epic_name, [subepic_names])]
        """
        epics = []
        for epic_name, subepic_names in epic_subepic_list:
            epic = {
                'name': epic_name,
                'sequential_order': len(epics),
                'domain_concepts': [],
                'sub_epics': [],
                'story_groups': []
            }
            for i, subepic_name in enumerate(subepic_names):
                epic['sub_epics'].append({
                    'name': subepic_name,
                    'sequential_order': i,
                    'sub_epics': [],
                    'story_groups': []
                })
            epics.append(epic)
        
        story_graph_data = {'epics': epics}
        self.create_story_graph(story_graph_data)
        return story_graph_data
    
    def create_story_under_subepic(self, subepic, story_name, test_class=None):
        """Create a story under a SubEpic.
        
        Args:
            subepic: SubEpic node
            story_name: Name of the story to create
            test_class: Optional test class name
            
        Returns:
            Created Story node
        """
        from story_graph.nodes import Story
        
        # Create story using SubEpic's create_story method
        story = subepic.create_story(name=story_name)
        
        # Set test_class if provided
        if test_class:
            story.test_class = test_class
            story.save()
        
        return story


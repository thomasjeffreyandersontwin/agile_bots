from abc import ABC, abstractmethod
from typing import List, Iterator, Optional, Dict, Any, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from pathlib import Path
import json
from datetime import datetime
from story_graph.domain import DomainConcept, StoryUser

def _log(message: str):
    """Write log message to file."""
    log_file = Path(__file__).parent.parent.parent / 'logs' / 'test_class_mover.log'
    log_file.parent.mkdir(exist_ok=True)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().isoformat()} {message}\n")

@dataclass
class ActionResult:
    success: bool
    action_name: str
    data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

@dataclass
class StoryNode(ABC):
    name: str
    sequential_order: Optional[float] = None
    behavior: Optional[str] = None
    _bot: Optional[Any] = field(default=None, repr=False)

    def __post_init__(self):
        self._children: List['StoryNode'] = []

    @property
    @abstractmethod
    def children(self) -> List['StoryNode']:
        pass

    def __iter__(self) -> Iterator['StoryNode']:
        return iter(self.children)
    
    def __getitem__(self, child_name: str) -> 'StoryNode':
        """Access child by name"""
        for child in self.children:
            if child.name == child_name:
                return child
        raise KeyError(f"Child '{child_name}' not found in {type(self).__name__} '{self.name}'")

    def __repr__(self) -> str:
        order = f', order={self.sequential_order}' if self.sequential_order is not None else ''
        return f"{self.__class__.__name__}(name='{self.name}'{order})"
    
    @property
    def node_type(self) -> str:
        return self.__class__.__name__.lower()

    def save(self) -> None:
        """Save this node's changes to the story graph and persist to disk."""
        if not self._bot:
            return
        
        story_map = self._bot.story_map
        
        if isinstance(self, Story):
            self.file_link = story_map._calculate_story_file_link(self)
        
        story_map.save()
    
    def save_all(self) -> None:
        """Save this node and all children's changes to the story graph and persist to disk."""
        # Same as save() since updating the parent updates all children
        self.save()

    def get_required_behavior_instructions(self, action: str):
        if not self._bot:
            raise RuntimeError(f"Cannot get instructions: node '{self.name}' has no bot reference")
        
        behavior_needed = self.behavior_needed
        self._bot.scope(f"story {self.name}")
        return self._bot.execute(behavior_needed, action_name=action)

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

    def rename(self, name: str = None) -> dict:
        """Rename the node. Parameter 'name' for CLI compatibility."""
        if name is None or not name:
            raise ValueError('Node name cannot be empty')
        if name != name.strip():
            raise ValueError('Node name cannot be whitespace-only')
        
        invalid_chars = ['<', '>', '\\', '|', '*', '?', '"']
        found_invalid = [ch for ch in invalid_chars if ch in name]
        if found_invalid:
            chars_str = ', '.join(found_invalid)
            raise ValueError(f'Name contains invalid characters: {chars_str}')
        
        if hasattr(self, '_parent') and self._parent:
            for sibling in self._parent.children:
                if sibling is not self and sibling.name == name:
                    raise ValueError(f"Name '{name}' already exists among siblings")
        
        node_type = type(self).__name__
        old_name = self.name
        self.name = name
        
        # Save changes to disk
        self.save()
        
        return {'node_type': node_type, 'old_name': old_name, 'new_name': name, 'operation': 'rename'}

    def delete(self, cascade: bool = True) -> dict:
        """Delete this node. Always cascades to delete all children."""
        import time
        start_time = time.time()
        
        if not hasattr(self, '_parent') or not self._parent:
            raise ValueError('Cannot delete node without parent')
        
        node_type = type(self).__name__
        node_name = self.name
        parent = self._parent
        children_count = len(self._children)
        
        # Handle Story deletion from StoryGroup
        if isinstance(parent, StoryGroup):
            parent._children.remove(self)
            parent._resequence_children()
            
            # Save changes from PARENT
            parent.save()
            
            elapsed = time.time() - start_time
            print(f"[DELETE TIMING] Deleted {node_type} '{node_name}' in {elapsed:.3f}s")
            
            return {'node_type': node_type, 'node_name': node_name, 'operation': 'delete', 'children_deleted': children_count}
        
        # Always cascade delete
        self._children.clear()
        
        parent._children.remove(self)
        self._resequence_siblings()
        
        # Save changes from PARENT
        parent.save()
        
        elapsed = time.time() - start_time
        print(f"[DELETE TIMING] Deleted {node_type} '{node_name}' in {elapsed:.3f}s")
        
        return {'node_type': node_type, 'node_name': node_name, 'operation': 'delete', 'children_deleted': children_count}

    def move_to(self, target: Union[str, 'StoryNode'] = None, position: Optional[int] = None, at_position: Optional[int] = None) -> dict:
        """Move node to a different parent or reorder within same parent. Parameters 'target' and 'at_position' for CLI compatibility."""
        # Handle CLI parameter alias
        if at_position is not None and position is None:
            position = at_position
        
        # If no target specified, move within same parent (just reorder)
        if target is None:
            if not hasattr(self, '_parent') or not self._parent:
                raise ValueError('Cannot move node without parent')
            target = self._parent
        elif isinstance(target, str):
            # Resolve string target to actual node
            target = self._resolve_target_from_string(target)
        
        node_type = type(self).__name__
        node_name = self.name
        source_parent_name = self._parent.name if hasattr(self, '_parent') and self._parent else None
        target_parent_name = target.name
        
        # Check for circular reference first (before checking parent)
        if self._is_circular_reference(target):
            raise ValueError('Cannot move node to its own descendant - circular reference')
        
        if not hasattr(self, '_parent') or not self._parent:
            raise ValueError('Cannot move node without parent')
        
        # Check if moving Story within same SubEpic (Story._parent is StoryGroup, need to check grandparent)
        actual_parent = self._parent
        if isinstance(actual_parent, StoryGroup) and hasattr(actual_parent, '_parent'):
            actual_grandparent = actual_parent._parent
            if actual_grandparent == target:
                # Moving within same SubEpic
                if position is not None:
                    current_position = actual_parent._children.index(self)
                    if current_position != position:
                        actual_parent._children.remove(self)
                        adjusted_position = min(position, len(actual_parent._children))
                        actual_parent._children.insert(adjusted_position, self)
                        actual_parent._resequence_children()
                        
                        # Save changes to disk
                        self.save()
                else:
                    raise ValueError(f"Node '{self.name}' already exists under parent '{target.name}'")
                return {'node_type': node_type, 'node_name': node_name, 'source_parent': source_parent_name, 'target_parent': target_parent_name, 'position': position, 'operation': 'move'}
        
        if self._parent == target:
            if position is not None:
                current_position = self._parent.children.index(self)
                if current_position != position:
                    self._parent._children.remove(self)
                    adjusted_position = min(position, len(self._parent.children))
                    self._parent._children.insert(adjusted_position, self)
                    self._resequence_siblings()
                    
                    # Save changes to disk
                    self.save()
            else:
                raise ValueError(f"Node '{self.name}' already exists under parent '{target.name}'")
            return {'node_type': node_type, 'node_name': node_name, 'source_parent': source_parent_name, 'target_parent': target_parent_name, 'position': position, 'operation': 'move'}
        
        for existing_child in target.children:
            if existing_child.name == self.name:
                raise ValueError(f"Node '{self.name}' already exists under parent '{target.name}'")
        
        self._validate_hierarchy_rules(target)
        
        # CRITICAL: Stories MUST be inside StoryGroups, not directly in SubEpic/Epic
        actual_target = target
        if isinstance(self, Story) and isinstance(target, (SubEpic, Epic)):
            # Find or create a StoryGroup in the target
            story_groups = [child for child in target._children if isinstance(child, StoryGroup)]
            if story_groups:
                # Use the first StoryGroup
                actual_target = story_groups[0]
            else:
                # Create a new StoryGroup
                story_group = StoryGroup(
                    name='',
                    sequential_order=0.0,
                    group_type='and',
                    connector=None,
                    _parent=target,
                    _bot=self._bot
                )
                target._children.append(story_group)
                actual_target = story_group
        
        # Check if we need to move test class (Story moving between SubEpics)
        source_subepic = None
        target_subepic = None
        if isinstance(self, Story):
            _log(f"[move_to] Story '{self.name}' is being moved")
            
            # Find source SubEpic
            current = self._parent
            while current and not isinstance(current, SubEpic):
                if hasattr(current, '_parent'):
                    current = current._parent
                else:
                    break
            source_subepic = current if isinstance(current, SubEpic) else None
            
            if source_subepic:
                _log(f"[move_to] Source SubEpic: '{source_subepic.name}'")
            else:
                _log(f"[move_to] Source SubEpic: None")
            
            # Find target SubEpic
            current = actual_target
            while current and not isinstance(current, SubEpic):
                if hasattr(current, '_parent'):
                    current = current._parent
                else:
                    break
            target_subepic = current if isinstance(current, SubEpic) else None
            
            if target_subepic:
                _log(f"[move_to] Target SubEpic: '{target_subepic.name}'")
            else:
                _log(f"[move_to] Target SubEpic: None")
        
        # Perform the move
        _log(f"[move_to] BEFORE MOVE - actual_target type: {type(actual_target).__name__}, name: {actual_target.name}, children count: {len(actual_target._children)}")
        self._parent._children.remove(self)
        self._parent._resequence_siblings()
        old_parent = self._parent
        self._parent = actual_target
        if position is not None:
            adjusted_position = min(position, len(actual_target.children))
            _log(f"[move_to] INSERTING at position {adjusted_position}")
            actual_target._children.insert(adjusted_position, self)
        else:
            _log(f"[move_to] APPENDING to children (no position specified)")
            actual_target._children.append(self)
        _log(f"[move_to] AFTER MOVE - actual_target children count: {len(actual_target._children)}")
        actual_target._resequence_children()
        
        # Move test class if needed
        if isinstance(self, Story) and source_subepic and target_subepic and source_subepic != target_subepic:
            _log(f"[move_to] Story moving between different SubEpics")
            _log(f"[move_to] Story test_class: {self.test_class}")
            
            if self.test_class and hasattr(source_subepic, 'test_file') and hasattr(target_subepic, 'test_file'):
                _log(f"[move_to] Source test_file: {source_subepic.test_file}")
                _log(f"[move_to] Target test_file: {target_subepic.test_file}")
                
                if source_subepic.test_file and target_subepic.test_file:
                    from story_graph.test_class_mover import TestClassMover
                    
                    # Get absolute paths
                    if self._bot and hasattr(self._bot, 'bot_paths'):
                        workspace_dir = Path(self._bot.bot_paths.workspace_directory)
                        source_file = workspace_dir / 'test' / source_subepic.test_file
                        target_file = workspace_dir / 'test' / target_subepic.test_file
                        
                        _log(f"[move_to] Workspace dir: {workspace_dir}")
                        _log(f"[move_to] Source file: {source_file}")
                        _log(f"[move_to] Target file: {target_file}")
                        _log(f"[move_to] Source exists: {source_file.exists()}")
                        _log(f"[move_to] Target exists: {target_file.exists()}")
                        
                        # Move the test class
                        if source_file.exists() and target_file.exists():
                            _log(f"[move_to] Initiating test class move")
                            result = TestClassMover.move_class(source_file, target_file, self.test_class)
                            _log(f"[move_to] Test class move result: {result}")
                        else:
                            _log(f"[move_to] Skipping test class move - file(s) do not exist")
                    else:
                        _log(f"[move_to] Skipping test class move - bot or bot_paths not available")
                else:
                    _log(f"[move_to] Skipping test class move - test_file not set on source or target")
            else:
                _log(f"[move_to] No test class to move")
        else:
            if isinstance(self, Story):
                if not source_subepic or not target_subepic:
                    _log(f"[move_to] Not a SubEpic-to-SubEpic move")
                elif source_subepic == target_subepic:
                    _log(f"[move_to] Moving within same SubEpic")
        
        # Save changes to disk
        self.save()
        
        return {'node_type': node_type, 'node_name': node_name, 'source_parent': source_parent_name, 'target_parent': target_parent_name, 'position': position, 'operation': 'move'}

    def _is_circular_reference(self, potential_parent: 'StoryNode') -> bool:
        current = potential_parent
        while hasattr(current, '_parent') and current._parent:
            if current._parent == self:
                return True
            current = current._parent
        return False
    
    def _resolve_target_from_string(self, target_name: str) -> 'StoryNode':
        """Resolve a target node name to an actual node by searching from root.
        Supports both simple names and dotted paths like \"Epic1\".\"Child1\"
        """
        import re
        
        _log(f"[_resolve_target_from_string] RECEIVED target_name: '{target_name}' (type: {type(target_name)})")
        
        # Handle already-quoted paths from parameter parsing (e.g., "Epic1"."Child1")
        path_str = target_name
        if path_str.startswith('"') and '"."' in path_str:
            # Already in quoted format, use as-is
            _log(f"[_resolve_target_from_string] Detected quoted path format: '{path_str}'")
        # Check if this is a dotted path (e.g., Epic1.Child1 or story_graph."Epic1"."Child1")
        elif path_str.startswith('story_graph.'):
            path_str = path_str[len('story_graph.'):]
            _log(f"[_resolve_target_from_string] After stripping story_graph: '{path_str}'")
        
        # Parse quoted path segments (e.g., "Epic1"."Child1" -> ["Epic1", "Child1"])
        path_segments = re.findall(r'"([^"]+)"', path_str)
        _log(f"[_resolve_target_from_string] Extracted path_segments: {path_segments}")
        
        # Navigate to root (story_map)
        current = self
        while hasattr(current, '_parent') and current._parent:
            current = current._parent
            if not hasattr(current, '_parent'):  # Reached Epic level
                # Go one more level up to StoryMap if Epic has _bot
                if hasattr(current, '_bot') and current._bot and hasattr(current._bot, 'story_graph'):
                    story_map = current._bot.story_map
                    
                    # If we have path segments, navigate the path
                    if path_segments:
                        node = None
                        # Start from the first epic that matches
                        for epic in story_map.epics:
                            if epic.name == path_segments[0]:
                                node = epic
                                break
                        
                        if not node:
                            raise ValueError(f"Epic '{path_segments[0]}' not found in path: {target_name}")
                        
                        # Navigate through remaining segments
                        for segment in path_segments[1:]:
                            found = False
                            for child in node.children:
                                if child.name == segment:
                                    node = child
                                    found = True
                                    break
                            if not found:
                                raise ValueError(f"Node '{segment}' not found in path: {target_name}")
                        
                        return node
                    else:
                        # Simple name search (legacy behavior)
                        for epic in story_map.epics:
                            if epic.name == target_name:
                                return epic
                            # Search in epic's children recursively
                            found = self._search_node_recursive(epic, target_name)
                            if found:
                                return found
                break
        
        raise ValueError(f"Target '{target_name}' not found")
    
    def _search_node_recursive(self, node: 'StoryNode', name: str) -> Optional['StoryNode']:
        """Recursively search for a node by name"""
        for child in node.children:
            if child.name == name:
                return child
            found = self._search_node_recursive(child, name)
            if found:
                return found
        return None
    
    def move_to_position(self, position: int) -> dict:
        """Alias for move_to with only position (moves within same parent)"""
        return self.move_to(position=position)
    
    def move_after(self, sibling: Union[str, 'StoryNode']) -> dict:
        """Move this node to be positioned after the specified sibling.
        
        Args:
            sibling: Either the name of a sibling node or a StoryNode instance
            
        Returns:
            Dict with operation details including new position
        """
        # Handle Epic nodes (no _parent, managed by StoryMap)
        if isinstance(self, Epic):
            if not self._bot or not hasattr(self._bot, 'story_map'):
                raise ValueError('Cannot move epic without bot context')
            
            story_map = self._bot.story_map
            
            # Resolve sibling if it's a string
            if isinstance(sibling, str):
                target_sibling = None
                for epic in story_map._epics_list:
                    if epic.name == sibling:
                        target_sibling = epic
                        break
                if not target_sibling:
                    raise ValueError(f"Epic '{sibling}' not found in story map")
                sibling = target_sibling
            
            # Find current and target positions
            current_position = story_map._epics_list.index(self)
            sibling_position = story_map._epics_list.index(sibling)
            
            # Remove from current position
            story_map._epics_list.remove(self)
            
            # Insert after sibling (adjust position if we removed before the sibling)
            new_position = sibling_position if current_position > sibling_position else sibling_position
            story_map._epics_list.insert(new_position, self)
            
            # Update sequential order
            for idx, e in enumerate(story_map._epics_list):
                e.sequential_order = idx
            
            # Rebuild epics collection and save
            story_map._epics = EpicsCollection(story_map._epics_list)
            story_map.save()
            
            return {
                'node_type': 'Epic',
                'node_name': self.name,
                'operation': 'move_after',
                'sibling': sibling.name,
                'new_position': new_position
            }
        
        # Handle other node types (SubEpic, Story, etc.)
        if not hasattr(self, '_parent') or not self._parent:
            raise ValueError('Cannot move node without parent')
        
        # Resolve sibling if it's a string
        if isinstance(sibling, str):
            target_sibling = None
            for child in self._parent.children:
                if child.name == sibling:
                    target_sibling = child
                    break
            if not target_sibling:
                raise ValueError(f"Sibling '{sibling}' not found under parent '{self._parent.name}'")
            sibling = target_sibling
        
        # Verify sibling has same parent
        if not hasattr(sibling, '_parent') or sibling._parent != self._parent:
            raise ValueError(f"Node '{sibling.name}' is not a sibling of '{self.name}'")
        
        # Find position after the sibling
        sibling_position = self._parent.children.index(sibling)
        new_position = sibling_position + 1
        
        # Use move_to with the calculated position
        return self.move_to(position=new_position)

    def _validate_hierarchy_rules(self, target_parent: 'StoryNode') -> None:
        if isinstance(self, SubEpic) and isinstance(target_parent, SubEpic):
            for child in target_parent.children:
                if isinstance(child, (Story, StoryGroup)):
                    raise ValueError('Cannot move SubEpic to SubEpic with Stories')
        if isinstance(self, Story) and isinstance(target_parent, SubEpic):
            for child in target_parent.children:
                if isinstance(child, SubEpic):
                    raise ValueError('Cannot move Story to SubEpic with SubEpics')

    def _resequence_siblings(self) -> None:
        if hasattr(self, '_parent') and self._parent:
            self._parent._resequence_children()

    def _resequence_children(self) -> None:
        for idx, child in enumerate(self._children):
            if hasattr(child, 'sequential_order'):
                child.sequential_order = float(idx)

    def execute_action(self, action_name: str, parameters: Optional[Dict[str, Any]] = None) -> ActionResult:
        if self._bot is None:
            raise ValueError('Cannot execute action: node has no bot reference')
        available_actions = self._get_available_actions()
        if action_name not in available_actions:
            available_actions_list = ', '.join(available_actions)
            raise ValueError(f"Action '{action_name}' not found. Available actions: {available_actions_list}")
        self._validate_action_parameters(action_name, parameters)
        return ActionResult(success=True, action_name=action_name, data={'node': self.name, 'action': action_name})

    def _get_available_actions(self) -> List[str]:
        if hasattr(self, '_registered_actions'):
            return self._registered_actions
        if self._bot and hasattr(self._bot, 'behaviors'):
            return [behavior.name for behavior in self._bot.behaviors]
        return ['clarify', 'strategy', 'build', 'validate', 'render']

    def _validate_action_parameters(self, action_name: str, parameters: Optional[Dict[str, Any]]) -> None:
        if parameters is None:
            parameters = {}
        if isinstance(parameters, str):
            import json
            try:
                parameters = json.loads(parameters)
            except json.JSONDecodeError:
                raise ValueError(f'Invalid JSON parameters: {parameters}')
        required_params = {
            'build': ['output'],
            'validate': ['rules'],
            'render': ['format']
        }
        valid_values = {
            'render': {
                'format': ['markdown', 'json', 'html']
            }
        }
        # Check for invalid parameters first
        expected_params = required_params.get(action_name, [])
        for param in parameters:
            if param not in expected_params and action_name in required_params:
                expected_str = ', '.join(expected_params) if expected_params else 'none'
                raise ValueError(f'Invalid parameter: {param}. Expected: {expected_str}')
        # Then check for missing required parameters
        if action_name in required_params:
            for param in required_params[action_name]:
                if param not in parameters:
                    raise ValueError(f'Missing required parameter: {param}')
        # Finally check for invalid values
        if action_name in valid_values:
            for param, valid_list in valid_values[action_name].items():
                if param in parameters and parameters[param] not in valid_list:
                    valid_str = ', '.join(valid_list)
                    raise ValueError(f'Invalid {param} value: {parameters[param]}. Expected: {valid_str}')

@dataclass
class Epic(StoryNode):
    domain_concepts: Optional[List[DomainConcept]] = None

    def __post_init__(self):
        super().__post_init__()
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

    @property
    def sub_epics(self) -> List['SubEpic']:
        return [child for child in self.children if isinstance(child, SubEpic)]

    @property
    def behavior_needed(self) -> str:
        hierarchy = ['shape', 'exploration', 'scenarios', 'tests', 'code']
        
        sub_epics = self.sub_epics
        if not sub_epics:
            return 'shape'
        
        highest_behavior = 'code'
        
        for sub_epic in sub_epics:
            sub_epic_behavior = sub_epic.behavior_needed
            if hierarchy.index(sub_epic_behavior) < hierarchy.index(highest_behavior):
                highest_behavior = sub_epic_behavior
        
        return highest_behavior

    def create(self, name: Optional[str] = None, child_type: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        """Alias for create_child"""
        return self.create_child(name, child_type, position)
    
    def create_sub_epic(self, name: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        """Create SubEpic child"""
        return self.create_child(name, 'SubEpic', position)
    
    def create_child(self, name: Optional[str] = None, child_type: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        # Validate name is not empty
        if name is not None and not name.strip():
            raise ValueError("Child name cannot be empty")
            
        for child in self.children:
            if child.name == name:
                raise ValueError(f"Child with name '{name}' already exists")
        if child_type == 'SubEpic' or child_type is None:
            sequential_order = float(len(self._children)) if position is None else float(position)
            child = SubEpic(name=name or self._generate_unique_child_name(), sequential_order=sequential_order, _parent=self, _bot=self._bot)
        else:
            raise ValueError(f'Epic can only create SubEpic children, not {child_type}')
            
        if position is not None:
            adjusted_position = min(position, len(self._children))
            self._children.insert(adjusted_position, child)
            self._resequence_children()
        else:
            child.sequential_order = float(len(self._children))
            self._children.append(child)
        
        # Save changes to disk
        child.save()
        
        return child

    def _generate_unique_child_name(self, child_type: str = 'Child') -> str:
        counter = 1
        while True:
            name = f'{child_type}{counter}'
            if not any(child.name == name for child in self.children):
                return name
            counter += 1

    def delete(self, cascade: bool = True) -> dict:
        """Delete this epic from the story map. Always cascades to delete all children."""
        if not self._bot:
            raise ValueError('Cannot delete epic without bot context')
        
        story_map = self._bot.story_map
        return story_map.delete_epic(self.name)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], bot: Optional[Any]=None) -> 'Epic':
        domain_concepts = [DomainConcept.from_dict(dc) for dc in data.get('domain_concepts', [])]
        epic = cls(
            name=data.get('name', ''),
            domain_concepts=domain_concepts,
            behavior=data.get('behavior'),
            _bot=bot
        )
        for sub_epic_data in data.get('sub_epics', []):
            sub_epic = SubEpic.from_dict(sub_epic_data, parent=epic, bot=bot)
            epic._children.append(sub_epic)
        for story_group_data in data.get('story_groups', []):
            story_group = StoryGroup.from_dict(story_group_data, parent=epic, bot=bot)
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
        # Initialize test_file attribute (not a dataclass field to avoid signature issues)
        if not hasattr(self, 'test_file'):
            self.test_file = None

    @property
    def children(self) -> List['StoryNode']:
        """Return children, transparently exposing Stories from StoryGroups."""
        if self.has_stories and not self.has_subepics:
            # Pure stories case: aggregate all stories from all story groups
            stories = []
            for child in self._children:
                if isinstance(child, StoryGroup):
                    stories.extend(child.children)
            return stories
        elif self.has_stories and self.has_subepics:
            # Mixed case (violation state): return SubEpics + Stories from StoryGroups
            result = []
            for child in self._children:
                if isinstance(child, SubEpic):
                    result.append(child)
                elif isinstance(child, StoryGroup):
                    result.extend(child.children)
            return result
        return self._children
    
    def __getitem__(self, child_name: str) -> 'StoryNode':
        """Access child by name"""
        for child in self.children:
            if child.name == child_name:
                return child
        raise KeyError(f"Child '{child_name}' not found in SubEpic '{self.name}'")
    
    def __getitem__(self, child_name: str) -> 'StoryNode':
        """Access child by name"""
        for child in self.children:
            if child.name == child_name:
                return child
        raise KeyError(f"Child '{child_name}' not found in SubEpic '{self.name}'")

    @classmethod
    def from_dict(cls, data: Dict[str, Any], parent: Optional[StoryNode]=None, bot: Optional[Any]=None) -> 'SubEpic':
        sequential_order = data.get('sequential_order')
        if sequential_order is None:
            raise ValueError('SubEpic requires sequential_order')
        sub_epic = cls(
            name=data.get('name', ''),
            sequential_order=float(sequential_order),
            behavior=data.get('behavior'),
            _parent=parent,
            _bot=bot
        )
        sub_epic.test_file = data.get('test_file')
        for nested_sub_epic_data in data.get('sub_epics', []):
            nested_sub_epic = SubEpic.from_dict(nested_sub_epic_data, parent=sub_epic, bot=bot)
            sub_epic._children.append(nested_sub_epic)
        for story_group_data in data.get('story_groups', []):
            story_group = StoryGroup.from_dict(story_group_data, parent=sub_epic, bot=bot)
            sub_epic._children.append(story_group)
        return sub_epic

    @property
    def has_subepics(self) -> bool:
        return any(isinstance(child, SubEpic) for child in self._children)

    @property
    def has_stories(self) -> bool:
        return any(isinstance(child, (Story, StoryGroup)) for child in self._children)

    @property
    def behavior_needed(self) -> str:
        hierarchy = ['shape', 'exploration', 'scenarios', 'tests', 'code']
        
        if self.has_subepics:
            sub_epics = [child for child in self._children if isinstance(child, SubEpic)]
            if not sub_epics:
                return 'shape'
            
            highest_behavior = 'code'
            for sub_epic in sub_epics:
                sub_epic_behavior = sub_epic.behavior_needed
                if hierarchy.index(sub_epic_behavior) < hierarchy.index(highest_behavior):
                    highest_behavior = sub_epic_behavior
            
            return highest_behavior
        else:
            stories = [child for child in self.children if isinstance(child, Story)]
            
            if not stories:
                return 'shape'
            
            current_behavior = stories[0].behavior_needed
            
            for story in stories[1:]:
                current_behavior = story.get_behavior_needed(current_behavior)
            
            return current_behavior

    def create(self, name: Optional[str] = None, child_type: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        """Alias for create_child"""
        return self.create_child(name, child_type, position)
    
    def create_story(self, name: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        """Create Story child"""
        return self.create_child(name, 'Story', position)
    
    def create_sub_epic(self, name: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        """Create SubEpic child"""
        return self.create_child(name, 'SubEpic', position)
    
    def create_child(self, name: Optional[str] = None, child_type: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        # Validate name is not empty
        if name is not None and not name.strip():
            raise ValueError("Child name cannot be empty")
            
        if child_type is None:
            child_type = 'Story' if self.has_stories else 'SubEpic'
        
        if child_type == 'SubEpic':
            for child in self.children:
                if child.name == name:
                    raise ValueError(f"Child with name '{name}' already exists")
            if self.has_stories:
                raise ValueError('Cannot create SubEpic under SubEpic with Stories')
            sequential_order = float(len(self._children)) if position is None else float(position)
            child = SubEpic(name=name or self._generate_unique_child_name(), sequential_order=sequential_order, _parent=self, _bot=self._bot)
                
        elif child_type == 'Story':
            if self.has_subepics:
                raise ValueError('Cannot create Story under SubEpic with SubEpics')
            story_group = self._get_or_create_story_group()
                
            for existing_story in story_group.children:
                if existing_story.name == name:
                    raise ValueError(f"Child with name '{name}' already exists")
            sequential_order = float(len(story_group._children)) if position is None else float(position)
            child = Story(name=name or self._generate_unique_child_name('Story'), sequential_order=sequential_order, _parent=story_group, _bot=self._bot)
                
            if position is not None:
                adjusted_position = min(position, len(story_group._children))
                story_group._children.insert(adjusted_position, child)
                story_group._resequence_children()
            else:
                child.sequential_order = float(len(story_group._children))
                story_group._children.append(child)
            
            # Save changes to disk
            child.save()
            
            return child
        else:
            raise ValueError(f'SubEpic can only create SubEpic or Story children, not {child_type}')
        if position is not None:
            adjusted_position = min(position, len(self._children))
            self._children.insert(adjusted_position, child)
            self._resequence_children()
        else:
            child.sequential_order = float(len(self._children))
            self._children.append(child)
        
        # Save changes to disk
        child.save()
        
        return child

    def _get_or_create_story_group(self) -> 'StoryGroup':
        for child in self._children:
            if isinstance(child, StoryGroup):
                return child
        story_group = StoryGroup(name=f'{self.name} Stories', sequential_order=float(len(self._children)), _parent=self, _bot=self._bot)
        self._children.append(story_group)
        return story_group

    def _generate_unique_child_name(self, child_type: str = 'Child') -> str:
        if child_type == 'Story' or (hasattr(self, 'has_stories') and self.has_stories):
            story_group = self._get_or_create_story_group()
            counter = 1
            while True:
                name = f'{child_type}{counter}'
                if not any(child.name == name for child in story_group.children):
                    return name
                counter += 1
        else:
            counter = 1
            while True:
                name = f'{child_type}{counter}'
                if not any(child.name == name for child in self.children):
                    return name
                counter += 1

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
    def from_dict(cls, data: Dict[str, Any], parent: Optional[StoryNode]=None, bot: Optional[Any]=None) -> 'StoryGroup':
        """Create StoryGroup from dictionary data."""
        sequential_order = data.get('sequential_order', 0.0)
        group_type = data.get('type', 'and')
        connector = data.get('connector')
        story_group = cls(
            name='',  # StoryGroup doesn't have a name in the typical sense
            sequential_order=float(sequential_order),
            group_type=group_type,
            connector=connector,
            behavior=data.get('behavior'),
            _parent=parent,
            _bot=bot
        )
        for story_data in data.get('stories', []):
            story = Story.from_dict(story_data, parent=story_group, bot=bot)
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
    file_link: Optional[str] = None  # Link to story markdown file
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
    
    def __getitem__(self, child_name: str) -> 'StoryNode':
        """Access child by name"""
        for child in self.children:
            if child.name == child_name:
                return child
        raise KeyError(f"Child '{child_name}' not found in Story '{self.name}'")

    @property
    def scenarios(self) -> List['Scenario']:
        return [child for child in self._children if isinstance(child, Scenario)]

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
    
    def has_acceptance_criteria(self) -> bool:
        return len(self.acceptance_criteria) > 0
    
    def has_scenarios(self) -> bool:
        return len(self.scenarios) > 0
    
    def has_tests(self) -> bool:
        if self.test_class:
            return True
        
        for scenario in self.scenarios:
            if scenario.test_method:
                return True
        
        return False

    @property
    def all_scenarios_have_tests(self) -> bool:
        if not self.scenarios:
            return False
        
        # Check if all scenarios have test_method fields populated
        if not all(scenario.test_method for scenario in self.scenarios):
            return False
        
        # If no bot context, fall back to simple check
        if not self._bot or not hasattr(self._bot, 'bot_paths'):
            return True
        
        # Check if the test file actually exists
        # Need to get test file from story or parent sub-epic
        test_file = self.test_file
        test_class = self.test_class
        
        # If story doesn't have test_file/test_class, get from parent sub-epic
        if not test_file or not test_class:
            parent = self._parent
            while parent:
                if hasattr(parent, 'test_file') and parent.test_file:
                    test_file = parent.test_file
                    break
                parent = parent._parent if hasattr(parent, '_parent') else None
            
            # If still no test_file, tests don't exist
            if not test_file:
                return False
            
            # Use story's test_class if available
            if not test_class:
                test_class = self.test_class
        
        # Check if test file exists on disk
        from pathlib import Path
        workspace_dir = Path(self._bot.bot_paths.workspace_directory if hasattr(self._bot.bot_paths, 'workspace_directory') else '.')
        test_dir = workspace_dir / self._bot.bot_paths.test_path
        test_file_path = test_dir / test_file
        
        if not test_file_path.exists():
            return False
        
        # Check if test class exists in file
        if test_class:
            from utils import find_test_class_line
            if not find_test_class_line(test_file_path, test_class):
                return False
        
        return True
    
    @property
    def many_scenarios(self) -> int:
        return len(self.scenarios)
    
    @property
    def many_acceptance_criteria(self) -> int:
        return len(self.acceptance_criteria)
    
    @property
    def behavior_needed(self) -> str:
        return self.get_behavior_needed()
    
    def get_behavior_needed(self, behavior_already_needed: str = None) -> str:
        hierarchy = ['code', 'tests', 'scenarios', 'exploration']
        start_idx = 0 if behavior_already_needed is None else hierarchy.index(behavior_already_needed)
        
        if start_idx <= hierarchy.index('code'):
            if self.all_scenarios_have_tests:
                return 'code'
        
        if start_idx <= hierarchy.index('tests'):
            if self.many_scenarios > 0:
                return 'tests'
        
        if start_idx <= hierarchy.index('scenarios'):
            if self.many_acceptance_criteria > 0:
                return 'scenarios'
        
        return 'exploration'

    def create(self, name: Optional[str] = None, child_type: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        """Alias for create_child"""
        return self.create_child(name, child_type, position)
    
    def create_scenario(self, name: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        """Create Scenario child"""
        return self.create_child(name, 'Scenario', position)
    
    def create_acceptance_criteria(self, name: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        """Create AcceptanceCriteria child"""
        return self.create_child(name, 'AcceptanceCriteria', position)
    
    def create_child(self, name: Optional[str] = None, child_type: Optional[str] = None, position: Optional[int] = None) -> StoryNode:
        # Validate name is not empty
        if name is not None and not name.strip():
            raise ValueError("Child name cannot be empty")
            
        for child in self.children:
            if child.name == name:
                raise ValueError(f"Child with name '{name}' already exists")
        if child_type == 'Scenario' or child_type is None:
            sequential_order = float(len(self._filter_children_by_type(Scenario))) if position is None else float(position)
            child = Scenario(name=name or self._generate_unique_child_name(), sequential_order=sequential_order, _parent=self, _bot=self._bot)
        elif child_type == 'AcceptanceCriteria':
            sequential_order = float(len(self._filter_children_by_type(AcceptanceCriteria))) if position is None else float(position)
            child = AcceptanceCriteria(name=name or self._generate_unique_child_name(), text=name or self._generate_unique_child_name(), sequential_order=sequential_order, _parent=self, _bot=self._bot)
        else:
            raise ValueError(f'Story can only create Scenario or AcceptanceCriteria children, not {child_type}')
        if position is not None:
            adjusted_position = min(position, len(self._children))
            self._children.insert(adjusted_position, child)
            self._resequence_children()
        else:
            self._children.append(child)
        
        # Save changes to disk
        child.save()
        
        return child

    def _generate_unique_child_name(self, child_type: str = 'Child') -> str:
        counter = 1
        while True:
            name = f'{child_type}{counter}'
            if not any(child.name == name for child in self.children):
                return name
            counter += 1

    @classmethod
    def from_dict(cls, data: Dict[str, Any], parent: Optional[StoryNode]=None, bot: Optional[Any]=None) -> 'Story':
        sequential_order = data.get('sequential_order')
        if sequential_order is None:
            raise ValueError('Story requires sequential_order')
        users = [StoryUser.from_str(u) for u in data.get('users', [])]
        story = cls(
            name=data.get('name', ''),
            sequential_order=float(sequential_order),
            connector=data.get('connector'),
            story_type=data.get('story_type', 'user'),
            users=users,
            test_file=data.get('test_file'),
            test_class=data.get('test_class'),
            file_link=data.get('file_link'),
            behavior=data.get('behavior'),
            _parent=parent,
            _bot=bot
        )
        acceptance_criteria_data = data.get('acceptance_criteria', [])
        for idx, ac_data in enumerate(acceptance_criteria_data):
            ac = AcceptanceCriteria.from_dict(ac_data, index=idx, parent=story, bot=bot)
            story._children.append(ac)
        scenarios_data = data.get('scenarios', [])
        for idx, scenario_data in enumerate(scenarios_data):
            scenario = Scenario.from_dict(scenario_data, index=idx, parent=story, bot=bot)
            story._children.append(scenario)
        # Legacy support: merge scenario_outlines into scenarios
        scenario_outlines_data = data.get('scenario_outlines', [])
        for idx, scenario_outline_data in enumerate(scenario_outlines_data):
            scenario = Scenario.from_dict(scenario_outline_data, index=len(scenarios_data) + idx, parent=story, bot=bot)
            story._children.append(scenario)
        return story

@dataclass
class Scenario(StoryNode):
    sequential_order: float
    type: str = ''
    background: List[str] = field(default_factory=list)
    examples: Optional[Dict[str, Any]] = None
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
    def examples_columns(self) -> List[str]:
        """Return columns from examples table, or empty list if no examples."""
        if self.examples:
            return self.examples.get('columns', [])
        return []

    @property
    def examples_rows(self) -> List[List[str]]:
        """Return rows from examples table, or empty list if no examples."""
        if self.examples:
            return self.examples.get('rows', [])
        return []

    @property
    def has_examples(self) -> bool:
        """Check if this scenario has examples (data-driven testing)."""
        return self.examples is not None and len(self.examples.get('columns', [])) > 0

    @property
    def default_test_method(self) -> str:
        return StoryNode._generate_default_test_method_name(self.name)

    @property
    def behavior_needed(self) -> str:
        if not self.test_method:
            return 'tests'
        
        if not self._bot or not hasattr(self._bot, 'bot_paths'):
            return 'code' if self.test_method else 'tests'
        
        parent = self._parent
        while parent and not isinstance(parent, Story):
            parent = parent._parent if hasattr(parent, '_parent') else None
        
        if not parent:
            return 'code' if self.test_method else 'tests'
        
        test_file = parent.test_file
        test_class = parent.test_class
        
        if not test_file:
            sub_epic_parent = parent._parent
            while sub_epic_parent:
                if hasattr(sub_epic_parent, 'test_file') and sub_epic_parent.test_file:
                    test_file = sub_epic_parent.test_file
                    break
                sub_epic_parent = sub_epic_parent._parent if hasattr(sub_epic_parent, '_parent') else None
        
        if not test_file or not test_class:
            return 'tests'
        
        from pathlib import Path
        workspace_dir = Path(self._bot.bot_paths.workspace_directory if hasattr(self._bot.bot_paths, 'workspace_directory') else '.')
        test_dir = workspace_dir / self._bot.bot_paths.test_path
        test_file_path = test_dir / test_file
        
        if not test_file_path.exists():
            return 'tests'
        
        from utils import find_test_method_line
        if not find_test_method_line(test_file_path, self.test_method):
            return 'tests'
        
        return 'code'

    @classmethod
    def from_dict(cls, data: Dict[str, Any], index: int=0, parent: Optional[StoryNode]=None, bot: Optional[Any]=None) -> 'Scenario':
        sequential_order = float(data.get('sequential_order', index + 1))
        scenario = cls(name=data.get('name', ''), sequential_order=sequential_order, type=data.get('type', ''), background=data.get('background', []), examples=data.get('examples'), test_method=data.get('test_method'), _parent=parent, _bot=bot)
        cls._add_steps_to_node(scenario, cls._parse_steps_from_data(data.get('steps', '')))
        return scenario

# ScenarioOutline class has been removed - use Scenario with optional examples field instead

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
    def from_dict(cls, data: Union[str, Dict[str, Any]], index: int=0, parent: Optional[StoryNode]=None, bot: Optional[Any]=None) -> 'AcceptanceCriteria':
        if isinstance(data, str):
            text = data
            sequential_order = float(index + 1)
        else:
            text = data.get('description', data.get('text', ''))
            sequential_order = float(data.get('sequential_order', index + 1))
        return cls(name=text, text=text, sequential_order=sequential_order, _parent=parent, _bot=bot)

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

class EpicsCollection:
    
    def __init__(self, epics: List[Epic]):
        self._epics = epics
        self._epics_by_name = {epic.name: epic for epic in epics}
    
    def __getitem__(self, name: str) -> Epic:
        if name not in self._epics_by_name:
            raise KeyError(f'Epic "{name}" not found')
        return self._epics_by_name[name]
    
    def __iter__(self) -> Iterator[Epic]:
        return iter(self._epics)
    
    def __len__(self) -> int:
        return len(self._epics)

class StoryMap:

    def __init__(self, story_graph: Dict[str, Any], bot=None):
        self.story_graph = story_graph
        self._bot = bot
        self._epics_list: List[Epic] = []
        for epic_data in story_graph.get('epics', []):
            self._epics_list.append(Epic.from_dict(epic_data, bot=bot))
        self._epics = EpicsCollection(self._epics_list)

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
        return cls(story_graph, bot=bot)

    def save(self) -> None:
        """Save the story graph to disk."""
        if not self._bot or not hasattr(self._bot, 'bot_paths'):
            return  # Cannot save without bot context
        
        # Regenerate story_graph dict from in-memory tree (only once, right before saving)
        self.story_graph['epics'] = [self._epic_to_dict(e) for e in self._epics_list]
        
        story_graph_path = Path(self._bot.bot_paths.workspace_directory) / 'docs' / 'stories' / 'story-graph.json'
        with open(story_graph_path, 'w', encoding='utf-8') as f:
            json.dump(self.story_graph, f, indent=2, ensure_ascii=False)
        
        # Invalidate the bot's cached story_graph to force reload on next access
        if hasattr(self._bot, '_story_graph'):
            self._bot._story_graph = None

    def _set_bot_on_all_nodes(self, bot: Any) -> None:
        for epic in self._epics_list:
            epic._bot = bot
            for node in self.walk(epic):
                node._bot = bot

    @property
    def epics(self) -> EpicsCollection:
        return self._epics
    
    def __getitem__(self, epic_name: str) -> Epic:
        """Allow epic access by name: story_map['Epic Name']"""
        return self._epics[epic_name]

    def walk(self, node: StoryNode) -> Iterator[StoryNode]:
        yield node
        for child in node.children:
            yield from self.walk(child)

    @property
    def all_stories(self) -> List['Story']:
        stories = []
        for epic in self._epics_list:
            for node in self.walk(epic):
                if isinstance(node, Story):
                    stories.append(node)
        return stories

    @property
    def all_scenarios(self) -> List['Scenario']:
        scenarios = []
        for epic in self._epics_list:
            for node in self.walk(epic):
                if isinstance(node, Story):
                    scenarios.extend(node.scenarios)
        return scenarios

    @property
    def all_domain_concepts(self) -> List[DomainConcept]:
        concepts = []
        for epic in self._epics_list:
            if epic.domain_concepts:
                concepts.extend(epic.domain_concepts)
        return concepts

    def filter_by_epic_names(self, epic_names: set) -> 'StoryMap':
        filtered_epics = [e for e in self._epics_list if e.name in epic_names]
        filtered_graph = {'epics': [self._epic_to_dict(e) for e in filtered_epics]}
        return StoryMap(filtered_graph)

    def filter_by_story_names(self, story_names: set) -> List['Story']:
        stories = []
        for epic in self._epics_list:
            for node in self.walk(epic):
                if isinstance(node, Story) and node.name in story_names:
                    stories.append(node)
        return stories

    def find_node(self, node_name: str) -> Optional[StoryNode]:
        for epic in self._epics_list:
            if epic.name == node_name:
                return epic
            for child in epic.children:
                if child.name == node_name:
                    return child
                if hasattr(child, 'children'):
                    result = self._find_in_children(child, node_name)
                    if result:
                        return result
        return None
    
    def _find_in_children(self, node: StoryNode, name: str) -> Optional[StoryNode]:
        for child in node.children:
            if child.name == name:
                return child
            if hasattr(child, 'children'):
                result = self._find_in_children(child, name)
                if result:
                    return result
        return None
    
    def find_epic_by_name(self, epic_name: str) -> Optional[Epic]:
        for epic in self._epics_list:
            if epic.name == epic_name:
                return epic
        return None

    def find_story_by_name(self, story_name: str) -> Optional['Story']:
        for epic in self._epics_list:
            for node in self.walk(epic):
                if isinstance(node, Story) and node.name == story_name:
                    return node
        return None
    
    def create_epic(self, name: Optional[str] = None, position: Optional[int] = None) -> Epic:
        """Create a new Epic at the root level of the story map.
        
        Args:
            name: Name for the new Epic. If None, generates unique name (Epic1, Epic2, etc.)
            position: Position to insert the Epic. If None, adds to end. If exceeds count, adjusts to last position.
            
        Returns:
            The newly created Epic instance
            
        Raises:
            ValueError: If an Epic with the same name already exists or name is empty
        """
        # Validate name is not empty
        if name is not None and not name.strip():
            raise ValueError("Epic name cannot be empty")
        
        # Validate name uniqueness
        if name:
            for epic in self._epics_list:
                if epic.name == name:
                    raise ValueError(f"Epic with name '{name}' already exists")
        
        # Generate unique name if not provided
        if not name:
            name = self._generate_unique_epic_name()
        
        # Create Epic instance
        epic = Epic(name=name, domain_concepts=[], _bot=self._bot)
        
        # Add to epics list at specified position
        if position is not None:
            adjusted_position = min(position, len(self._epics_list))
            self._epics_list.insert(adjusted_position, epic)
        else:
            self._epics_list.append(epic)
        
        # Set sequential_order based on position in list
        for idx, e in enumerate(self._epics_list):
            e.sequential_order = idx
        
        # Rebuild epics collection with new epic
        self._epics = EpicsCollection(self._epics_list)
        
        # Save to disk (save() will regenerate dict)
        self.save()
        
        return epic
    
    def delete_epic(self, name: str) -> Dict[str, Any]:
        """Delete an epic from the story map. Always cascades to delete all children.
        
        Args:
            name: Name of the epic to delete
            
        Returns:
            Dict with operation details
            
        Raises:
            ValueError: If epic not found
        """
        # Find the epic
        epic_to_delete = None
        for epic in self._epics_list:
            if epic.name == name:
                epic_to_delete = epic
                break
        
        if not epic_to_delete:
            raise ValueError(f"Epic '{name}' not found")
        
        children_count = len(epic_to_delete._children)
        
        # Remove from list (cascade delete of all children)
        self._epics_list.remove(epic_to_delete)
        
        # Update sequential order
        for idx, e in enumerate(self._epics_list):
            e.sequential_order = idx
        
        # Rebuild epics collection
        self._epics = EpicsCollection(self._epics_list)
        
        # Save to disk (save() will regenerate dict)
        self.save()
        
        return {
            'node_type': 'Epic',
            'node_name': name,
            'operation': 'delete',
            'children_deleted': children_count
        }
    
    def _generate_unique_epic_name(self) -> str:
        """Generate a unique Epic name (Epic1, Epic2, etc.)"""
        counter = 1
        while True:
            name = f'Epic{counter}'
            if not any(epic.name == name for epic in self._epics_list):
                return name
            counter += 1

    def _epic_to_dict(self, epic: Epic) -> Dict[str, Any]:
        result = {
            'name': epic.name,
            'sequential_order': epic.sequential_order,
            'behavior': epic.behavior,  # Always include behavior (even if None)
            'domain_concepts': [dc.__dict__ for dc in epic.domain_concepts] if epic.domain_concepts else [],
            'sub_epics': [self._sub_epic_to_dict(child) for child in epic.children if isinstance(child, SubEpic)],
            'story_groups': [self._story_group_to_dict(child) for child in epic.children if isinstance(child, StoryGroup)]
        }
        return result

    def _sub_epic_to_dict(self, sub_epic: SubEpic) -> Dict[str, Any]:
        # Stories are ONLY serialized in story_groups, not duplicated in a flattened array
        result = {
            'name': sub_epic.name,
            'sequential_order': sub_epic.sequential_order,
            'behavior': sub_epic.behavior,  # Always include behavior (even if None)
        }
        
        # Include test_file if present (critical for test links in panel)
        if sub_epic.test_file is not None:
            result['test_file'] = sub_epic.test_file
        
        result.update({
            'sub_epics': [self._sub_epic_to_dict(child) for child in sub_epic._children if isinstance(child, SubEpic)],
            'story_groups': [self._story_group_to_dict(child) for child in sub_epic._children if isinstance(child, StoryGroup)]
        })
        
        return result

    def _story_group_to_dict(self, story_group: StoryGroup) -> Dict[str, Any]:
        result = {
            'name': story_group.name,
            'sequential_order': story_group.sequential_order,
            'type': story_group.group_type,
            'connector': story_group.connector,
            'behavior': story_group.behavior,  # Always include behavior (even if None)
            'stories': [self._story_to_dict(child) for child in story_group.children if isinstance(child, Story)]
        }
        return result

    def _story_to_dict(self, story: Story) -> Dict[str, Any]:
        # Extract children by type
        scenarios = []
        acceptance_criteria = []
        
        for child in story._children:
            if isinstance(child, Scenario):
                scenarios.append(self._scenario_to_dict(child))
            elif isinstance(child, AcceptanceCriteria):
                acceptance_criteria.append(self._acceptance_criteria_to_dict(child))
        
        result = {
            'name': story.name,
            'sequential_order': story.sequential_order,
            'connector': story.connector,
            'story_type': story.story_type,
            'users': [str(u) for u in story.users] if story.users else [],
            'test_file': story.test_file,
            'test_class': story.test_class,
            'scenarios': scenarios,
            'acceptance_criteria': acceptance_criteria,
            'behavior': story.behavior  # Always include behavior (even if None)
        }
        if story.file_link is not None:
            result['file_link'] = story.file_link
        return result
    
    def _scenario_to_dict(self, scenario: Scenario) -> Dict[str, Any]:
        # Convert Step objects to newline-separated string
        steps_text = '\n'.join(step.text for step in scenario.steps) if scenario.steps else ''
        result = {
            'name': scenario.name,
            'sequential_order': scenario.sequential_order,
            'type': scenario.type,
            'background': scenario.background,
            'test_method': scenario.test_method,
            'steps': steps_text
        }
        # Only include examples if present
        if scenario.examples:
            result['examples'] = scenario.examples
        return result
    
    def _acceptance_criteria_to_dict(self, ac: AcceptanceCriteria) -> Dict[str, Any]:
        return {
            'name': ac.name,
            'text': ac.text,
            'sequential_order': ac.sequential_order
        }
    
    
    def _calculate_story_file_link(self, story: Story) -> str:
        """Calculate the file path for a story's markdown file."""
        if not self._bot or not hasattr(self._bot, 'bot_paths'):
            return ''
        
        # Build path: docs/stories/map/Epic/SubEpic/.../Story.md
        path_parts = []
        current = story
        
        # Walk up to collect all parent names
        while hasattr(current, '_parent') and current._parent:
            current = current._parent
            if isinstance(current, (Epic, SubEpic)):
                path_parts.insert(0, current.name)
        
        # Add story name
        path_parts.append(f"📄 {story.name}.md")
        
        # Build full path
        from pathlib import Path
        docs_path = Path(self._bot.bot_paths.workspace_directory) / 'docs' / 'stories' / 'map'
        story_path = docs_path
        for part in path_parts:
            story_path = story_path / part
        
        return str(story_path)
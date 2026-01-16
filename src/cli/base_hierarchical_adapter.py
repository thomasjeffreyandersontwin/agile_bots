from abc import ABC, abstractmethod
from typing import List, Optional
from agile_bots.src.cli.adapter_factory import AdapterFactory

class BaseHierarchicalAdapter(ABC):
    def __init__(self, domain_object, channel: str, factory: Optional[AdapterFactory] = None):
        self.domain_object = domain_object
        self.channel = channel
        self.factory = factory or AdapterFactory
        self._build_wrapped_hierarchy()

    @abstractmethod
    def _build_wrapped_hierarchy(self):
        pass

    @abstractmethod
    def serialize(self) -> str:
        pass

class BaseBotAdapter(BaseHierarchicalAdapter):
    def __init__(self, bot, channel: str):
        self.bot = bot
        self._behaviors_adapter = None
        super().__init__(bot, channel)

    def _build_wrapped_hierarchy(self):
        if self.bot.behaviors:
            self._behaviors_adapter = self.factory.create(
                self.bot.behaviors,
                self.channel
            )

    def serialize(self) -> str:
        lines = []
        lines.append(self.format_header())
        lines.append(self.format_bot_info())
        if self._behaviors_adapter:
            lines.append(self._behaviors_adapter.serialize())
        lines.append(self.format_footer())
        return '\n'.join(lines)

    @abstractmethod
    def format_header(self) -> str:
        pass

    @abstractmethod
    def format_bot_info(self) -> str:
        pass

    @abstractmethod
    def format_footer(self) -> str:
        pass

class BaseBehaviorsAdapter(BaseHierarchicalAdapter):
    def __init__(self, behaviors, channel: str):
        self.behaviors = behaviors
        self._behavior_adapters: List = []
        super().__init__(behaviors, channel)

    def _build_wrapped_hierarchy(self):
        current_behavior_name = (
            self.behaviors.current.name
            if self.behaviors.current
            else None
        )
        sorted_behaviors = sorted(list(self.behaviors), key=lambda b: b.order)

        for behavior in sorted_behaviors:
            is_current = behavior.name == current_behavior_name
            behavior_adapter = self.factory.create(behavior, self.channel)
            behavior_adapter.is_current = is_current
            if hasattr(behavior_adapter, 'behavior'):
                behavior_adapter.behavior = behavior
            self._behavior_adapters.append(behavior_adapter)

    def serialize(self) -> str:
        lines = []
        for behavior_adapter in self._behavior_adapters:
            lines.append(behavior_adapter.serialize())
        return '\n'.join(lines)

class BaseBehaviorAdapter(BaseHierarchicalAdapter):
    def __init__(self, behavior, channel: str, is_current: bool = False):
        self.behavior = behavior
        self.is_current = is_current
        self._actions_adapter = None
        super().__init__(behavior, channel)

    def _build_wrapped_hierarchy(self):
        if self.behavior.actions:
            self._actions_adapter = self.factory.create(
                self.behavior.actions,
                self.channel
            )
            if hasattr(self._actions_adapter, '_set_current_behavior'):
                self._actions_adapter._set_current_behavior(self.behavior)

    def serialize(self) -> str:
        lines = []
        lines.append(self.format_behavior_name())
        if self.is_current and self._actions_adapter:
            actions_output = self._actions_adapter.serialize()
            lines.append(self._indent_actions(actions_output))
        return '\n'.join(lines)

    @abstractmethod
    def format_behavior_name(self) -> str:
        pass

    def _indent_actions(self, actions_output: str) -> str:
        return '\n'.join(f"    {line}" if line else "" for line in actions_output.split('\n'))

class BaseActionsAdapter(BaseHierarchicalAdapter):
    def __init__(self, actions, channel: str):
        self.actions = actions
        self._action_adapters: List = []
        self._current_behavior = None
        super().__init__(actions, channel)

    def _set_current_behavior(self, behavior):
        self._current_behavior = behavior

    def _build_wrapped_hierarchy(self):
        current_action_name = (
            self.actions.current.action_name
            if self.actions.current
            else None
        )
        for action in self.actions:
            is_current = action.action_name == current_action_name
            is_completed = self.actions.is_action_completed(action.action_name)
            action_adapter = self.factory.create(action, self.channel, is_current=is_current, is_completed=is_completed)
            if hasattr(action_adapter, 'action'):
                action_adapter.action = action
            elif not hasattr(action_adapter, 'action'):
                action_adapter.action = action
            self._action_adapters.append(action_adapter)

    def serialize(self) -> str:
        lines = []
        for action_adapter in self._action_adapters:
            lines.append(action_adapter.serialize())
        return '\n'.join(lines)

"""
Navigation Test Helper - Domain navigation logic (format-agnostic)

Handles navigation operations: moving between behaviors and actions,
asserting current position. This is domain logic, not CLI-specific.
"""
from helpers.base_helper import BaseHelper


class NavigationTestHelper(BaseHelper):
    """Helper for navigation operations - format-agnostic domain logic"""
    
    def navigate_to(self, behavior: str, action: str):
        """
        Navigate bot to specific behavior and action.
        
        Args:
            behavior: Behavior name to navigate to
            action: Action name to navigate to
        """
        self.parent.bot.behaviors.navigate_to(behavior)
        self.parent.bot.behaviors.current.actions.navigate_to(action)
    
    def navigate_next(self):
        """
        Navigate to next action in workflow.
        
        Returns:
            Result of navigation operation
        """
        return self.parent.bot.next()
    
    def navigate_back(self):
        """
        Navigate to previous action in workflow.
        
        Returns:
            Result of navigation operation
        """
        return self.parent.bot.back()
    
    def assert_at_position(self, behavior: str, action: str):
        """
        Assert bot is at specific behavior and action.
        
        Args:
            behavior: Expected behavior name
            action: Expected action name
        """
        assert self.parent.bot.behaviors.current.name == behavior, \
            f"Expected behavior '{behavior}', got '{self.parent.bot.behaviors.current.name}'"
        assert self.parent.bot.behaviors.current.actions.current_action_name == action, \
            f"Expected action '{action}', got '{self.parent.bot.behaviors.current.actions.current_action_name}'"

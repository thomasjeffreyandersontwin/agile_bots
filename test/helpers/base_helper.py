"""
Base Test Helper

Base class for all domain-specific test helpers.
Provides parent reference pattern for accessing shared resources.
"""
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from helpers.bot_test_helper import BotTestHelper


class BaseTestHelper:
    """Base class for all test helpers with parent reference pattern."""
    
    def __init__(self, parent: 'BotTestHelper'):
        """Initialize with parent reference.
        
        Args:
            parent: Parent BotTestHelper instance providing access to bot, workspace, etc.
        """
        self.parent = parent
    
    @property
    def bot(self):
        """Access parent's bot instance."""
        return self.parent.bot
    
    @property
    def workspace(self) -> Path:
        """Access parent's workspace directory."""
        return self.parent.workspace
    
    @property
    def bot_directory(self) -> Path:
        """Access parent's bot directory."""
        return self.parent.bot_directory


# Alias for convenience
BaseHelper = BaseTestHelper

"""
Base CLI Bot Test Helper - Creates domain helper internally

This is the base class for all CLI channel helpers (TTY, Pipe, JSON).
It creates the domain BotTestHelper internally and sets up the CLI session.
"""
from pathlib import Path
from cli.cli_session import CLISession
from domain.bot_test_helper import BotTestHelper


class CLIBotTestHelper:
    """Base class for all CLI channel helpers - manages domain helper and CLI session"""
    
    def __init__(self, tmp_path: Path, mode: str):
        """
        Initialize CLI helper with domain helper and CLI session.
        
        Args:
            tmp_path: Test temporary directory
            mode: CLI mode ('tty', 'pipe', or 'json')
        """
        # Create domain helper internally (encapsulation)
        self.domain = BotTestHelper(tmp_path)
        
        # Create CLI session with proper mode
        self.cli_session = CLISession(
            bot=self.domain.bot,
            workspace_directory=self.domain.workspace,
            mode=mode
        )
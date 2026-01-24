
import json
import os
from pathlib import Path

from bot.bot import Bot
# Core helpers (in test/helpers/)
from .state_helper import StateTestHelper
from .file_helper import FileTestHelper

# SubEpic-specific helpers (organized by feature, in each SubEpic folder)
from invoke_bot.edit_story_map.story_helper import StoryTestHelper
from invoke_bot.edit_story_map.scope_helper import ScopeTestHelper
from invoke_bot.initialize_bot.behavior_helper import BehaviorTestHelper
from invoke_bot.navigate_behavior_actions.navigation_helper import NavigationTestHelper
from invoke_bot.navigate_behavior_actions.activity_helper import ActivityTestHelper
from invoke_bot.perform_action.guardrails_helper import GuardrailsTestHelper
from invoke_bot.perform_action.clarify_helper import ClarifyTestHelper
from invoke_bot.perform_action.strategy_helper import StrategyTestHelper
from invoke_bot.perform_action.build_helper import BuildTestHelper
from invoke_bot.perform_action.validate_helper import ValidateTestHelper
from invoke_bot.perform_action.rules_helper import RulesTestHelper
from invoke_bot.perform_action.render_helper import RenderTestHelper
from invoke_bot.perform_action.instructions_helper import InstructionsTestHelper
class BotTestHelper:
    """
    Test helper that provides production story_bot and workspace.
    
    All domain-specific methods are accessible through sub-helpers:
    - helper.state.set_state()
    - helper.behaviors.navigate_to()
    - helper.story.create_story_graph()
    - etc.
    """
    
    def __init__(self, tmp_path: Path, workspace_directory: Path = None, bot_directory: Path = None):
        """Initialize with production story_bot and temp workspace.
        
        Args:
            tmp_path: Temporary directory path (pytest fixture)
            workspace_directory: Optional workspace directory (defaults to tmp_path / 'workspace')
            bot_directory: Optional custom bot directory (defaults to production story_bot)
        """
        if bot_directory is not None:
            self.bot_directory = bot_directory
            self.bot_directory.mkdir(parents=True, exist_ok=True)
        else:
            repo_root = Path(__file__).parent.parent.parent.parent
            self.bot_directory = repo_root / 'agile_bots' / 'bots' / 'story_bot'
        
        self.workspace = workspace_directory if workspace_directory is not None else tmp_path / 'workspace'
        self.workspace.mkdir(parents=True, exist_ok=True)

        os.environ['BOT_DIRECTORY'] = str(self.bot_directory)
        os.environ['WORKING_AREA'] = str(self.workspace)
        
        if bot_directory is not None:
            config_path = self.bot_directory / 'bot_config.json'
            if not config_path.exists():
                import json
                config_data = {
                    'botName': 'story_bot',
                    'behaviors': []
                }
                config_path.write_text(json.dumps(config_data, indent=2), encoding='utf-8')
        else:
            config_path = self.bot_directory / 'bot_config.json'
            if not config_path.exists():
                config_path = self.bot_directory / 'config' / 'bot_config.json'
        
        self.bot = Bot(
            bot_name='story_bot',
            bot_directory=self.bot_directory,
            config_path=config_path
        )
        
        self.state = StateTestHelper(parent=self)
        self.behaviors = BehaviorTestHelper(parent=self)
        self.navigation = NavigationTestHelper(parent=self)
        self.guardrails = GuardrailsTestHelper(parent=self)
        self.clarify = ClarifyTestHelper(parent=self)
        self.strategy = StrategyTestHelper(parent=self)
        self.build = BuildTestHelper(parent=self)
        self.validate = ValidateTestHelper(parent=self)
        self.rules = RulesTestHelper(parent=self)
        self.render = RenderTestHelper(parent=self)
        self.activity = ActivityTestHelper(parent=self)
        self.story = StoryTestHelper(parent=self)
        self.scope = ScopeTestHelper(parent=self)
        self.instructions = InstructionsTestHelper(parent=self)
        self.files = FileTestHelper(parent=self)
    
    def setup_custom_bot_directory(self, bot_directory: Path = None, workspace_directory: Path = None):
        """Set up a custom bot directory for testing (instead of production story_bot).
        
        Args:
            bot_directory: Custom bot directory to use (defaults to tmp_path / 'bot' if use_custom_bot was True)
            workspace_directory: Optional workspace directory (defaults to self.workspace)
        """
        if bot_directory:
            self.bot_directory = bot_directory
        elif not hasattr(self, 'bot_directory') or self.bot_directory is None:
            from pathlib import Path as P
            tmp_path = self.workspace.parent if self.workspace.name == 'workspace' else self.workspace
            self.bot_directory = tmp_path / 'bot'
        
        self.bot_directory.mkdir(parents=True, exist_ok=True)
        
        if workspace_directory:
            self.workspace = workspace_directory
            self.workspace.mkdir(parents=True, exist_ok=True)
        
        os.environ['BOT_DIRECTORY'] = str(self.bot_directory)
        os.environ['WORKING_AREA'] = str(self.workspace)
        
        if self.bot is None:
            config_path = self.bot_directory / 'bot_config.json'
            if not config_path.exists():
                config_path = self.bot_directory / 'config' / 'bot_config.json'
            
            if config_path.exists():
                self.bot = Bot(
                    bot_name='story_bot',
                    bot_directory=self.bot_directory,
                    config_path=config_path
                )

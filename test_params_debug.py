import sys
sys.path.insert(0, 'C:/dev/agile_bots/src')
sys.path.insert(0, 'C:/dev/agile_bots/test')
import os
os.environ['BOT_DIRECTORY'] = 'C:/dev/agile_bots/bots/story_bot'
os.environ['WORKING_AREA'] = 'C:/dev/agile_bots'

from bot.bot import Bot
from pathlib import Path

bot = Bot(
    bot_name='story_bot',
    bot_directory=Path('C:/dev/agile_bots/bots/story_bot'),
    config_path=Path('C:/dev/agile_bots/bots/story_bot/bot_config.json')
)

from navigation.domain_navigator import DomainNavigator

nav = DomainNavigator(bot)

# Test parsing parameters
command = 'story_graph.create_epic name:"Test Epic"'
command_part, params_part = nav._split_command_and_params(command)
params = nav._parse_parameters(params_part)

print(f"Command: {command}")
print(f"Command part: {command_part}")
print(f"Params part: {params_part}")
print(f"Parsed params: {params}")
print(f"Params type: {type(params)}")
print(f"Params keys: {list(params.keys())}")

# Try to call it
print("\n=== Attempting to call create_epic ===")
try:
    result = bot.story_graph.create_epic(**params)
    print(f"SUCCESS: {result}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

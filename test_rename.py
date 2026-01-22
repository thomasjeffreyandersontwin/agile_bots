from src.navigation.domain_navigator import DomainNavigator
from src.bot.bot import Bot

bot = Bot.initialize('C:/dev/agile_bots/bots/story_bot')
nav = DomainNavigator(bot)

# Test rename with spaces
command = 'story_graph."Build Agile Bots".rename new_name:"Test Name With Spaces"'
print(f"Command: {command}")

try:
    result = nav.execute(command)
    print(f"Success: {result}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

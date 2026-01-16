"""
Story Bot MCP Server Entry Point

Runnable MCP server for story_bot using FastMCP with statically generated tools.
"""
from pathlib import Path
import sys
import os
import json
from datetime import datetime
import logging

python_workspace_root = Path(__file__).parent.parent.parent.parent.parent
if str(python_workspace_root) not in sys.path:
    sys.path.insert(0, str(python_workspace_root))

bot_directory = Path(__file__).parent.parent
os.environ['BOT_DIRECTORY'] = str(bot_directory)

if 'WORKING_AREA' not in os.environ:
    config_path = bot_directory / 'bot_config.json'
    if config_path.exists():
        bot_config = json.loads(config_path.read_text(encoding='utf-8'))
        if 'mcp' in bot_config and 'env' in bot_config['mcp']:
            mcp_env = bot_config['mcp']['env']
            if 'WORKING_AREA' in mcp_env:
                os.environ['WORKING_AREA'] = mcp_env['WORKING_AREA']

from agile_bots.bots.base_bot.src.bot.workspace import (
    get_bot_directory,
    get_workspace_directory,
    get_python_workspace_root
)
from agile_bots.bots.base_bot.src.bot.bot import Bot, BotResult
from agile_bots.bots.base_bot.src.mcp.server_restart import restart_mcp_server
from fastmcp import FastMCP

logger = logging.getLogger(__name__)

def main():
    """Main entry point for story_bot MCP server.

    Environment variables are bootstrapped before import:
    - BOT_DIRECTORY: Self-detected from script location
    - WORKING_AREA: Read from bot_config.json (or overridden by mcp.json env)
    
    All subsequent code reads from these environment variables.
    """
    bot_directory = get_bot_directory()
    workspace_directory = get_workspace_directory()
    
    bot = Bot(bot_name='story_bot', bot_directory=bot_directory, config_path=bot_directory / 'bot_config.json')
    
    server_name = 'story_bot'
    mcp_server = FastMCP(server_name)
    
        @mcp_server.tool(name='tool', description='Bot tool for story_bot - routes to current behavior and action.')
    async def bot_tool(parameters: dict=None):
        current_behavior = bot.behaviors.current
        if current_behavior is None:
            if bot.behaviors.first:
                bot.behaviors.navigate_to(bot.behaviors.first.name)
                current_behavior = bot.behaviors.current
            else:
                raise ValueError('No behaviors available')
        if current_behavior is None:
            raise ValueError('No current behavior')
        action = current_behavior.actions.forward_to_current()
        result_data = action.execute(parameters or {})
        result = BotResult(status='completed', behavior=current_behavior.name, action=action.action_name, data=result_data)
        return {'status': result.status, 'behavior': result.behavior, 'action': result.action, 'data': result.data}

    @mcp_server.tool(name='get_working_dir', description="Get the current working directory from WORKING_AREA. Triggers: where are we working, what's my location, show working directory")
    async def get_working_dir(input_file: str=None, project_dir: str=None):
        working_dir = get_workspace_directory()
        return {'working_dir': str(working_dir), 'message': f'Working directory from WORKING_AREA: {working_dir}'}

    @mcp_server.tool(name='set_working_dir', description="Update the working directory (WORKING_AREA). Triggers: update working directory, change working path, change working folder, set workspace")
    async def set_working_dir(new_path: str, persist: bool=True):
        if not new_path:
            return {'error': 'missing_path', 'message': 'new_path is required'}
        try:
            previous = str(bot.bot_paths.workspace_directory)
        except Exception:
            previous = None
        try:
            resolved = str(bot.bot_paths.update_workspace_directory(new_path, persist=persist))
            return {'working_dir': resolved, 'previous_working_dir': previous, 'persisted': bool(persist), 'message': f'Working directory updated to {resolved}'}
        except Exception as e:
            logger.error(f'Failed to set working directory: {e}', exc_info=True)
            return {'error': 'failed_to_set_working_dir', 'message': str(e)}

    @mcp_server.tool(name='close_current_action', description='Close current action tool for story_bot - marks current action complete and transitions to next')
    async def close_current_action(parameters: dict=None):
        state_file = bot.bot_paths.workspace_directory / 'behavior_action_state.json'
        if not state_file.exists():
            return {'error': 'No active state found', 'message': 'No behavior_action_state.json exists. Start a behavior first.'}
        try:
            current_behavior = bot.behaviors.current
            current_behavior.actions.load_state()
            current_action = current_behavior.actions.current
            action_name = current_action.action_name
            action_names = current_behavior.actions.names
            is_final_action = action_name == action_names[-1] if action_names else False
            current_behavior.actions.close_current()
            new_action = current_behavior.actions.current
            behavior_complete = new_action is None or (is_final_action and new_action.action_name == action_name)
            if behavior_complete:
                next_behavior = bot.behaviors.next()
                if next_behavior:
                    bot.behaviors.navigate_to(next_behavior.name)
                    next_behavior.actions.load_state()
                    first_action = next_behavior.actions.current.action_name if next_behavior.actions.current else 'clarify'
                    return {'status': 'completed', 'completed_action': action_name, 'completed_behavior': current_behavior.name, 'next_behavior': next_behavior.name, 'next_action': first_action, 'message': f"Behavior '{current_behavior.name}' complete. Transitioned to behavior '{next_behavior.name}', action '{first_action}'."}
                return {'status': 'completed', 'completed_action': action_name, 'completed_behavior': current_behavior.name, 'message': f"Action '{action_name}' marked complete. All behaviors complete."}
            new_action_name = current_behavior.actions.current.action_name if current_behavior.actions.current else None
            return {'status': 'completed', 'completed_action': action_name, 'next_action': new_action_name, 'message': f"Action '{action_name}' marked complete. Transitioned to '{new_action_name}'."}
        except Exception as e:
            return {'error': 'Failed to close current action', 'message': str(e)}

    @mcp_server.tool(name='confirm_out_of_order', description='Confirm out-of-order behavior execution for story_bot - MUST be called explicitly by HUMAN USER, NOT by AI assistant. AI must ask user to call this tool, never call it directly.')
    async def confirm_out_of_order(behavior: str):
        working_dir = get_workspace_directory()
        state_file = working_dir / 'behavior_action_state.json'
        try:
            state_data = json.loads(state_file.read_text(encoding='utf-8'))
            if 'out_of_order_confirmations' not in state_data:
                state_data['out_of_order_confirmations'] = {}
            state_data['out_of_order_confirmations'][behavior] = {'confirmed_at': datetime.now().isoformat(), 'confirmed_by': 'human'}
            state_file.write_text(json.dumps(state_data, indent=2), encoding='utf-8')
            return {'status': 'confirmed', 'behavior': behavior, 'message': f"Out-of-order execution confirmed for behavior '{behavior}'. You may now execute this behavior.", 'confirmed_at': state_data['out_of_order_confirmations'][behavior]['confirmed_at']}
        except Exception as e:
            return {'error': 'Failed to confirm out-of-order execution', 'message': str(e)}

    @mcp_server.tool(name='restart_server', description='Restart MCP server for story_bot - terminates processes, clears cache, and restarts to load code changes')
    async def restart_server(parameters: dict=None):
        try:
            workspace_root = get_python_workspace_root()
            bot_location = str(bot_directory.relative_to(workspace_root))
            result = restart_mcp_server(workspace_root=workspace_root, bot_name='story_bot', bot_location=bot_location)
            return result
        except Exception as e:
            logger.error(f'Failed to restart MCP server: {e}', exc_info=True)
            return {'status': 'error', 'error': 'Failed to restart server', 'message': str(e)}
    
        @mcp_server.tool(name='shape', description='shape behavior for story_bot. Accepts optional action parameter and parameters dict.
Trigger patterns: start.*shaping, let.*s.*shape, begin.*shaping, do.*shaping, shaping')
    async def shape_tool(action: str=None, parameters: dict=None):
        behavior_obj = bot.behaviors.find_by_name('shape')
        if action:
            action_obj = behavior_obj.actions.find_by_name(action)
            result_data = action_obj.execute(parameters or {})
            return {'status': 'completed', 'behavior': 'shape', 'action': action, 'data': result_data}
        behavior_obj.actions.load_state()
        current_action = behavior_obj.actions.current
        result_data = current_action.execute(parameters or {})
        return {'status': 'completed', 'behavior': 'shape', 'action': current_action.action_name, 'data': result_data}

    @mcp_server.tool(name='prioritization', description='prioritization behavior for story_bot. Accepts optional action parameter and parameters dict.
Trigger patterns: start.*prioritization, let.*s.*prioritize, begin.*prioritization, do.*prioritization, prioritization')
    async def prioritization_tool(action: str=None, parameters: dict=None):
        behavior_obj = bot.behaviors.find_by_name('prioritization')
        if action:
            action_obj = behavior_obj.actions.find_by_name(action)
            result_data = action_obj.execute(parameters or {})
            return {'status': 'completed', 'behavior': 'prioritization', 'action': action, 'data': result_data}
        behavior_obj.actions.load_state()
        current_action = behavior_obj.actions.current
        result_data = current_action.execute(parameters or {})
        return {'status': 'completed', 'behavior': 'prioritization', 'action': current_action.action_name, 'data': result_data}

    @mcp_server.tool(name='discovery', description='discovery behavior for story_bot. Accepts optional action parameter and parameters dict.
Trigger patterns: start.*discovery, let.*s.*discover, begin.*discovery, do.*discovery, discovery')
    async def discovery_tool(action: str=None, parameters: dict=None):
        behavior_obj = bot.behaviors.find_by_name('discovery')
        if action:
            action_obj = behavior_obj.actions.find_by_name(action)
            result_data = action_obj.execute(parameters or {})
            return {'status': 'completed', 'behavior': 'discovery', 'action': action, 'data': result_data}
        behavior_obj.actions.load_state()
        current_action = behavior_obj.actions.current
        result_data = current_action.execute(parameters or {})
        return {'status': 'completed', 'behavior': 'discovery', 'action': current_action.action_name, 'data': result_data}

    @mcp_server.tool(name='exploration', description='exploration behavior for story_bot. Accepts optional action parameter and parameters dict.
Trigger patterns: start.*exploration, let.*s.*explore, begin.*exploration, do.*exploration, exploration')
    async def exploration_tool(action: str=None, parameters: dict=None):
        behavior_obj = bot.behaviors.find_by_name('exploration')
        if action:
            action_obj = behavior_obj.actions.find_by_name(action)
            result_data = action_obj.execute(parameters or {})
            return {'status': 'completed', 'behavior': 'exploration', 'action': action, 'data': result_data}
        behavior_obj.actions.load_state()
        current_action = behavior_obj.actions.current
        result_data = current_action.execute(parameters or {})
        return {'status': 'completed', 'behavior': 'exploration', 'action': current_action.action_name, 'data': result_data}

    @mcp_server.tool(name='scenarios', description='scenarios behavior for story_bot. Accepts optional action parameter and parameters dict.
Trigger patterns: specify.*scenarios, *specification, write.*scenarios, define.*test.*scenario, write.*details')
    async def scenarios_tool(action: str=None, parameters: dict=None):
        behavior_obj = bot.behaviors.find_by_name('scenarios')
        if action:
            action_obj = behavior_obj.actions.find_by_name(action)
            result_data = action_obj.execute(parameters or {})
            return {'status': 'completed', 'behavior': 'scenarios', 'action': action, 'data': result_data}
        behavior_obj.actions.load_state()
        current_action = behavior_obj.actions.current
        result_data = current_action.execute(parameters or {})
        return {'status': 'completed', 'behavior': 'scenarios', 'action': current_action.action_name, 'data': result_data}

    @mcp_server.tool(name='tests', description='tests behavior for story_bot. Accepts optional action parameter and parameters dict.
Trigger patterns: write.*test.*files, write.*test.*code, write.*pytest.*tests, write.*test.*cases, generate.*test.*code')
    async def tests_tool(action: str=None, parameters: dict=None):
        behavior_obj = bot.behaviors.find_by_name('tests')
        if action:
            action_obj = behavior_obj.actions.find_by_name(action)
            result_data = action_obj.execute(parameters or {})
            return {'status': 'completed', 'behavior': 'tests', 'action': action, 'data': result_data}
        behavior_obj.actions.load_state()
        current_action = behavior_obj.actions.current
        result_data = current_action.execute(parameters or {})
        return {'status': 'completed', 'behavior': 'tests', 'action': current_action.action_name, 'data': result_data}

    @mcp_server.tool(name='code', description='code behavior for story_bot. Accepts optional action parameter and parameters dict.
Trigger patterns: generate.*source.*code, create.*production.*code, write.*source.*files, implement.*production.*code, generate.*implementation')
    async def code_tool(action: str=None, parameters: dict=None):
        behavior_obj = bot.behaviors.find_by_name('code')
        if action:
            action_obj = behavior_obj.actions.find_by_name(action)
            result_data = action_obj.execute(parameters or {})
            return {'status': 'completed', 'behavior': 'code', 'action': action, 'data': result_data}
        behavior_obj.actions.load_state()
        current_action = behavior_obj.actions.current
        result_data = current_action.execute(parameters or {})
        return {'status': 'completed', 'behavior': 'code', 'action': current_action.action_name, 'data': result_data}
    
    mcp_server.run()

if __name__ == '__main__':
    main()

import json
from datetime import datetime
import uuid

from worlds.world import World
from typing import List, Dict, Optional

FUNCTION_SYSTEM_PROMPT="""
You are a helpful assistant that is responsible for managing desktop applications and performing actions within them. The state is provided. Always check the state and use the functions to make changes based on the user prompt.
"""
DECISION_SYSTEM_PROMPT="""
You are a helpful assistant that is responsible for managing desktop applications and performing actions within them. The state is provided.
"""
WORLD_STATE_DESCRIPTION = "State: {}"

class DesktopManager(World):
    def __init__(self):
        self.world_state_description = WORLD_STATE_DESCRIPTION
        self.function_system_prompt = FUNCTION_SYSTEM_PROMPT
        self.decision_system_prompt = DECISION_SYSTEM_PROMPT
        
        self.tool_definitions = self._get_tool_definitions()
        self._init_world_state = {
            "open_applications": [],
            "app_history": [],
            "action_log": {}
        }
        self.world_state = self._init_world_state
        self.prompts = [
            {"prompt": "Open 'Text Editor' and list open applications.", "expected_sequence": ["open_application('Text Editor')", "print_open_applications()"]},
            {"prompt": "Open 'Browser', perform a search action, then print actions performed in the Browser.", "expected_sequence": ["open_application('Browser')", "perform_action('Browser', 'Search for AI')", "print_application_actions('Browser')"]},
            {"prompt": "Open 'Music Player', play a song, and close the application.", "expected_sequence": ["open_application('Music Player')", "perform_action('Music Player', 'Play song')", "close_application('Music Player')"]},
            {"prompt": "Check the history of opened applications.", "expected_sequence": ["print_application_history()"]},
            {"prompt": "Open 'Terminal', execute a command, and list all currently open applications.", "expected_sequence": ["open_application('Terminal')", "perform_action('Terminal', 'Run ls command')", "print_open_applications()"]},
            {"prompt": "Open 'Spreadsheet', enter data, then print its action log.", "expected_sequence": ["open_application('Spreadsheet')", "perform_action('Spreadsheet', 'Enter data in cell A1')", "print_application_actions('Spreadsheet')"]}
        ]

    def open_application(self, app_name: str) -> str:
        """
        Opens an application and adds it to the open applications list.
        
        :param app_name: The name of the application to open.
        :return: Confirmation message.
        """
        if app_name not in self.world_state["open_applications"]:
            self.world_state["open_applications"].append(app_name)
            self.world_state["app_history"].append(app_name)
            self.world_state["action_log"][app_name] = []
            return f"Opened application '{app_name}'."
        return f"Application '{app_name}' is already open."

    def close_application(self, app_name: str) -> str:
        """
        Closes an application if it is currently open.
        
        :param app_name: The name of the application to close.
        :return: Confirmation message.
        """
        if app_name in self.world_state["open_applications"]:
            self.world_state["open_applications"].remove(app_name)
            return f"Closed application '{app_name}'."
        return f"Application '{app_name}' is not open."

    def print_open_applications(self) -> List[str]:
        """
        Prints a list of currently open applications.
        
        :return: List of open application names.
        """
        return self.world_state["open_applications"]

    def print_application_history(self) -> List[str]:
        """
        Prints the history of all applications that have been opened.
        
        :return: List of application names.
        """
        return self.world_state["app_history"]

    def perform_action(self, app_name: str, action: str) -> str:
        """
        Logs an action performed in an open application.
        
        :param app_name: The name of the application where the action is performed.
        :param action: The action to log.
        :return: Confirmation message.
        """
        if app_name in self.world_state["open_applications"]:
            self.world_state["action_log"][app_name].append(action)
            return f"Performed action '{action}' in application '{app_name}'."
        return f"Application '{app_name}' is not open."

    def print_application_actions(self, app_name: str) -> List[str]:
        """
        Prints the action log for a specific application.
        
        :param app_name: The name of the application.
        :return: List of actions performed in the application.
        """
        return self.world_state["action_log"].get(app_name, [])
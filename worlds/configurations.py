import json
from datetime import datetime
import uuid

from worlds.world import World
from typing import List, Dict, Optional

FUNCTION_SYSTEM_PROMPT="""
You are a helpful assistant that is responsible for handling state and configuration management by interacting with a structured database. The database is provided. Always check the state and use the functions to make changes based on the user prompt.
"""
DECISION_SYSTEM_PROMPT="""
You are a helpful assistant that is responsible for handling state and configuration management by interacting with a structured database. The database is provided.
"""
WORLD_STATE_DESCRIPTION = "Database: {}"

class Configurations(World):
    def __init__(self):
        self.world_state_description = WORLD_STATE_DESCRIPTION
        self.function_system_prompt = FUNCTION_SYSTEM_PROMPT
        self.decision_system_prompt = DECISION_SYSTEM_PROMPT
        
        self.tool_definitions = self._get_tool_definitions()
        self._init_world_state = {}
        self.reset_world_state()
        self.prompts = [
            {
                "prompt": "Set the configuration for 'theme' to 'dark mode' under the 'UI' category with the current timestamp, 2025-02-12T10:00:00.",
                "expected_sequence": ["set_config('theme', 'dark mode', 'UI')"]
            },
            {
                "prompt": "Print the configuration for 'theme' and update it to 'light mode' while keeping the category unchanged.",
                "expected_sequence": ["print_config('theme')", "update_config('theme', 'light mode')"]
            },
            {
                "prompt": "Set a new configuration for 'auto-save' to 'enabled' under the 'system' category, then print and confirm it.",
                "expected_sequence": ["set_config('auto-save', 'enabled', 'system')", "print_config('auto-save')"]
            },
            {
                "prompt": "Set a configuration for 'timeout' to '30 minutes' under the 'security' category, then update it to '15 minutes' and verify the change by printing the config.",
                "expected_sequence": ["set_config('timeout', '30 minutes', 'security')", "update_config('timeout', '15 minutes')", "print_config('timeout')"]
            },
            {
                "prompt": "Set configurations for 'max-connections' to '100' in 'network', 'log-level' to 'debug' in 'system', then print both.",
                "expected_sequence": ["set_config('max-connections', '100', 'network')", "set_config('log-level', 'debug', 'system')", "print_config('max-connections')", "print_config('log-level')"]
            },
            {
                "prompt": "Update 'log-level' from 'debug' to 'info', then delete 'max-connections', and finally print all remaining configurations.",
                "expected_sequence": ["update_config('log-level', 'info')", "delete_config('max-connections')", "print_config('log-level'), print_config('timeout')"]
            },
            {
                "prompt": "Set a new configuration for 'backup-frequency' to 'daily' in 'storage', update 'timeout' to '10 minutes', then print both settings.",
                "expected_sequence": ["set_config('backup-frequency', 'daily', 'storage')", "update_config('timeout', '10 minutes')", "print_config('backup-frequency')", "print_config('timeout')"]
            }
        ]

    def set_config(self, key: str, value: str, category: Optional[str] = "general", timestamp: Optional[str] = None) -> str:
        """
        Sets a configuration value in the database.
        
        :param key: The key for the configuration setting.
        :param value: The value to store.
        :param category: The category of the setting (default is 'general').
        :param timestamp: Optional timestamp for when the setting was changed.
        :return: Confirmation message.
        """
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        self.world_state[key] = {"value": value, "category": category, "timestamp": timestamp}
        return f"Configuration '{key}' set to '{value}' in category '{category}'."

    def print_config(self, key: str) -> Optional[Dict[str, str]]:
        """
        Print a configuration value from the database.
        
        :param key: The key of the configuration to retrieve.
        :return: The configuration data if found, otherwise None.
        """
        return self.world_state.get(key, None)

    def update_config(self, key: str, new_value: str, category: Optional[str] = None, timestamp: Optional[str] = None) -> str:
        """
        Updates an existing configuration setting.
        
        :param key: The key for the configuration setting.
        :param new_value: The new value to update.
        :param category: Optionally change the category.
        :param timestamp: Optional timestamp for when the update occurs.
        :return: Confirmation message.
        """
        if key not in self.world_state:
            return f"Configuration '{key}' not found."
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        self.world_state[key]["value"] = new_value
        self.world_state[key]["timestamp"] = timestamp
        if category is not None:
            self.world_state[key]["category"] = category
        return f"Configuration '{key}' updated to '{new_value}' in category '{self.world_state[key]['category']}'."

    def delete_config(self, key: str) -> str:
        """
        Deletes a configuration setting from the database.
        
        :param key: The key of the configuration to delete.
        :return: Confirmation message.
        """
        if key in self.world_state:
            del self.world_state[key]
            return f"Configuration '{key}' has been deleted."
        return f"Configuration '{key}' not found."

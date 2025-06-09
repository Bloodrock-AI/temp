import json
from datetime import datetime
import uuid

from worlds.world import World
from typing import List, Dict, Optional

FUNCTION_SYSTEM_PROMPT="""
You are a helpful assistant that is responsible for managing a smart house. The state of the smart house functionalities is provided. Always check the state and use the functions to make changes based on the user prompt.
"""
DECISION_SYSTEM_PROMPT="""
You are a helpful assistant that is responsible for managing a smart house. The state of the smart house functionalities is provided. Always check the state.
"""
WORLD_STATE_DESCRIPTION = "Smart House state: {}"

class Automation(World):
    def __init__(self):
        self.world_state_description = WORLD_STATE_DESCRIPTION
        self.function_system_prompt = FUNCTION_SYSTEM_PROMPT
        self.decision_system_prompt = DECISION_SYSTEM_PROMPT
        
        self.tool_definitions = self._get_tool_definitions()
        self._init_world_state = {
            "lights_on": False,
            "thermostat": 22,
            "door_locked": True,
            "alarm_on": False,
        }
        self.reset_world_state()
        self.prompts = [
            {
                "prompt": "Turn on the lights and then set the thermostat to 24 degrees.",
                "setup_functions": [],
                "expected_sequences": [["turn_on_lights()", "set_thermostat(temperature=24)"]]
            },
            {
                "prompt": "Lock the door and activate the alarm in that order.",
                "setup_functions":["unlock_door()",],
                "expected_sequences": [["lock_door()", "activate_alarm()"]]
            },
            {
                "prompt": "First step: Unlock the door. Second step: Turn off the lights. Third step: Set the thermostat to 20 degrees.",
                "setup_functions":["turn_on_lights()",],
                "expected_sequences": [["unlock_door()", "turn_off_lights()", "set_thermostat(temperature=20)"]]
            },
            {
                "prompt": "Print the system status, then turn on the lights only if they are off.",
                "setup_functions": [],
                "expected_sequences": [["print_system_status()", "turn_on_lights()"]]
            },
            {
                "prompt": "The house does in lockdown mode. Lock the doors, activate the alarm and turn off the lights in that order. Then, set the thermostat to 30 degrees and turn everything back on in the same order they were shut down.",
                "setup_functions":["unlock_door()", "turn_on_lights()"],
                "expected_sequences": [["lock_door()", "activate_alarm()", "turn_off_lights()","set_thermostat(temperature=30)", "unlock_door()", "deactivate_alarm()", "turn_on_lights()"]]
            }
        ]

    def turn_on_lights(self) -> str:
        """
        Turns on the lights in the system.
        
        :return: Confirmation message
        """
        self.world_state["lights_on"] = True
        return "Lights turned on."

    def turn_off_lights(self) -> str:
        """
        Turns off the lights in the system.
        
        :return: Confirmation message
        """
        self.world_state["lights_on"] = False
        return "Lights turned off."

    def set_thermostat(self, temperature: int) -> str:
        """
        Sets the thermostat to the specified temperature.
        
        :param temperature: Desired temperature setting.
        :return: Confirmation message
        """
        self.world_state["thermostat"] = temperature
        return f"Thermostat set to {temperature} degrees."

    def lock_door(self) -> str:
        """
        Locks the main door.
        
        :return: Confirmation message
        """
        self.world_state["door_locked"] = True
        return "Door locked."

    def unlock_door(self) -> str:
        """
        Unlocks the main door.
        
        :return: Confirmation message
        """
        self.world_state["door_locked"] = False
        return "Door unlocked."

    def activate_alarm(self) -> str:
        """
        Activates the security alarm.
        
        :return: Confirmation message
        """
        self.world_state["alarm_on"] = True
        return "Alarm activated."

    def deactivate_alarm(self) -> str:
        """
        Deactivates the security alarm.
        
        :return: Confirmation message
        """
        self.world_state["alarm_on"] = False
        return "Alarm deactivated."

    def print_system_status(self) -> Dict[str, str]:
        """
        Returns the current status of the system.
        
        :return: Dictionary with system state information
        """
        return self.world_state

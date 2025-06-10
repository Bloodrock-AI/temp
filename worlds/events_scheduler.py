import json
from datetime import datetime, timedelta
import uuid

from worlds.world import World
from typing import List, Dict, Optional

FUNCTION_SYSTEM_PROMPT="""
You are a helpful assistant that is responsible for for managing event scheduling and time-related tasks. The state is provided. Always check the state and use the functions to make changes based on the user prompt.
"""
DECISION_SYSTEM_PROMPT="""
You are a helpful assistant that is responsible for for managing event scheduling and time-related tasks. The state is provided.
"""
WORLD_STATE_DESCRIPTION = "State: {}"

class EventsScheduler(World):
    def __init__(self):
        self.world_state_description = WORLD_STATE_DESCRIPTION
        self.function_system_prompt = FUNCTION_SYSTEM_PROMPT
        self.decision_system_prompt = DECISION_SYSTEM_PROMPT
        
        self.tool_definitions = self._get_tool_definitions()
        self._init_world_state = {}
        self.reset_world_state()
        self.prompts = [
            {
                "prompt": "Schedule a meeting called 'Team Sync' at '2025-02-10T09:00:00' and retrieve its scheduled time.",
                "setup_functions": [],
                "expected_sequences": [["schedule_event('Team Sync', '2025-02-10T09:00:00')", "get_event_time('Team Sync')"]]
            },
            {
                "prompt": "Schedule 'Team Sync' at '2025-02-10T09:00:00', then list all scheduled events.",
                "setup_functions": [],
                "expected_sequences": [["schedule_event('Team Sync', '2025-02-10T09:00:00')", "list_events()"]]
            },
            {
                "prompt": "Reschedule 'Team Sync' to '2025-02-10T10:00:00' and check the remaining time until the event.",
                "setup_functions": ["schedule_event('Team Sync', '2025-02-10T09:00:00')"],
                "expected_sequences": [["reschedule_event('Team Sync', '2025-02-10T10:00:00')", "time_until_event('Team Sync')"]]
            },
            {
                "prompt": "Cancel 'Team Sync', then list all events to confirm it has been removed.",
                "setup_functions": ["schedule_event('Team Sync', '2025-02-10T09:00:00')"],
                "expected_sequences": [["cancel_event('Team Sync')", "list_events()"]]
            },
            {
                "prompt": "Schedule a recurring stand-up meeting every 30 minutes and retrieve its scheduled time.",
                "setup_functions": [],
                "expected_sequences": [["schedule_recurring_event('Stand-up Meeting', 30)", "get_event_time('Stand-up Meeting')"]]
            },
            {
                "prompt": "Schedule 'Project Review' at '2025-02-11T15:00:00', list all events, then check the time until that event.",
                "setup_functions": [],
                "expected_sequences": [["schedule_event('Project Review', '2025-02-11T15:00:00')", "list_events()", "time_until_event('Project Review')"]]
            }
        ]

    def schedule_event(self, event_name: str, event_time: str) -> str:
        """
        Schedules an event at a specified time.
        
        :param event_name: The name of the event.
        :param event_time: The scheduled time in ISO 8601 format.
        :return: Confirmation message.
        """
        self.world_state[event_name] = event_time
        return f"Event '{event_name}' scheduled at {event_time}."

    def cancel_event(self, event_name: str) -> str:
        """
        Cancels a scheduled event.
        
        :param event_name: The name of the event to cancel.
        :return: Confirmation message.
        """
        if event_name in self.world_state:
            del self.world_state[event_name]
            return f"Event '{event_name}' has been canceled."
        return f"Event '{event_name}' not found."

    def list_events(self) -> Dict[str, str]:
        """
        Lists all scheduled events with their respective times.
        
        :return: Dictionary of scheduled events.
        """
        return self.world_state

    def reschedule_event(self, event_name: str, new_time: str) -> str:
        """
        Reschedules an existing event to a new time.
        
        :param event_name: The name of the event to reschedule.
        :param new_time: The new event time in ISO 8601 format.
        :return: Confirmation message.
        """
        if event_name in self.world_state:
            self.world_state[event_name] = new_time
            return f"Event '{event_name}' rescheduled to {new_time}."
        return f"Event '{event_name}' not found."

    def get_event_time(self, event_name: str) -> Optional[str]:
        """
        Retrieves the scheduled time of an event.
        
        :param event_name: The name of the event.
        :return: The scheduled time of the event or None if not found.
        """
        return self.world_state.get(event_name, None)

    def time_until_event(self, event_name: str) -> Optional[str]:
        """
        Calculates the remaining time until a scheduled event.
        
        :param event_name: The name of the event.
        :return: The remaining time as a string, or None if the event is not found.
        """
        if event_name not in self.world_state:
            return None
        event_time = datetime.fromisoformat(self.world_state[event_name])
        time_difference = event_time - datetime.utcnow()
        return str(time_difference) if time_difference.total_seconds() > 0 else "Event time has passed."

    def schedule_recurring_event(self, event_name: str, interval_minutes: int) -> str:
        """
        Schedules a recurring event that repeats at a fixed interval.
        
        :param event_name: The name of the event.
        :param interval_minutes: Interval time in minutes.
        :return: Confirmation message.
        """
        event_time = datetime.utcnow() + timedelta(minutes=interval_minutes)
        self.world_state[event_name] = event_time.isoformat()
        return f"Recurring event '{event_name}' scheduled every {interval_minutes} minutes."

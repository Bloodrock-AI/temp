import json
from datetime import datetime
import uuid

from worlds.world import World
from typing import List, Dict, Optional

FUNCTION_SYSTEM_PROMPT="""
You are a helpful assistant that is responsible for handling communication and messaging tasks. The database of messages is provided. Always check the state and use the functions to make changes based on the user prompt.
"""
DECISION_SYSTEM_PROMPT="""
You are a helpful assistant that is responsible for handling communication and messaging tasks. The database of messages is provided.
"""
WORLD_STATE_DESCRIPTION = "Database: {}"

class Communication(World):
    def __init__(self):
        self.world_state_description = WORLD_STATE_DESCRIPTION
        self.function_system_prompt = FUNCTION_SYSTEM_PROMPT
        self.decision_system_prompt = DECISION_SYSTEM_PROMPT
        
        self.tool_definitions = self._get_tool_definitions()
        self._init_world_state = {
            "messages": []
        }
        self.reset_world_state()
        self.prompts = [
            {
                "prompt": "Send a high-priority message from 'Alice' to 'Bob' with the content 'Urgent meeting at 3 PM'.",
                "expected_sequence": ["send_message(sender='Alice', recipient='Bob', content='Urgent meeting at 3 PM', priority='high')"]
            },
            {
                "prompt": "Print all messages for 'Bob', filtering only high-priority ones.",
                "expected_sequence": ["print_messages(recipient='Bob', priority='high')"]
            },
            {
                "prompt": "Send a normal-priority message from 'Charlie' to 'Dana' with the content 'Lunch at noon'. Then print all of Dana’s messages.",
                "expected_sequence": ["send_message(sender='Charlie', recipient='Dana', content='Lunch at noon', priority='normal')", "print_messages(recipient='Dana')"]
            },
            {
                "prompt": "Schedule a message from 'Eve' to 'Frank' saying 'Reminder: Call at 10 AM' to be sent at '2025-02-12T10:00:00'.",
                "expected_sequence": ["schedule_message(sender='Eve', recipient='Frank', content='Reminder: Call at 10 AM', send_time='2025-02-12T10:00:00')"]
            },
            {
                "prompt": "Forward a message originally sent by 'Alice' at '2025-02-11T14:30:00' to 'Grace' by 'Bob'.",
                "expected_sequence": ["forward_message(original_sender='Alice', new_recipient='Grace', timestamp='2025-02-11T14:30:00', forwarded_by='Bob')"]
            },
            {
                "prompt": "Send a message from 'Henry' to 'Ivy' saying 'See you at the event!' with normal priority, then delete it using the correct timestamp.",
                "expected_sequence": ["send_message(sender='Henry', recipient='Ivy', content='See you at the event!', priority='normal')", "delete_message(sender='Henry', recipient='Ivy', timestamp='<timestamp>')"]
            },
        ]

    def send_message(self, sender: str, recipient: str, content: str, priority: Optional[str], timestamp: Optional[str] = None) -> str:
        """
        Sends a message from a sender to a recipient.
        
        :param sender: The sender's name or identifier.
        :param recipient: The recipient's name or identifier.
        :param content: The message content.
        :param priority: Message priority (default: "normal"). Enum: ["low", "normal", "high"]
        :param timestamp: Optional timestamp of when the message was sent.
        :return: Confirmation message.
        """
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        message = {"sender": sender, "recipient": recipient, "content": content, "priority": priority, "timestamp": timestamp}
        self.world_state["messages"].append(message)
        return f"Message sent from '{sender}' to '{recipient}' with priority '{priority}'."

    def print_messages(self, recipient: str, priority: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Prints messages for a specific recipient, optionally filtering by priority.
        
        :param recipient: The recipient whose messages should be printed.
        :param priority: Optionally filter messages by priority.  Enum: ["low", "normal", "high"]
        :return: A list of messages.
        """
        return [msg for msg in self.world_state["messages"] if msg["recipient"] == recipient and (priority is None or msg["priority"] == priority)]

    def delete_message(self, sender: str, recipient: str) -> str:
        """
        Deletes a message based on sender, recipient, and timestamp.
        
        :param sender: The sender of the message.
        :param recipient: The recipient of the message.
        :param timestamp: The timestamp of the message to delete.
        :return: Confirmation message.
        """
        self.world_state["messages"] = [msg for msg in self.world_state["messages"] if not (msg["sender"] == sender and msg["recipient"] == recipient) ]
        return f"Message from '{sender}' to '{recipient}' has been deleted."

    def forward_message(self, original_sender: str, new_recipient: str, timestamp: str, forwarded_by: str) -> str:
        """
        Forwards a message to a new recipient.
        
        :param original_sender: The sender of the original message.
        :param new_recipient: The new recipient of the forwarded message.
        :param timestamp: The timestamp of the original message.
        :param forwarded_by: The user forwarding the message.
        :return: Confirmation message.
        """
        for msg in self.world_state["messages"]:
            if msg["sender"] == original_sender and msg["timestamp"] == timestamp:
                new_message = msg.copy()
                new_message["recipient"] = new_recipient
                new_message["sender"] = forwarded_by
                self.world_state["messages"].append(new_message)
                return f"Message from '{original_sender}' forwarded to '{new_recipient}' by '{forwarded_by}'."
        return "Original message not found."

    def schedule_message(self, sender: str, recipient: str, content: str, send_time: str, priority: Optional[str] = "normal") -> str:
        """
        Schedules a message to be sent at a later time.
        
        :param sender: The sender's name or identifier.
        :param recipient: The recipient's name or identifier.
        :param content: The message content.
        :param send_time: The scheduled time to send the message in ISO 8601 format.
        :param priority: Message priority (default: "normal").  Enum: ["low", "normal", "high"]
        :return: Confirmation message.
        """
        message = {"sender": sender, "recipient": recipient, "content": content, "priority": priority, "timestamp": send_time}
        self.world_state["messages"].append(message)
        return f"Message from '{sender}' to '{recipient}' scheduled for {send_time} with priority '{priority}'."

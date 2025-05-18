import json
from datetime import datetime
import uuid

from worlds.world import World
from typing import List, Dict, Optional

FUNCTION_SYSTEM_PROMPT="""
You are a helpful assistant that makes changes on a database. The database is a list of users. Always check the database and use the functions to make changes based on the user prompt.
"""
DECISION_SYSTEM_PROMPT="""
You are a helpful assistant that makes changes on a database. The database is a list of users. Always check the database.
"""

class CRUD(World):
    def __init__(self):
        self.world_state_description = "Database: {}"
        self.function_system_prompt = FUNCTION_SYSTEM_PROMPT
        self.decision_system_prompt = DECISION_SYSTEM_PROMPT
        
        self.tool_definitions = self._get_tool_definitions()
        self._init_world_state = {}
        self.world_state = self._init_world_state
        self.prompts = [
            {
                "prompt": "Create a new user named 'Alice' with an age of 25. List the details of this user and confirm the age field is correct",
            },
            {
                "prompt": "Show all users and update the email of the user with name 'Alice' to 'alice@example.com'. Ensure the changes were applied.",
                "functions": [
                    'add_user(name="Alice", age=25)',
                ],
            },
            {
                "prompt": "Show all users. Then, update the emails of all users with no email address to 'default@example.com'. Pick one of these users and ensure the changes were applied.",
                "functions": [
                    'add_user(name="John", age=30, email=None)',
                    'add_user(name="Jane", age=25, email=None)',
                ],
            },
            {
                "prompt": "Add a new user named 'Charlie' aged 40 with email 'charlie@email.com'. Then, delete that user. Finally, confirm the deletion by showing all the users."
            },
            {
                "prompt": "Create a new user named 'Eve' with an age of 22 and empty email. Then, update their email to 'eve@example.com'. Finally delete the user and verify the deletion by checking all the existing users.",
            }
        ]

    def generate_timestamp(self):
        """Generates the current timestamp in ISO 8601 format."""
        return datetime.utcnow().isoformat() + "Z"

    def add_user(self, name: str, age: int, email: Optional[str] = None) -> str:
        """
        Adds a new user to the database and returns the user ID.

        :param name: The name of the user to be added.
        :param age: The age of the user to be added.
        :param email: The email of the user to be added.
        :return: user ID
        """
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        new_user = {
            "id": user_id,
            "name": name,
            "age": age,
            "email": email,
        }
        self.world_state[user_id] = new_user
        return user_id

    def update_user_email(self, user_id: str, email: str) -> bool:
        """
        Updates a user's email.

        :param user_id: The user ID of the user to be updated.
        :param email: The updated email of the user.
        :return: True if the user was found and updated, False otherwise
        """
        if user_id not in self.world_state:
            return False
        user = self.world_state[user_id]
        user["email"] = email
        return True
        
    def delete_user(self, user_id: str) -> bool:
        """
        Deletes a user from the database by user ID.

        :param user_id: The user ID of the user to be deleted. 
        :return: True if the user was found and deleted, False otherwise
        """
        if user_id in self.world_state:
            del self.world_state[user_id]
            return True
        return False

    def list_users(self) -> List[Dict]:
        """
        Returns a list of users, optionally filtered by specific criteria.
        :return: list of users
        """
        return list(self.world_state.values())
        
    def verify_user_field(self, user_id: str, field: str, expected_value: str) -> bool:
        """
        Verifies if a specific field in a user record matches the expected value.

        :param user_id: The user ID of the user to be verified.
        :param field: field to check
        :param expected_value: expected value in string form
        :return: True if the field matches the expected value, False otherwise
        """
        user = self.world_state.get(user_id, None)
        if not user:
            return False
        if field == "age":
            expected_value = int(expected_value)
        return user.get(field) == expected_value

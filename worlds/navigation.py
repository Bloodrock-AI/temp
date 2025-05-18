# navigation.py

from typing import Tuple, Dict, List, Optional
from worlds.world import World
from llm_tool import tool


class Navigation(World):
    def __init__(self):
        self.world_state_description = "Player Position on 5x5 Grid: {}"
        self.function_system_prompt = """
You are an AI agent responsible for handling spatial navigation in a 5x5 grid-based environment.
Your objective is to correctly execute movement functions to navigate the grid efficiently while ensuring logical consistency.
        """
        self.decision_system_prompt = self.function_system_prompt

        self.grid_size = (5, 5)  # Fixed 5x5 grid
        self._init_world_state = {
            "player_position": (0, 0),
        }
        self.world_state = self._init_world_state.copy()

        self.prompts = [
            {"prompt": "Move the player right by 2 steps."},
            {"prompt": "Move the player down by 3 steps, then retrieve the player's position."},
            {"prompt": "Move the player right by 1 step, then move down by 2 steps."},
            {"prompt": "Move the player in a square pattern (2 steps right, 2 steps down, 2 steps left, 2 steps up)."},
            {"prompt": "Move the player to the bottom-right corner of the grid (4,4)."},
            {"prompt": "Move the player right by 3 steps. Reset the player's position and confirm their location."},
        ]

        self.tool_definitions = self._get_tool_definitions()

    def _is_within_bounds(self, position: Tuple[int, int]) -> bool:
        x, y = position
        width, height = self.grid_size
        return 0 <= x < width and 0 <= y < height

    @tool()
    def move_up(self, steps: int = 1) -> str:
        x, y = self.world_state["player_position"]
        new_position = (x, y - steps)
        if self._is_within_bounds(new_position):
            self.world_state["player_position"] = new_position
            return f"Moved up to {new_position}."
        return "Move out of bounds."

    @tool()
    def move_down(self, steps: int = 1) -> str:
        x, y = self.world_state["player_position"]
        new_position = (x, y + steps)
        if self._is_within_bounds(new_position):
            self.world_state["player_position"] = new_position
            return f"Moved down to {new_position}."
        return "Move out of bounds."

    @tool()
    def move_left(self, steps: int = 1) -> str:
        x, y = self.world_state["player_position"]
        new_position = (x - steps, y)
        if self._is_within_bounds(new_position):
            self.world_state["player_position"] = new_position
            return f"Moved left to {new_position}."
        return "Move out of bounds."

    @tool()
    def move_right(self, steps: int = 1) -> str:
        x, y = self.world_state["player_position"]
        new_position = (x + steps, y)
        if self._is_within_bounds(new_position):
            self.world_state["player_position"] = new_position
            return f"Moved right to {new_position}."
        return "Move out of bounds."

    @tool()
    def get_player_position(self) -> Tuple[int, int]:
        return self.world_state["player_position"]

    @tool()
    def reset_position(self) -> str:
        self.world_state["player_position"] = (0, 0)
        return "Player position reset to (0, 0)."

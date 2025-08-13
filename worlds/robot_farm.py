import json
from datetime import datetime
import uuid
from typing import Dict, List, Optional

from worlds.world import World

WORLD_STATE_DESCRIPTION = "Farming Rover state: {}"

FUNCTION_SYSTEM_PROMPT = """
You operate an autonomous farming rover in an outdoor field.
The rover position is (x, y) in meters and yaw in radians. There is no Z axis.
You must respect safety mode, field bounds, and no-go zones. Use the functions exactly with the parameters shown.
Harvest/water/spray actions require the rover to be within the specified tolerances of the target plant or station.
"""

DECISION_SYSTEM_PROMPT = """
Plan a safe, correct sequence for the farming rover.
Always unlock safety before motion or actuation.
Use read-only checks (e.g., sense_pose, scan_plant, get_plant_pose, get_station_pose) if needed,
but avoid unnecessary detours.
"""

class FarmingRover(World):
    def __init__(self):
        self.world_state_description = WORLD_STATE_DESCRIPTION
        self.function_system_prompt = FUNCTION_SYSTEM_PROMPT
        self.decision_system_prompt = DECISION_SYSTEM_PROMPT

        self.tool_definitions = self._get_tool_definitions()

        # Fixed environment & initial state
        self._init_world_state = {
            # Kinematics / pose (meters, radians)
            "pose": {"x": 5.0, "y": 5.0, "yaw": 0.0},
            "home_pose": {"x": 5.0, "y": 5.0, "yaw": 0.0},

            # Safety
            "safety_mode": True,

            # Workspace / field constraints
            "field_bounds": {"xmin": 0.0, "xmax": 20.0, "ymin": 0.0, "ymax": 20.0},
            # Rectangular no-go zones in XY (e.g., irrigation ditches, fences)
            "no_go_xy": [
                {"xmin": 9.0, "xmax": 11.0, "ymin": 0.0, "ymax": 6.0},  # a ditch
            ],

            # Tolerances (meters)
            "plant_tolerance_xy": 0.30,
            "station_tolerance_xy": 0.40,

            # Plants (positions in the field, attributes are realistic but simplified)
            # ripeness: 0..1, moisture: 0..1, pest: bool, fruit_weight: kg, has_fruit: bool
            "plants": {
                "plant_A": {"pose": {"x": 2.0, "y": 14.0}, "ripeness": 0.85, "moisture": 0.40, "pest": False, "has_fruit": True, "fruit_weight": 1.2},
                "plant_B": {"pose": {"x": 3.5, "y": 12.5}, "ripeness": 0.45, "moisture": 0.55, "pest": True,  "has_fruit": True, "fruit_weight": 0.8},
                "plant_C": {"pose": {"x": 14.0, "y": 8.5}, "ripeness": 0.92, "moisture": 0.30, "pest": False, "has_fruit": True, "fruit_weight": 1.5},
                "plant_D": {"pose": {"x": 16.5, "y": 15.0}, "ripeness": 0.20, "moisture": 0.20, "pest": True,  "has_fruit": False, "fruit_weight": 0.0},
            },

            # Stations (navigation targets)
            "stations": {
                "collection_bin": {"x": 6.0, "y": 18.0, "yaw": 0.0},
                "charging_pad":   {"x": 1.0, "y": 1.0,  "yaw": 0.0},
                "water_station":  {"x": 18.5, "y": 2.0, "yaw": 0.0},
                "pesticide_refill": {"x": 18.0, "y": 18.0, "yaw": 0.0},
            },

            # Resources & capacities
            "battery_pct": 80.0,             # %
            "hopper_capacity_kg": 10.0,      # kg
            "hopper_load_kg": 0.0,           # kg
            "water_tank_capacity_l": 10.0,   # liters
            "water_tank_l": 5.0,             # liters
            "pesticide_tank_capacity_ml": 500.0,  # ml
            "pesticide_tank_ml": 200.0,           # ml

            # Policy thresholds
            "ripe_threshold": 0.70,          # minimum ripeness to harvest
            "max_moisture": 0.80,            # do not exceed after watering
        }

        self.reset_world_state()

        # (Optional) Example prompts for quick testing — remove or extend as needed.
        self.prompts = [
            {
                "prompt_id": "robot_farm_1",
                "prompt": (
                    "Disengage safety. Drive to plant C and harvest its fruit. "
                    "Then take the load to the collection bin,"
                    "empty the hopper, and return to base."
                ),
                "setup_functions": [],
                "expected_sequences": [[
                    "unlock_safety_mode()",
                    "move_to(x=14.0, y=8.5, yaw=0.0)",
                    "harvest_fruit(plant_id='plant_C')",
                    "move_to(x=6.0, y=18.0, yaw=0.0)",
                    "dump_hopper()",
                    "move_home()"
                ],
                [
                    "unlock_safety_mode()",
                    "move_to(x=14.0, y=8.5, yaw=0.0)",
                    "harvest_fruit(plant_id='plant_C')",
                    "move_to(x=6.0, y=18.0, yaw=0.0)",
                    "dump_hopper()",
                    "move_to(x=5.0, y=5.0, yaw=0.0)"
                ]
                ]
            },
            {
                "prompt_id": "robot_farm_2",
                "prompt": (
                    "Water plant A with 1.5 liters, then plant C with 2.5 liters, then plant B with 1.5 liters. "
                    "Refill at the water station only when you need to."
                ),
                "setup_functions": [],
                "expected_sequences": [[
                    "unlock_safety_mode()",
                    "move_to(x=2.0, y=14.0, yaw=0.0)",
                    "water_plant(plant_id='plant_A', liters=1.5)",
                    "move_to(x=14.0, y=8.5, yaw=0.0)",
                    "water_plant(plant_id='plant_C', liters=2.5)",
                    "move_to(x=18.5, y=2.0, yaw=0.0)",
                    "refill_water_tank()",
                    "move_to(x=3.5, y=12.5, yaw=0.0)",
                    "water_plant(plant_id='plant_B', liters=1.5)",
                    "move_home()"
                ],
                [
                    "unlock_safety_mode()",
                    "move_to(x=2.0, y=14.0, yaw=0.0)",
                    "water_plant(plant_id='plant_A', liters=1.5)",
                    "move_to(x=14.0, y=8.5, yaw=0.0)",
                    "water_plant(plant_id='plant_C', liters=2.5)",
                    "move_to(x=18.5, y=2.0, yaw=0.0)",
                    "refill_water_tank()",
                    "move_to(x=3.5, y=12.5, yaw=0.0)",
                    "water_plant(plant_id='plant_B', liters=1.5)",
                    "move_to(x=5.0, y=5.0, yaw=0.0)"
                ]
                ]
            },
            {
                "prompt_id": "robot_farm_3",
                "prompt": (
                    "Apply 150 milliliters of pesticide to plant B, then refuel pesticide at the refill station "
                    "and apply 150 milliliters to plant D. Finish by returning to base."
                ),
                "setup_functions": [],
                "expected_sequences": [[
                    "unlock_safety_mode()",
                    "move_to(x=3.5, y=12.5, yaw=0.0)",
                    "spray_pesticide(plant_id='plant_B', ml=150.0)",
                    "move_to(x=18.0, y=18.0, yaw=0.0)",
                    "refill_pesticide()",
                    "move_to(x=16.5, y=15.0, yaw=0.0)",
                    "spray_pesticide(plant_id='plant_D', ml=150.0)",
                    "move_home()"
                ],
                [
                    "unlock_safety_mode()",
                    "move_to(x=3.5, y=12.5, yaw=0.0)",
                    "spray_pesticide(plant_id='plant_B', ml=150.0)",
                    "move_to(x=18.0, y=18.0, yaw=0.0)",
                    "refill_pesticide()",
                    "move_to(x=16.5, y=15.0, yaw=0.0)",
                    "spray_pesticide(plant_id='plant_D', ml=150.0)",
                    "move_to(x=5.0, y=5.0, yaw=0.0)"
                ]]
            },
            {
                "prompt_id": "robot_farm_4",
                "prompt": (
                    "Inspect plant B. If you detect pests, apply 20 milliliters of pesticide. "
                    "Harvest only if its fruit is ripe. Empty the hopper at the bin and go back to base."
                ),
                "setup_functions": [],
                "expected_sequences": [[
                    "unlock_safety_mode()",
                    "scan_plant(plant_id='plant_B')",
                    "move_to(x=3.5, y=12.5, yaw=0.0)",
                    "spray_pesticide(plant_id='plant_B', ml=20.0)",
                    "move_to(x=6.0, y=18.0, yaw=0.0)",
                    "dump_hopper()",
                    "move_home()"
                ],
                [
                    "unlock_safety_mode()",
                    "scan_plant(plant_id='plant_B')",
                    "move_to(x=3.5, y=12.5, yaw=0.0)",
                    "spray_pesticide(plant_id='plant_B', ml=20.0)",
                    "move_to(x=6.0, y=18.0, yaw=0.0)",
                    "dump_hopper()",
                    "move_to(x=5.0, y=5.0, yaw=0.0)"
                ]
                ]
            },
            {
                "prompt_id": "robot_farm_5",
                "prompt": (
                    "Disengage safety. Report your current position, then navigate to the charging pad."
                    "Recharge there and re-engage safety."
                ),
                "setup_functions": [],
                "expected_sequences": [[
                    "unlock_safety_mode()",
                    "sense_pose()",
                    "move_to(x=1.0, y=1.0, yaw=0.0)",
                    "recharge()",
                    "lock_safety_mode()"
                ],]
            },
            {
                "prompt_id": "robot_farm_6",
                "prompt": (
                    "Harvest plant A, then plant C. "
                    "Take each load to the collection bin, empty the hopper, and return to base."
                ),
                "setup_functions": [],
                "expected_sequences": [[
                    "unlock_safety_mode()",
                    "move_to(x=2.0, y=14.0, yaw=0.0)",
                    "harvest_fruit(plant_id='plant_A')",
                    "move_to(x=14.0, y=8.5, yaw=0.0)",
                    "harvest_fruit(plant_id='plant_C')",
                    "move_to(x=6.0, y=18.0, yaw=0.0)",
                    "dump_hopper()",
                    "move_home()"
                ],
                [
                    "unlock_safety_mode()",
                    "move_to(x=2.0, y=14.0, yaw=0.0)",
                    "harvest_fruit(plant_id='plant_A')",
                    "move_to(x=14.0, y=8.5, yaw=0.0)",
                    "harvest_fruit(plant_id='plant_C')",
                    "move_to(x=6.0, y=18.0, yaw=0.0)",
                    "dump_hopper()",
                    "move_to(x=5.0, y=5.0, yaw=0.0)"
                ]]
            },
            {
                "prompt_id": "robot_farm_7",
                "prompt": (
                    "Water plant C with 4.5 liters while keeping moisture within safe limits. "
                    "Then harvest plant A and deliver the load to the collection bin."
                    "Empty the hopper and return to base."
                ),
                "setup_functions": [],
                "expected_sequences": [[
                    "unlock_safety_mode()",
                    "move_to(x=14.0, y=8.5, yaw=0.0)",
                    "water_plant(plant_id='plant_C', liters=4.5)",
                    "move_to(x=2.0, y=14.0, yaw=0.0)",
                    "harvest_fruit(plant_id='plant_A')",
                    "move_to(x=6.0, y=18.0, yaw=0.0)",
                    "dump_hopper()",
                    "move_home()"
                ],
                [
                    "unlock_safety_mode()",
                    "move_to(x=14.0, y=8.5, yaw=0.0)",
                    "water_plant(plant_id='plant_C', liters=4.5)",
                    "move_to(x=2.0, y=14.0, yaw=0.0)",
                    "harvest_fruit(plant_id='plant_A')",
                    "move_to(x=6.0, y=18.0, yaw=0.0)",
                    "dump_hopper()",
                    "move_to(x=5.0, y=5.0, yaw=0.0)"
                ]]
            },
            {
                "prompt_id": "robot_farm_8",
                "prompt": (
                    "First refill the water tank at the water station."
                    "Then service plant D: inspect it, apply 50 milliliters of pesticide if pests are present, "
                    "and water it with 2.5 liters. Return to base and re-engage safety."
                ),
                "setup_functions": [],
                "expected_sequences": [[
                    "unlock_safety_mode()",
                    "move_to(x=18.5, y=2.0, yaw=0.0)",
                    "refill_water_tank()",
                    "scan_plant(plant_id='plant_D')",
                    "move_to(x=16.5, y=15.0, yaw=0.0)",
                    "spray_pesticide(plant_id='plant_D', ml=50.0)",
                    "water_plant(plant_id='plant_D', liters=2.5)",
                    "move_home()",
                    "lock_safety_mode()"
                ],
                [
                    "unlock_safety_mode()",
                    "move_to(x=18.5, y=2.0, yaw=0.0)",
                    "refill_water_tank()",
                    "scan_plant(plant_id='plant_D')",
                    "move_to(x=16.5, y=15.0, yaw=0.0)",
                    "spray_pesticide(plant_id='plant_D', ml=50.0)",
                    "water_plant(plant_id='plant_D', liters=2.5)",
                    "move_to(x=5.0, y=5.0, yaw=0.0)"
                    "lock_safety_mode()"
                ]]
            }
        ]


    def _within_bounds(self, x: float, y: float) -> bool:
        """
        Determine whether the provided (x, y) coordinates are within the inclusive field boundaries.

        Preconditions (enforced by this method):
            - `self.world_state["field_bounds"]` must define valid numeric limits for xmin, xmax, ymin, ymax.

        Behavior:
            - Returns True if both x and y are within their respective minimum and maximum bounds.
            - Returns False otherwise.

        :param x: X coordinate to check.
        :param y: Y coordinate to check.
        :return: True if (x, y) lies within bounds; False otherwise.
        """
        b = self.world_state["field_bounds"]
        return (b["xmin"] <= x <= b["xmax"]) and (b["ymin"] <= y <= b["ymax"])

    def _in_no_go_zone(self, x: float, y: float) -> bool:
        """
        Check whether the provided (x, y) coordinates lie inside any defined no-go zone.

        Preconditions (enforced by this method):
            - `self.world_state["no_go_xy"]` must contain one or more rectangles,
            each with inclusive boundaries xmin, xmax, ymin, ymax.

        Behavior:
            - Iterates through all defined no-go rectangles in the XY plane.
            - Returns True if (x, y) falls inside any such rectangle.
            - Returns False if no match is found.

        :param x: X coordinate to check.
        :param y: Y coordinate to check.
        :return: True if (x, y) lies inside at least one no-go zone; False otherwise.
        """
        for rect in self.world_state["no_go_xy"]:
            if rect["xmin"] <= x <= rect["xmax"] and rect["ymin"] <= y <= rect["ymax"]:
                return True
        return False

    def _dist_xy(self, a: Dict[str, float], b: Dict[str, float]) -> float:
        """
        Compute the Euclidean distance between two points in the XY plane.

        Preconditions (enforced by this method):
            - Both `a` and `b` must be dictionaries with numeric "x" and "y" keys.

        Behavior:
            - Calculates the straight-line distance between the points, ignoring z or yaw values.
            - Returns the distance as a floating-point number.

        :param a: Dictionary representing the first point, with keys "x" and "y".
        :param b: Dictionary representing the second point, with keys "x" and "y".
        :return: Euclidean distance between points a and b in the XY plane.
        """
        dx = a["x"] - b["x"]
        dy = a["y"] - b["y"]
        return (dx * dx + dy * dy) ** 0.5

    def unlock_safety_mode(self) -> str:
        """
        Disable the rover's safety lock to allow motion and actuations.
        Do NOT issue this command if the safety is already locked.
        Repeatedly “unlocking” an already-unlocked system can spam
        safety logs, retrigger permission handshakes, or momentarily stall motion
        while interlocks are revalidated — all with no benefit.

        Preconditions (enforced by this method):
            - None.

        Behavior:
            - Sets `self.world_state["safety_mode"] = False`.
            - Returns a confirmation message.

        Failure cases (returns an error string):
            - None (this operation always succeeds).

        :return: Confirmation message indicating safety mode is unlocked.
        """
        self.world_state["safety_mode"] = False
        return "Safety mode unlocked."

    def lock_safety_mode(self) -> str:
        """
        Enable the rover's safety lock to prevent motion and actuations.
        Do NOT issue this command if the arm is already locked.
        Repeated “lock” commands can generate nuisance events in safety logs,
        prolong stop-to-start transitions, or cause confusing operator prompts,
        without improving safety.

        Preconditions (enforced by this method):
            - None.

        Behavior:
            - Sets `self.world_state["safety_mode"] = True`.
            - Returns a confirmation message.

        Failure cases (returns an error string):
            - None (this operation always succeeds).

        :return: Confirmation message indicating safety mode is locked.
        """
        self.world_state["safety_mode"] = True
        return "Safety mode locked."

    def move_to(self, x: float, y: float, yaw: float = None, speed: float = None) -> str:
        """
        Drive the rover to the target (x, y) with an optional yaw (radians).

        Preconditions (enforced by this method):
            - Safety mode must be disabled (`self.world_state["safety_mode"]` is False).
            - Target (x, y) must lie within the inclusive field bounds.
            - Target (x, y) must not intersect any configured no-go zone.

        Behavior:
            - On success, updates `self.world_state["pose"]["x"]` and `["y"]` to the target.
            - If `yaw` is provided, updates `self.world_state["pose"]["yaw"]`; if None, yaw is unchanged.
            - `speed` is accepted for realism but ignored in this simulation.

        Failure cases (returns an error string):
            - "ERROR: Safety mode is enabled. Unlock before moving."
            - "ERROR: Target location out of field bounds."
            - "ERROR: Target location lies within a no-go zone."

        :param x: Target x coordinate in meters.
        :param y: Target y coordinate in meters.
        :param yaw: Optional rover heading in radians. If None, heading is unchanged.
        :param speed: Optional travel speed parameter (ignored in this simulation).
        :return: Confirmation or error message.
        """
        if self.world_state["safety_mode"]:
            return "ERROR: Safety mode is enabled. Unlock before moving."

        if not self._within_bounds(x, y):
            return "ERROR: Target location out of field bounds."

        if self._in_no_go_zone(x, y):
            return "ERROR: Target location lies within a no-go zone."

        self.world_state["pose"].update({"x": x, "y": y})
        if yaw is not None:
            self.world_state["pose"]["yaw"] = yaw
        # speed is accepted for realism, ignored in this simulation
        return f"Moved to (x={x:.2f}, y={y:.2f}, yaw={self.world_state['pose']['yaw']:.2f})."

    def move_home(self) -> str:
        """
        Drive the rover to the configured home pose.

        Preconditions (enforced by this method):
            - Safety mode must be disabled (`self.world_state["safety_mode"]` is False).

        Behavior:
            - Retrieves `self.world_state["home_pose"]` and delegates to `move_to(...)`.
            - Returns the same confirmation or error message as `move_to`.

        Failure cases (returns an error string):
            - "ERROR: Safety mode is enabled. Unlock before moving."
            - "ERROR: Target location out of field bounds."        (propagated from `move_to`)
            - "ERROR: Target location lies within a no-go zone."   (propagated from `move_to`)

        :return: Confirmation or error message from the underlying `move_to(...)` call.
        """
        if self.world_state["safety_mode"]:
            return "ERROR: Safety mode is enabled. Unlock before moving."
        p = self.world_state["home_pose"]
        return self.move_to(p["x"], p["y"], p["yaw"])


    def harvest_fruit(self, plant_id: str) -> str:
        """
        Harvest fruit from a specified plant at the rover’s current position.

        Preconditions (enforced by this method):
            - Safety mode is disabled (`self.world_state["safety_mode"]` is False).
            - The plant exists in `self.world_state["plants"]`.
            - The plant currently has fruit (`has_fruit` is True).
            - The plant’s ripeness meets or exceeds `self.world_state["ripe_threshold"]`.
            - The rover is within `self.world_state["plant_tolerance_xy"]` of the plant’s pose.
            - Adding the plant’s `fruit_weight` will not exceed `hopper_capacity_kg`.

        Behavior:
            - On success, increases `hopper_load_kg` by the plant’s `fruit_weight`.
            - Marks the plant as harvested by setting `has_fruit = False`.
            - Returns a confirmation message including new hopper load.

        Failure cases (returns an error string):
            - "ERROR: Safety mode is enabled. Unlock before harvesting."
            - "ERROR: Unknown plant id."
            - "ERROR: No harvestable fruit on this plant."
            - "ERROR: Fruit not ripe enough to harvest."
            - "ERROR: Not within harvesting tolerance."
            - "ERROR: Hopper capacity exceeded."

        :param plant_id: Identifier of the target plant (key in `self.world_state["plants"]`).
        :return: Confirmation or error message.
        """
        if self.world_state["safety_mode"]:
            return "ERROR: Safety mode is enabled. Unlock before harvesting."

        plant = self.world_state["plants"].get(plant_id)
        if plant is None:
            return "ERROR: Unknown plant id."
        if not plant["has_fruit"]:
            return "ERROR: No harvestable fruit on this plant."
        if plant["ripeness"] < self.world_state["ripe_threshold"]:
            return "ERROR: Fruit not ripe enough to harvest."

        pose = self.world_state["pose"]
        if self._dist_xy(pose, plant["pose"]) > self.world_state["plant_tolerance_xy"]:
            return "ERROR: Not within harvesting tolerance."

        weight = plant["fruit_weight"]
        if self.world_state["hopper_load_kg"] + weight > self.world_state["hopper_capacity_kg"]:
            return "ERROR: Hopper capacity exceeded."

        # success
        self.world_state["hopper_load_kg"] += weight
        plant["has_fruit"] = False
        return f"Harvested {weight:.2f} kg from {plant_id}. Hopper now {self.world_state['hopper_load_kg']:.2f} kg."

    def dump_hopper(self) -> str:
        """
        Empty the hopper at the collection bin station.

        Preconditions (enforced by this method):
            - Safety mode is disabled (`self.world_state["safety_mode"]` is False).
            - The rover is within `self.world_state["station_tolerance_xy"]` of `stations["collection_bin"]`.

        Behavior:
            - On success, sets `hopper_load_kg` to 0.0.
            - Returns a confirmation message including the dumped mass.

        Failure cases (returns an error string):
            - "ERROR: Safety mode is enabled. Unlock before dumping."
            - "ERROR: Not at collection bin."

        :return: Confirmation or error message.
        """
        if self.world_state["safety_mode"]:
            return "ERROR: Safety mode is enabled. Unlock before dumping."

        bin_pose = self.world_state["stations"]["collection_bin"]
        if self._dist_xy(self.world_state["pose"], bin_pose) > self.world_state["station_tolerance_xy"]:
            return "ERROR: Not at collection bin."

        dumped = self.world_state["hopper_load_kg"]
        self.world_state["hopper_load_kg"] = 0.0
        return f"Dumped {dumped:.2f} kg at collection bin."

    def water_plant(self, plant_id: str, liters: float) -> str:
        """
        Water a plant by a specified amount.

        Preconditions (enforced by this method):
            - Safety mode is disabled (`self.world_state["safety_mode"]` is False).
            - The plant exists in `self.world_state["plants"]`.
            - `liters` is positive and less than or equal to `self.world_state["water_tank_l"]`.
            - The rover is within `self.world_state["plant_tolerance_xy"]` of the plant’s pose.
            - The resulting moisture would not exceed `self.world_state["max_moisture"]`.

        Behavior:
            - On success, decreases `water_tank_l` by `liters`.
            - Increases the plant’s `moisture` by `liters / water_tank_capacity_l`,
            capped at `max_moisture`.
            - Returns a confirmation message including remaining tank volume.

        Failure cases (returns an error string):
            - "ERROR: Safety mode is enabled. Unlock before watering."
            - "ERROR: Liters must be positive."
            - "ERROR: Unknown plant id."
            - "ERROR: Not within watering tolerance."
            - "ERROR: Not enough water in tank."
            - "ERROR: Moisture would exceed safe limit."

        :param plant_id: Identifier of the target plant (key in `self.world_state["plants"]`).
        :param liters: Amount of water to apply (liters).
        :return: Confirmation or error message.
        """
        if self.world_state["safety_mode"]:
            return "ERROR: Safety mode is enabled. Unlock before watering."

        if liters <= 0:
            return "ERROR: Liters must be positive."

        plant = self.world_state["plants"].get(plant_id)
        if plant is None:
            return "ERROR: Unknown plant id."

        if self._dist_xy(self.world_state["pose"], plant["pose"]) > self.world_state["plant_tolerance_xy"]:
            return "ERROR: Not within watering tolerance."

        if self.world_state["water_tank_l"] < liters:
            return "ERROR: Not enough water in tank."

        new_moisture = plant["moisture"] + liters / self.world_state["water_tank_capacity_l"]
        if new_moisture > self.world_state["max_moisture"]:
            return "ERROR: Moisture would exceed safe limit."

        # success
        self.world_state["water_tank_l"] -= liters
        plant["moisture"] = min(new_moisture, self.world_state["max_moisture"])
        return f"Watered {plant_id} with {liters:.2f} L. Tank: {self.world_state['water_tank_l']:.2f} L."

    def spray_pesticide(self, plant_id: str, ml: float) -> str:
        """
        Apply pesticide to a specified plant.

        Preconditions (enforced by this method):
            - Safety mode is disabled (`self.world_state["safety_mode"]` is False).
            - The plant exists in `self.world_state["plants"]`.
            - `ml` is positive and less than or equal to `self.world_state["pesticide_tank_ml"]`.
            - The plant currently has a pest issue (`pest` is True).
            - The rover is within `self.world_state["plant_tolerance_xy"]` of the plant’s pose.

        Behavior:
            - On success, decreases `pesticide_tank_ml` by `ml`.
            - Sets the plant’s `pest` flag to False.
            - Returns a confirmation message including remaining tank volume.

        Failure cases (returns an error string):
            - "ERROR: Safety mode is enabled. Unlock before spraying."
            - "ERROR: Milliliters must be positive."
            - "ERROR: Unknown plant id."
            - "ERROR: No pest detected on this plant."
            - "ERROR: Not within spraying tolerance."
            - "ERROR: Not enough pesticide in tank."

        :param plant_id: Identifier of the target plant (key in `self.world_state["plants"]`).
        :param ml: Amount of pesticide to apply (milliliters).
        :return: Confirmation or error message.
        """
        if self.world_state["safety_mode"]:
            return "ERROR: Safety mode is enabled. Unlock before spraying."

        if ml <= 0:
            return "ERROR: Milliliters must be positive."

        plant = self.world_state["plants"].get(plant_id)
        if plant is None:
            return "ERROR: Unknown plant id."
        if not plant["pest"]:
            return "ERROR: No pest detected on this plant."

        if self._dist_xy(self.world_state["pose"], plant["pose"]) > self.world_state["plant_tolerance_xy"]:
            return "ERROR: Not within spraying tolerance."

        if self.world_state["pesticide_tank_ml"] < ml:
            return "ERROR: Not enough pesticide in tank."

        # success
        self.world_state["pesticide_tank_ml"] -= ml
        plant["pest"] = False
        return f"Sprayed {ml:.0f} ml pesticide on {plant_id}. Tank: {self.world_state['pesticide_tank_ml']:.0f} ml."

    def refill_water_tank(self) -> str:
        """
        Refill the water tank to capacity at the water station.

        Preconditions (enforced by this method):
            - Safety mode is disabled (`self.world_state["safety_mode"]` is False).
            - The rover is within `self.world_state["station_tolerance_xy"]` of `stations["water_station"]`.

        Behavior:
            - On success, sets `self.world_state["water_tank_l"]` to `self.world_state["water_tank_capacity_l"]`.
            - Returns a confirmation message including the final tank volume.

        Failure cases (returns an error string):
            - "ERROR: Safety mode is enabled. Unlock before refilling."
            - "ERROR: Not at water station."

        :return: Confirmation or error message.
        """
        if self.world_state["safety_mode"]:
            return "ERROR: Safety mode is enabled. Unlock before refilling."

        st = self.world_state["stations"]["water_station"]
        if self._dist_xy(self.world_state["pose"], st) > self.world_state["station_tolerance_xy"]:
            return "ERROR: Not at water station."

        self.world_state["water_tank_l"] = self.world_state["water_tank_capacity_l"]
        return f"Water tank refilled to {self.world_state['water_tank_l']:.2f} L."

    def refill_pesticide(self) -> str:
        """
        Refill the pesticide tank to capacity at the pesticide refill station.

        Preconditions (enforced by this method):
            - Safety mode is disabled (`self.world_state["safety_mode"]` is False).
            - The rover is within `self.world_state["station_tolerance_xy"]` of `stations["pesticide_refill"]`.

        Behavior:
            - On success, sets `self.world_state["pesticide_tank_ml"]` to
            `self.world_state["pesticide_tank_capacity_ml"]`.
            - Returns a confirmation message including the final tank volume.

        Failure cases (returns an error string):
            - "ERROR: Safety mode is enabled. Unlock before refilling."
            - "ERROR: Not at pesticide refill station."

        :return: Confirmation or error message.
        """
        if self.world_state["safety_mode"]:
            return "ERROR: Safety mode is enabled. Unlock before refilling."

        st = self.world_state["stations"]["pesticide_refill"]
        if self._dist_xy(self.world_state["pose"], st) > self.world_state["station_tolerance_xy"]:
            return "ERROR: Not at pesticide refill station."

        self.world_state["pesticide_tank_ml"] = self.world_state["pesticide_tank_capacity_ml"]
        return f"Pesticide tank refilled to {self.world_state['pesticide_tank_ml']:.0f} ml."

    def recharge(self) -> str:
        """
        Recharge the rover's battery to 100% at the charging pad.

        Preconditions (enforced by this method):
            - Safety mode is disabled (`self.world_state["safety_mode"]` is False).
            - The rover is within `self.world_state["station_tolerance_xy"]` of `stations["charging_pad"]`.

        Behavior:
            - On success, sets `self.world_state["battery_pct"] = 100.0`.
            - Returns a confirmation message.

        Failure cases (returns an error string):
            - "ERROR: Safety mode is enabled. Unlock before recharging."
            - "ERROR: Not at charging pad."

        :return: Confirmation or error message.
        """
        if self.world_state["safety_mode"]:
            return "ERROR: Safety mode is enabled. Unlock before recharging."

        st = self.world_state["stations"]["charging_pad"]
        if self._dist_xy(self.world_state["pose"], st) > self.world_state["station_tolerance_xy"]:
            return "ERROR: Not at charging pad."

        self.world_state["battery_pct"] = 100.0
        return "Battery recharged to 100%."

    def sense_pose(self) -> Dict[str, float]:
        """
        Read-only: return the current rover pose as a mapping with keys 'x', 'y', and 'yaw'.

        Preconditions (enforced by this method):
            - None.

        Behavior:
            - Returns the current pose without modifying any state.

        Failure cases (returns an error string):
            - None (this operation always succeeds).

        :return: Dict containing {'x': float, 'y': float, 'yaw': float}.
        """
        return self.world_state["pose"]

    def sense_battery(self) -> str:
        """
        Read-only: report the current battery percentage as a formatted string (e.g., '80.0%').

        Preconditions (enforced by this method):
            - None.

        Behavior:
            - Returns the current battery percentage from `self.world_state["battery_pct"]`
            formatted with one decimal place and a trailing percent sign.
            - Does not modify any state.

        Failure cases (returns an error string):
            - None (this operation always succeeds).

        :return: Battery percentage string (e.g., '80.0%').
        """
        return f"{self.world_state['battery_pct']:.1f}%"

    def sense_hopper(self) -> Dict[str, float]:
        """
        Read-only: return the hopper load and capacity in kilograms.

        Preconditions (enforced by this method):
            - None.

        Behavior:
            - Returns a mapping with keys:
                - 'load_kg': current mass in the hopper.
                - 'capacity_kg': maximum hopper capacity.
            - Does not modify any state.

        Failure cases (returns an error string):
            - None (this operation always succeeds).

        :return: Dict with {'load_kg': float, 'capacity_kg': float}.
        """
        return {
            "load_kg": self.world_state["hopper_load_kg"],
            "capacity_kg": self.world_state["hopper_capacity_kg"],
        }

    def list_plants(self) -> Dict[str, dict]:
        """
        Read-only: enumerate all known plants and their attributes.

        Preconditions (enforced by this method):
            - None.

        Behavior:
            - Returns a mapping from plant_id to a dict containing:
            {'pose': {'x','y'}, 'ripeness': float, 'moisture': float,
            'pest': bool, 'has_fruit': bool, 'fruit_weight': float}.
            - Provides a snapshot view; does not modify any state.

        Failure cases (returns an error string):
            - None (this operation always succeeds).

        :return: Dict[str, dict] of plant metadata.
        """
        return self.world_state["plants"]

    def scan_plant(self, plant_id: str) -> dict:
        """
        Read-only: inspect a single plant and return its attributes, or an error payload if unknown.

        Preconditions (enforced by this method):
            - None.

        Behavior:
            - On success, returns:
            {
                'pose': {'x','y'},
                'ripeness': float,
                'moisture': float,
                'pest': bool,
                'has_fruit': bool,
                'fruit_weight': float
            }.
            - Does not modify any state.

        Failure cases (returns an error string):
            - Returns {'error': 'Unknown plant id.'} if the plant_id does not exist.

        :param plant_id: Identifier of the plant to inspect.
        :return: Attribute dict or {'error': 'Unknown plant id.'}.
        """
        plant = self.world_state["plants"].get(plant_id)
        if plant is None:
            return {"error": "Unknown plant id."}
        return {
            "pose": plant["pose"],
            "ripeness": plant["ripeness"],
            "moisture": plant["moisture"],
            "pest": plant["pest"],
            "has_fruit": plant["has_fruit"],
            "fruit_weight": plant["fruit_weight"],
        }

    def get_plant_pose(self, plant_id: str) -> dict:
        """
        Read-only: retrieve the XY pose of a plant, or an error payload if unknown.

        Preconditions (enforced by this method):
            - None.

        Behavior:
            - On success, returns {'x': float, 'y': float} for the specified plant.
            - Does not modify any state.

        Failure cases (returns an error string):
            - Returns {'error': 'Unknown plant id.'} if the plant_id does not exist.

        :param plant_id: Identifier of the plant.
        :return: {'x': float, 'y': float} or {'error': 'Unknown plant id.'}.
        """
        plant = self.world_state["plants"].get(plant_id)
        if plant is None:
            return {"error": "Unknown plant id."}
        return plant["pose"]

    def get_station_pose(self, station_name: str) -> dict:
        """
        Read-only: retrieve the pose of a named station, or an error payload if unknown.

        Preconditions (enforced by this method):
            - None.

        Behavior:
            - On success, returns {'x': float, 'y': float, 'yaw': float}.
            - Does not modify any state.

        Failure cases (returns an error string):
            - Returns {'error': 'Unknown station name.'} if the station is not defined.

        :param station_name: Name of the station (e.g., 'collection_bin', 'charging_pad').
        :return: {'x': float, 'y': float, 'yaw': float} or {'error': 'Unknown station name.'}.
        """
        st = self.world_state["stations"].get(station_name)
        if st is None:
            return {"error": "Unknown station name."}
        return st

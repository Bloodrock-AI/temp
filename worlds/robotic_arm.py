import json
from datetime import datetime
import uuid

from worlds.world import World
from typing import List, Dict, Optional
WORLD_STATE_DESCRIPTION = "Robotic Arm state: {}"

FUNCTION_SYSTEM_PROMPT = """
You operate a fixed-base industrial robotic arm. The arm's end-effector pose is (x, y, z) in meters and yaw in radians.
You must respect safety mode, workspace bounds, and no-go zones. Use the functions exactly with the parameters shown.
Pick/place are only valid when pose tolerances are satisfied and safety mode is unlocked.
"""

DECISION_SYSTEM_PROMPT = """
Decide a safe, correct sequence for the robotic arm. Always unlock safety before motion.
Use read-only checks (e.g., sense_pose, get_object_pose) if needed, but avoid unnecessary detours.
"""

class RoboticArm(World):
    def __init__(self):
        self.world_state_description = WORLD_STATE_DESCRIPTION
        self.function_system_prompt = FUNCTION_SYSTEM_PROMPT
        self.decision_system_prompt = DECISION_SYSTEM_PROMPT

        self.tool_definitions = self._get_tool_definitions()

        # Fixed environment & initial state
        self._init_world_state = {
            # Kinematics / pose
            "pose": {"x": 0.50, "y": 0.00, "z": 0.40, "yaw": 0.0},  # meters, radians
            "home_pose": {"x": 0.50, "y": 0.00, "z": 0.40, "yaw": 0.0},

            # Gripper/load
            "gripper_closed": False,
            "holding_object": None,
            "current_load": 0.0,
            "load_capacity": 5.0,  # kg

            # Safety
            "safety_mode": True,   # must be unlocked before any motion or grasp

            # Workspace bounds (axis-aligned box) and no-go zones (rectangles in XY, [xmin, xmax, ymin, ymax])
            "workspace_bounds": {"xmin": 0.10, "xmax": 1.20, "ymin": -0.50, "ymax": 0.50, "zmin": 0.05, "zmax": 0.60},
            "no_go_xy": [
                {"xmin": 0.70, "xmax": 0.85, "ymin": -0.10, "ymax": 0.10},   # e.g., a column or a human zone
            ],

            # Tolerances for pick/place alignment
            "pick_tolerance_xy": 0.02,   # meters
            "pick_tolerance_z": 0.01,    # meters
            "place_tolerance_xy": 0.02,  # meters
            "place_tolerance_z": 0.01,   # meters

            # Known stations (reference poses for convenience; agent can read or use explicit coordinates from prompt)
            "stations": {
                "assembly_table": {"x": 0.95, "y": 0.20, "z": 0.10, "yaw": 0.0},
                "quality_control": {"x": 1.05, "y": -0.20, "z": 0.10, "yaw": 0.0},
                "packaging_area": {"x": 0.80, "y": 0.35, "z": 0.10, "yaw": 0.0},
            },

            # Object catalog with unambiguous names, exact poses (top of object), and weights
            # z is at the grasping surface (top), not table height; pick requires exact z within tolerance
            "objects": {
                "box_small": {"weight": 2.0, "pose": {"x": 0.30, "y": 0.35, "z": 0.12}},
                "box_large": {"weight": 4.0, "pose": {"x": 0.28, "y": -0.30, "z": 0.15}},
                "gear_A":    {"weight": 1.0, "pose": {"x": 0.60, "y": 0.10, "z": 0.11}},
                "panel_X":   {"weight": 3.0, "pose": {"x": 0.90, "y": -0.10, "z": 0.14}},
            }
        }

        self.reset_world_state()

        # Prompts include explicit coordinates and/or object names so an agent can solve from text alone.
        # Each expected sequence uses precise function calls (no ambiguity).
        self.prompts = [
            {
                "prompt_id": "arm_1",
                "prompt": (
                    "Unlock safety. Move to (0.30, 0.35, 0.12, yaw=0.0) and pick 'box_small'. "
                    "Then move to (0.95, 0.20, 0.10, yaw=0.0) and place it."
                ),
                "setup_functions": [],
                "expected_sequences": [[
                    "unlock_safety_mode()",
                    "move_to(x=0.30, y=0.35, z=0.12, yaw=0.0)",
                    "open_gripper()",
                    "pick(object_name='box_small')",
                    "move_to(x=0.95, y=0.20, z=0.10, yaw=0.0)",
                    "place()"
                ]]
            },
            {
                "prompt_id": "arm_2",
                "prompt": (
                    "Pick 'box_large' at its known pose, "
                    "bring it to quality control station, then return home."
                ),
                "setup_functions": [],
                "expected_sequences": [
                [
                    "unlock_safety_mode()",
                    "move_to(x=0.28, y=-0.30, z=0.15, yaw=0.0)",
                    "open_gripper()",
                    "pick(object_name='box_large')",
                    "move_to(x=1.05, y=-0.20, z=0.10, yaw=0.0)",
                    "place()",
                    "move_home()"
                ],
                [
                    "unlock_safety_mode()",
                    "move_to(x=0.28, y=-0.30, z=0.15, yaw=0.0)",
                    "open_gripper()",
                    "pick(object_name='box_large')",
                    "move_to(x=1.05, y=-0.20, z=0.10, yaw=0.0)",
                    "place()",
                    "move_to(x=0.50, y=0.00, z=0.40, yaw=0.00)"
                ],]
            },
            {
                "prompt_id": "arm_3",
                "prompt": (
                    "Unlock safety. Check pose and list objects in ther order. Move to the pose of 'gear_A' and pick it. "
                    "Then place it at (0.80, 0.35, 0.10, yaw=0.0)."
                ),
                "setup_functions": [],
                "expected_sequences": [[
                    "unlock_safety_mode()",
                    "sense_pose()",
                    "list_objects()",
                    "move_to(x=0.60, y=0.10, z=0.11, yaw=0.0)",
                    "open_gripper()",
                    "pick(object_name='gear_A')",
                    "move_to(x=0.80, y=0.35, z=0.10, yaw=0.0)",
                    "place()"
                ]]
            },
            {
                "prompt_id": "arm_4",
                "prompt": (
                    "Move to (0.90, -0.10, 0.14, yaw=0.0) and pick 'panel_X'. "
                    "Rotate yaw to 1.57 rad while above (0.95, 0.20, 0.10) and place it there."
                ),
                "setup_functions": [],
                "expected_sequences": [[
                    "unlock_safety_mode()",
                    "move_to(x=0.90, y=-0.10, z=0.14, yaw=0.0)",
                    "open_gripper()",
                    "pick(object_name='panel_X')",
                    "move_to(x=0.95, y=0.20, z=0.10, yaw=1.57)",
                    "place()"
                ]]
            },
            {
                "prompt_id": "arm_5",
                "prompt": (
                    "Pick 'box_large' at (0.28, -0.30, 0.15), place it at (0.80, 0.35, 0.10). "
                    "Then pick 'box_small' at (0.30, 0.35, 0.12) and place it at (0.95, 0.20, 0.10). Finally, return home."
                ),
                "setup_functions": [],
                "expected_sequences": [[
                    "unlock_safety_mode()",
                    "move_to(x=0.28, y=-0.30, z=0.15, yaw=0.0)",
                    "open_gripper()",
                    "pick(object_name='box_large')",
                    "move_to(x=0.80, y=0.35, z=0.10, yaw=0.0)",
                    "place()",
                    "move_to(x=0.30, y=0.35, z=0.12, yaw=0.0)",
                    "open_gripper()",
                    "pick(object_name='box_small')",
                    "move_to(x=0.95, y=0.20, z=0.10, yaw=0.0)",
                    "place()",
                    "move_home()"
                ],
                [
                    "unlock_safety_mode()",
                    "move_to(x=0.28, y=-0.30, z=0.15, yaw=0.0)",
                    "open_gripper()",
                    "pick(object_name='box_large')",
                    "move_to(x=0.80, y=0.35, z=0.10, yaw=0.0)",
                    "place()",
                    "move_to(x=0.30, y=0.35, z=0.12, yaw=0.0)",
                    "open_gripper()",
                    "pick(object_name='box_small')",
                    "move_to(x=0.95, y=0.20, z=0.10, yaw=0.0)",
                    "place()",
                    "move_to(x=0.50, y=0.00, z=0.40, yaw=0.00)"
                ]]
            },
            {
                "prompt_id": "arm_6",
                "prompt": (
                    "Unlock safety. Read current pose and gripper state in that order. Query the pose of 'gear_A' and move to it at "
                    "speed 0.2. When there, pick it up. Query the pose of the 'packaging_area' "
                    "station and move to it with yaw=1.57 (rotate end-effector) and place the object. Finally, return home and lock safety mode"
                ),
                "setup_functions": [],
                "expected_sequences": [[
                    "unlock_safety_mode()",
                    "sense_pose()",
                    "sense_gripper()",
                    "get_object_pose(object_name='gear_A')",
                    "move_to(x=0.60, y=0.10, z=0.11, yaw=0.0, speed=0.2)",
                    "open_gripper()",
                    "pick(object_name='gear_A')",
                    "get_station_pose(station_name='packaging_area')",
                    "move_to(x=0.80, y=0.35, z=0.10, yaw=1.57)",
                    "place()",
                    "move_home()",
                    "lock_safety_mode()",
                ],
                [
                    "unlock_safety_mode()",
                    "sense_pose()",
                    "sense_gripper()",
                    "get_object_pose(object_name='gear_A')",
                    "move_to(x=0.60, y=0.10, z=0.11, yaw=0.0, speed=0.2)",
                    "open_gripper()",
                    "pick(object_name='gear_A')",
                    "get_station_pose(station_name='packaging_area')",
                    "move_to(x=0.80, y=0.35, z=0.10, yaw=1.57)",
                    "place()",
                    "move_to(x=0.50, y=0.00, z=0.40, yaw=0.00)",
                    "lock_safety_mode()",
                ]]
            },
            {
                "prompt_id": "arm_7",
                "prompt": (
                    "List objects. Unlock safety. Pick 'box_large' at its known pose and place it at the packaging area. "
                    "Lock safety for an operator pass-through, read the current pose, then unlock. Pick 'box_small', and move to "
                    "the assembly table with yaw = 1.576. Then, descend 10 centimeters and place the object you are holding. Finally, return home."
                ),
                "setup_functions": [],
                "expected_sequences": [
                [
                    "list_objects()",
                    "unlock_safety_mode()",
                    "move_to(x=0.28, y=-0.30, z=0.15, yaw=0.0)",
                    "open_gripper()",
                    "pick(object_name='box_large')",
                    "move_to(x=0.80, y=0.35, z=0.10, yaw=0.0)",
                    "place()",
                    "lock_safety_mode()",
                    "sense_pose()",
                    "unlock_safety_mode()",
                    "move_to(x=0.30, y=0.35, z=0.12, yaw=0.0)",
                    "open_gripper()",
                    "pick(object_name='box_small')",
                    "move_to(x=0.95, y=0.20, z=0.20, yaw=1.57)",
                    "move_to(x=0.95, y=0.20, z=0.10, yaw=1.57)",
                    "place()",
                    "move_to(x=0.50, y=0.00, z=0.40, yaw=0.00)"
                ],
                [
                    "list_objects()",
                    "unlock_safety_mode()",
                    "move_to(x=0.28, y=-0.30, z=0.15, yaw=0.0)",
                    "pick(object_name='box_large')",
                    "get_station_pose(station_name='packaging_area')",
                    "move_to(x=0.80, y=0.35, z=0.10, yaw=0.0)",
                    "place()",
                    "lock_safety_mode()",
                    "sense_pose()",
                    "unlock_safety_mode()",
                    "move_to(x=0.30, y=0.35, z=0.12, yaw=0.0)",
                    "pick(object_name='box_small')",
                    "move_to(x=0.95, y=0.20, z=0.20, yaw=1.57)",
                    "move_to(x=0.95, y=0.20, z=0.10, yaw=1.57)",
                    "place()",
                    "move_home()"
                ]]
        },
        {
            "prompt_id": "arm_8",
            "prompt": (
                "Pick 'gear_A' and then pick 'box_small'. Deliver both to the assembly table and then return home."
            ),
            "setup_functions": [],
            "expected_sequences": [[
                "unlock_safety_mode()",
                "move_to(x=0.60, y=0.10, z=0.11, yaw=0.0)",
                "open_gripper()",
                "pick(object_name='gear_A')",
                "move_to(x=0.95, y=0.20, z=0.10, yaw=0.0)",
                "place()",
                "move_to(x=0.30, y=0.35, z=0.12, yaw=0.0)",
                "open_gripper()",
                "pick(object_name='box_small')",
                "move_to(x=0.95, y=0.20, z=0.10, yaw=0.0)",
                "place()",
                "move_to(x=0.50, y=0.00, z=0.40, yaw=0.00)"
            ],
            [
                "unlock_safety_mode()",
                "move_to(x=0.60, y=0.10, z=0.11, yaw=0.0)",
                "open_gripper()",
                "pick(object_name='gear_A')",
                "move_to(x=0.95, y=0.20, z=0.10, yaw=0.0)",
                "place()",
                "move_to(x=0.30, y=0.35, z=0.12, yaw=0.0)",
                "open_gripper()",
                "pick(object_name='box_small')",
                "move_to(x=0.95, y=0.20, z=0.10, yaw=0.0)",
                "place()",
                "move_home()"
            ]]
        }
        ]


    def _within_bounds(self, x, y, z):
        """
        Check whether a target Cartesian point lies inside the arm's configured workspace box.

        The check is **inclusive** on all axes (xmin ≤ x ≤ xmax, etc.) and uses the
        axis-aligned bounds in `self.world_state["workspace_bounds"]`:
        `{xmin, xmax, ymin, ymax, zmin, zmax}` (units: meters).

        Note:
            This does **not** consider safety exclusion areas (no-go zones). Use
            `_in_no_go_zone(x, y)` separately when validating a target.

        :param x: Target x coordinate in meters.
        :param y: Target y coordinate in meters.
        :param z: Target z coordinate in meters.
        :return: True if (x, y, z) is within the inclusive workspace bounds; False otherwise.
        """
        b = self.world_state["workspace_bounds"]
        return (b["xmin"] <= x <= b["xmax"] and
                b["ymin"] <= y <= b["ymax"] and
                b["zmin"] <= z <= b["zmax"])

    def _in_no_go_zone(self, x, y):
        """
        Determine whether the XY point lies inside any configured no-go (exclusion) rectangle.

        Each rectangle is defined in `self.world_state["no_go_xy"]` as a dict
        `{xmin, xmax, ymin, ymax}` (units: meters). The check is **inclusive** on edges.

        Notes:
            - Only the XY plane is considered; Z is intentionally ignored.
            - This function is typically used alongside `_within_bounds(...)` during motion validation.

        :param x: X coordinate in meters.
        :param y: Y coordinate in meters.
        :return: True if (x, y) falls within any no-go rectangle; False otherwise.
        """
        for rect in self.world_state["no_go_xy"]:
            if rect["xmin"] <= x <= rect["xmax"] and rect["ymin"] <= y <= rect["ymax"]:
                return True
        return False

    def _dist_xy(self, a, b):
        """
        Compute the Euclidean distance between two points in the XY plane.

        Expects mappings `a` and `b` with keys `"x"` and `"y"` (other keys like `"z"` or `"yaw"`
        are ignored). Returned distance is in meters.

        :param a: Mapping with float `a["x"]` and `a["y"]`.
        :param b: Mapping with float `b["x"]` and `b["y"]`.
        :return: Euclidean distance sqrt((ax - bx)^2 + (ay - by)^2) in meters.
        :raises KeyError: If either mapping is missing the `"x"` or `"y"` key.
        """
        dx = a["x"] - b["x"]
        dy = a["y"] - b["y"]
        return (dx*dx + dy*dy) ** 0.5


    def unlock_safety_mode(self) -> str:
        """
        Disable the arm's safety lock, allowing motion and manipulation commands to execute.

        Many state-changing operations (e.g., `move_to`, `pick`, `place`) require that
        safety mode be disabled. This method sets `self.world_state["safety_mode"]` to False.

        :return: Confirmation message indicating safety mode has been unlocked.
        """
        self.world_state["safety_mode"] = False
        return "Safety mode unlocked."

    def lock_safety_mode(self) -> str:
        """
        Enable the arm's safety lock, preventing motion and manipulation commands.

        When safety mode is enabled (`self.world_state["safety_mode"]` is True), 
        operations such as `move_to`, `pick`, and `place` will fail with an error message.
        Locking the safety mode is typically done after completing a task or when
        the arm is idle to ensure operational safety.

        :return: Confirmation message indicating safety mode has been locked.
        """
        self.world_state["safety_mode"] = True
        return "Safety mode locked."

    def move_to(self, x: float, y: float, z: float, yaw: float = None, speed: float = None) -> str:
        """
        Command a Cartesian point-to-point move of the end-effector to (x, y, z) with an optional yaw.

        Preconditions (enforced by this method):
            - Safety mode must be disabled (`self.world_state["safety_mode"]` is False).
            - Target (x, y, z) must lie within the inclusive workspace bounds.
            - Target (x, y) must not intersect any configured no-go zone.

        Behavior:
            - On success, updates `self.world_state["pose"]` to the target position.
            - If `yaw` is provided, updates yaw; if None, yaw is left unchanged.
            - `speed` is accepted for realism but ignored in this simulation.

        Failure cases (returns an error string):
            - "ERROR: Safety mode is enabled. Unlock before moving."
            - "ERROR: Target pose out of workspace bounds."
            - "ERROR: Target pose lies within a no-go zone."

        :param x: Target x coordinate in meters.
        :param y: Target y coordinate in meters.
        :param z: Target z coordinate in meters.
        :param yaw: Optional end-effector yaw in radians. If None, yaw is unchanged.
        :param speed: Optional motion speed parameter (ignored in this simulation).
        :return: Confirmation or error message.
        """
        if self.world_state["safety_mode"]:
            return "ERROR: Safety mode is enabled. Unlock before moving."

        if not self._within_bounds(x, y, z):
            return "ERROR: Target pose out of workspace bounds."

        if self._in_no_go_zone(x, y):
            return "ERROR: Target pose lies within a no-go zone."

        self.world_state["pose"].update({"x": x, "y": y, "z": z})
        if yaw is not None:
            self.world_state["pose"]["yaw"] = yaw
        # speed is ignored in this simulation but accepted for realism
        return f"Moved to (x={x:.2f}, y={y:.2f}, z={z:.2f}, yaw={self.world_state['pose']['yaw']:.2f})."

    def move_home(self) -> str:
        """
        Move the end-effector to the configured home pose.

        Preconditions:
            - Safety mode must be disabled (same as `move_to`).

        Behavior:
            - Uses `self.world_state["home_pose"]` and delegates to `move_to(...)`.
            - Returns the same confirmation or error string as `move_to`.

        :return: Confirmation or error message from the underlying `move_to(...)` call.
        """
        if self.world_state["safety_mode"]:
            return "ERROR: Safety mode is enabled. Unlock before moving."
        p = self.world_state["home_pose"]
        return self.move_to(p["x"], p["y"], p["z"], p["yaw"])

    def open_gripper(self) -> str:
        """
        Open the gripper — use only with intent (e.g., immediately before grasping, or after releasing).

        Safety & policy:
            - The gripper must be open before picking up an object.
            - Do not open while transporting or supporting an object; objects should only be moved while the gripper is closed.
            - Avoid issuing repeated open commands when the gripper is already open:
            it can retrigger actuation cycles (pneumatic/vacuum), cause pressure fluctuations, part slip/drops,
            and unnecessary wear or faults.
            - Opening while supporting a load is considered harmful.

        Operational note:
            - This action changes only the jaw state; higher-level logic must ensure it is done at an appropriate time.

        :return: Confirmation message.
        """
        self.world_state["gripper_closed"] = False
        return "Gripper opened."

    def close_gripper(self) -> str:
        """
        Close the gripper — use only with intent. Gripper is automatically closed after picking up an object.

        Safety & policy:
            - Objects must be transported with the gripper closed; do not move an object with the gripper open.
            - Avoid issuing repeated close commands when the gripper is already closed. In real cells this is not idempotent:
            repeated closes can induce force spikes, over-squeeze, controller faults, or premature mechanical wear.
            - Closing without an object present does not create a grasp; alignment and contact must be established beforehand.

        Operational note:
            - This action changes only the jaw state; higher-level logic must ensure conditions are appropriate for closing.

        :return: Confirmation message.
        """
        self.world_state["gripper_closed"] = True
        return "Gripper closed."

    def pick(self, object_name: str) -> str:
        """
        Grasp a named object at the current end-effector pose.

        Preconditions (enforced):
            - Safety mode is disabled.
            - No object is currently held.
            - The named object exists in the scene catalogue.
            - The gripper is OPEN prior to grasping.
            - The current end-effector pose is within the object's pick tolerances
            (|Δx,y| ≤ pick_tolerance_xy and |Δz| ≤ pick_tolerance_z).
            - Object weight does not exceed the configured load capacity.

        Behavior on success:
            - Secures the object (marks it as held), records its load, and CLOSES the gripper.
            - Returns a confirmation message.

        Failure cases (returns an error string):
            - "ERROR: Safety mode is enabled. Unlock before picking."
            - "ERROR: Already holding an object."
            - "ERROR: Unknown object name."
            - "ERROR: Gripper must be open before pick."
            - "ERROR: Pose not aligned for pick (tolerance exceeded)."
            - "ERROR: Object too heavy for gripper."

        Safety & policy:
            - Opening the gripper while supporting a load is unsafe; grasp should be established with the
            gripper open and then secured by closing as part of the grasp cycle.
            - Avoid unnecessary grasp attempts; repeated cycles increase wear and risk.

        :param object_name: Unique identifier of the target object.
        :return: Confirmation or error message.
        """
        if self.world_state["safety_mode"]:
            return "ERROR: Safety mode is enabled. Unlock before picking."

        if self.world_state["holding_object"] is not None:
            return "ERROR: Already holding an object."

        obj = self.world_state["objects"].get(object_name)
        if obj is None:
            return "ERROR: Unknown object name."

        if self.world_state["gripper_closed"]:
            return "ERROR: Gripper must be open before pick."

        pose = self.world_state["pose"]
        target = obj["pose"]
        tol_xy = self.world_state["pick_tolerance_xy"]
        tol_z = self.world_state["pick_tolerance_z"]

        if self._dist_xy(pose, target) > tol_xy or abs(pose["z"] - target["z"]) > tol_z:
            return "ERROR: Pose not aligned for pick (tolerance exceeded)."

        if obj["weight"] > self.world_state["load_capacity"]:
            return "ERROR: Object too heavy for gripper."

        # success
        self.world_state["holding_object"] = object_name
        self.world_state["current_load"] = obj["weight"]
        self.world_state["gripper_closed"] = True
        return f"Picked '{object_name}'."

    def place(self) -> str:
        """
        Release the currently held object at the current end-effector pose.

        Preconditions (enforced):
            - Safety mode is disabled.
            - An object is currently held.
            - The pose lies within the inclusive workspace bounds and outside no-go zones.

        Behavior on success:
            - Updates the placed object's pose to the current end-effector pose.
            - Clears the held object and load, and OPENS the gripper.
            - Returns a confirmation message including the final coordinates.

        Failure cases (returns an error string):
            - "ERROR: Safety mode is enabled. Unlock before placing."
            - "ERROR: No object to place."
            - "ERROR: Cannot place outside workspace bounds."
            - "ERROR: Cannot place in a no-go zone."

        Safety & policy:
            - Objects should be transported with the gripper CLOSED; releasing occurs only at the
            intended destination.
            - Although this simulator opens the gripper on success and does not separately verify a
            closed state beforehand, in real cells releasing with an open/unstable grasp is unsafe.

        :return: Confirmation or error message.
        """
        if self.world_state["safety_mode"]:
            return "ERROR: Safety mode is enabled. Unlock before placing."

        obj_name = self.world_state["holding_object"]
        if obj_name is None:
            return "ERROR: No object to place."

        pose = self.world_state["pose"]
        if not self._within_bounds(pose["x"], pose["y"], pose["z"]):
            return "ERROR: Cannot place outside workspace bounds."

        if self._in_no_go_zone(pose["x"], pose["y"]):
            return "ERROR: Cannot place in a no-go zone."

        # success: update object catalog with new pose
        self.world_state["objects"][obj_name]["pose"] = {"x": pose["x"], "y": pose["y"], "z": pose["z"]}
        self.world_state["holding_object"] = None
        self.world_state["current_load"] = 0.0
        self.world_state["gripper_closed"] = False
        return f"Placed '{obj_name}' at (x={pose['x']:.2f}, y={pose['y']:.2f}, z={pose['z']:.2f})."


    def sense_pose(self) -> dict:
        """
        Read-only: return the current end-effector pose.

        Purpose:
            - Verify actual position/orientation before moving, grasping, or releasing.
            - Useful for tolerance checks and for logging/telemetry.

        Returns:
            Dict with fields: {"x": float, "y": float, "z": float, "yaw": float} in SI units.

        Side effects:
            - None (does not alter state).
        """
        return self.world_state["pose"]

    def sense_gripper(self) -> str:
        """
        Read-only: report the current gripper state.

        Purpose:
            - Confirm preconditions (e.g., open before picking up an object; closed while transporting).
            - Useful for safety checks and sequencing.

        Returns:
            "open" or "closed".

        Side effects:
            - None (does not alter state).
        """
        return "closed" if self.world_state["gripper_closed"] else "open"

    def list_objects(self) -> dict:
        """
        Read-only: enumerate known objects with their weights and poses.

        Purpose:
            - Inspect available items for planning (e.g., select objects within load capacity).
            - Retrieve exact target poses without relying on hardcoded coordinates.

        Returns:
            Mapping of object_name -> {"weight": float (kg), "pose": {"x": float, "y": float, "z": float}}.

        Side effects:
            - None (does not alter state).
        """
        return {k: {"weight": v["weight"], "pose": v["pose"]} for k, v in self.world_state["objects"].items()}

    def get_object_pose(self, object_name: str) -> dict:
        """
        Read-only: return the pose of a named object, or an error payload if unknown.

        Purpose:
            - Obtain the precise pick location from the scene catalog prior to aligning.

        Returns:
            - On success: {"x": float, "y": float, "z": float}.
            - On failure: {"error": "Unknown object name."}

        Side effects:
            - None (does not alter state).
        """
        obj = self.world_state["objects"].get(object_name)
        if obj is None:
            return {"error": "Unknown object name."}
        return obj["pose"]

    def get_station_pose(self, station_name: str) -> dict:
        """
        Read-only: return the pose of a named station, or an error payload if unknown.

        Purpose:
            - Obtain the precise destination pose for transport/release operations.

        Returns:
            - On success: {"x": float, "y": float, "z": float, "yaw": float}.
            - On failure: {"error": "Unknown station name."}

        Side effects:
            - None (does not alter state).
        """
        st = self.world_state["stations"].get(station_name)
        if st is None:
            return {"error": "Unknown station name."}
        return st

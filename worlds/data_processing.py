import json
from datetime import datetime
import uuid

from worlds.world import World
from typing import List, Dict, Optional

FUNCTION_SYSTEM_PROMPT="""
You are a helpful assistant that is responsible for executing data processing tasks using structured datasets. The dataset is provided. Always check the state and use the functions to make changes based on the user prompt.
"""
DECISION_SYSTEM_PROMPT="""
You are a helpful assistant that is responsible for executing data processing tasks using structured datasets. The dataset is provided.
"""
WORLD_STATE_DESCRIPTION = "Dataset: {}"

class DataProcessing(World):
    def __init__(self):
        self.world_state_description = WORLD_STATE_DESCRIPTION
        self.function_system_prompt = FUNCTION_SYSTEM_PROMPT
        self.decision_system_prompt = DECISION_SYSTEM_PROMPT
        
        self.tool_definitions = self._get_tool_definitions()
        self._init_world_state = {
            "dataset": [
                {"employee_id": 1, "name": "Alice", "age": 35, "salary": 70000, "department": "HR", "status": "active", "sales": 5000, "category": "management", "date": "2024-02-01"},
                {"employee_id": 2, "name": "Bob", "age": 28, "salary": 50000, "department": "Engineering", "status": "inactive", "sales": 3000, "category": "development", "date": "2024-02-02"},
                {"employee_id": 3, "name": "Charlie", "age": 40, "salary": 90000, "department": "HR", "status": "active", "sales": 7000, "category": "management", "date": "2024-02-03"},
                {"employee_id": 4, "name": "Dana", "age": 25, "salary": 45000, "department": "Marketing", "status": "active", "sales": 2000, "category": "advertising", "date": "2024-02-04"},
                {"employee_id": 5, "name": "Eve", "age": 32, "salary": 75000, "department": "Engineering", "status": "active", "sales": 6000, "category": "development", "date": "2024-02-05"},
                {"employee_id": 6, "name": "Frank", "age": 45, "salary": 100000, "department": "Finance", "status": "inactive", "sales": 8000, "category": "accounting", "date": "2024-02-06"}
            ]
        }
        self.world_state = self._init_world_state
        self.prompts = [
            {
                "prompt": "Print all employees in the 'HR' department who are currently active.",
                "expected_sequence": ["filter_data(field='department', value='HR', condition='equals')", "filter_data(field='status', value='active', condition='equals')"]
            },
            {
                "prompt": "Find employees older than 30 and sort them by salary in descending order.",
                "expected_sequence": ["filter_data(field='age', value=30, condition='greater')", "sort_data(field='salary', order='descending')"]
            },
            {
                "prompt": "Calculate the total sales from all active employees in the dataset.",
                "expected_sequence": ["filter_data(field='status', value='active', condition='equals')", "aggregate_data('sales', 'sum')"]
            },
            {
                "prompt": "Transform all employee names to uppercase and sort by employee_id in ascending order.",
                "expected_sequence": ["transform_data('name', 'uppercase')", "sort_data(transformed_'employee_id', 'ascending')"]
            },
            {
                "prompt": "Keep only employees in the 'Finance' department and count how many remain.",
                "expected_sequence": ["filter_data('department', 'Finance', 'equals')", "aggregate_data('employee_id', 'count')"]
            },
            {
                "prompt": "Lowercase all category names and sort employees by 'date' in ascending order.",
                "expected_sequence": ["transform_data('category', 'lowercase')", "sort_data(transformed_'date', 'ascending')"]
            },
            {
                "prompt": "Find and keep only the employee with the highest salary.",
                "expected_sequence": ["sort_data('salary', 'descending')", "filter_data('salary', dataset[0]['salary'], 'equals')"]
            }
        ]

    def add_numbers(self, a: int, b: int) -> int:
        """
        Adds two integers and returns the result.
        
        :param a: The first integer.
        :param b: The second integer.
        :return: Sum of a and b.
        """
        self.world_state["calculations"].append(f"{a} + {b} = {a + b}")
        return a + b

    def subtract_numbers(self, a: int, b: int) -> int:
        """
        Subtracts the second integer from the first and returns the result.
        
        :param a: The first integer.
        :param b: The second integer.
        :return: Difference of a and b.
        """
        self.world_state["calculations"].append(f"{a} - {b} = {a - b}")
        return a - b

    def multiply_numbers(self, a: int, b: int) -> int:
        """
        Multiplies two integers and returns the product.
        
        :param a: The first integer.
        :param b: The second integer.
        :return: Product of a and b.
        """
        self.world_state["calculations"].append(f"{a} * {b} = {a * b}")
        return a * b

    def divide_numbers(self, a: int, b: int) -> Optional[float]:
        """
        Divides the first integer by the second and returns the result.
        
        :param a: The numerator.
        :param b: The denominator. Must not be zero.
        :return: Quotient of a and b, or None if division by zero.
        """
        self.world_state["calculations"].append(f"{a} / {b} = {a / b if b != 0 else None}")
        if b == 0:
            return None
        return a / b

    def power(self, base: int, exponent: int) -> int:
        """
        Raises a base number to a given exponent and returns the result.
        
        :param base: The base number.
        :param exponent: The exponent to raise the base to.
        :return: base raised to the power of exponent.
        """
        self.world_state["calculations"].append(f"{base} ^ {exponent} = {base ** exponent}")
        return base ** exponent

    def calculate_average(self, numbers: List[int]) -> float:
        """
        Calculates the average of a list of integers.
        
        :param numbers: A list of integers.
        :return: The average value.
        """
        self.world_state["calculations"].append(f"Average of {numbers} = {sum(numbers) / len(numbers) if numbers else 0.0}")
        if not numbers:
            return 0.0
        return sum(numbers) / len(numbers)

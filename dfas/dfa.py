from dataclasses import dataclass, field
from typing import List, Tuple, Optional

from agents import FunctionCalled

@dataclass
class Node:
    name: str
    transitions: List["Transition"] = field(default_factory=list)
    is_final: bool = False

@dataclass
class Transition:
    symbols: List[str]
    _from: Node
    _to: Node

@dataclass
class FunctionArgument:
    name: str
    value: Optional[Any]
    excluded_values: Optional[List[Any]]
    type: str

@dataclass
class FunctionCall:
    name: str
    arguments: Dict[str, FunctionArgument]
    
@dataclass
class Prompt:
    text: str
    expected_sequence: List[str]
    dfa: List[Node]
    alphabet: Dict[str, FunctionCall]

from abc import ABC
from typing import Any


class VariablesOperator(ABC):
    def __init__(self):
        self.variables: dict[str, Any] = {}

    def set_variables(self, variables: dict[str, Any]):
        self.variables = variables

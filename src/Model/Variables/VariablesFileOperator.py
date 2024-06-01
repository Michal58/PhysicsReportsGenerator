import os.path
from typing import Any
import pickle

from settings_namespace import VARIABLES_FILE_NAME


class VariablesFileOperator:
    def __init__(self, selected_directory: str) -> None:
        self.selected_directory = selected_directory
        self.variables_filepath = os.path.join(self.selected_directory, VARIABLES_FILE_NAME)

    def save_variables(self, variables: dict[str, Any]) -> bool:
        try:
            with open(self.variables_filepath, 'wb') as file:
                pickle.dump(variables, file)
                return True
        except (FileNotFoundError, pickle.PicklingError):
            return False

    def read_variables(self) -> dict[str, Any]:
        try:
            with open(self.variables_filepath, 'rb') as file:
                return pickle.load(file)
        except (FileNotFoundError, pickle.UnpicklingError):
            return {}

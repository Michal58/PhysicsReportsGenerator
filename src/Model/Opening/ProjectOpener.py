import os
from typing import Any

from Model.Opening.SettingsOperator import SettingsOperator
from Model.Variables.VariablesFileOperator import VariablesFileOperator


class ProjectOpener:
    def __init__(self, open_directory: str):
        self.read_settings: dict[str, str] = {}
        self.open_directory: str = open_directory

    def open_project(self) -> bool:
        if not os.path.exists(self.open_directory):
            return False
        self.read_settings = SettingsOperator.read(self.open_directory)
        if self.read_settings == {}:
            return False
        else:
            return True

    def get_settings(self) -> dict[str, str]:
        return self.read_settings

    def get_variables(self)->dict[str, Any]:
        var_Operator: VariablesFileOperator=VariablesFileOperator(self.open_directory)
        return var_Operator.read_variables()

import os.path
import sys

from Model.FilesDirectoriesManager import FilesDirectoriesManager
from Model.Opening.SettingsOperator import SettingsOperator
from src.settings_namespace import *


class ProjectCreator:
    def __init__(self, creation_dir: str) -> None:
        self.basic_settings: dict[str, str] = {}
        self.creation_dir: str = creation_dir

    def create_settings(self) -> None:
        # json field->path to directory with files
        self.basic_settings = {setting_field: os.path.join(self.creation_dir, setting_field) for setting_field in
                               SETTINGS_FIELDS_LIST}
        SettingsOperator.save(self.creation_dir, self.basic_settings)

    def create(self) -> bool:
        if not os.path.exists(self.creation_dir):
            return False
        self.create_settings()
        dir_manager=FilesDirectoriesManager(self.basic_settings)
        return dir_manager.create_non_existent_directories()

    def get_settings(self) -> dict[str, str]:
        return self.basic_settings


def main_function() -> None:
    USER_PATH: str = sys.argv[1]
    creator: ProjectCreator = ProjectCreator(USER_PATH)
    print(creator.create())


if __name__ == '__main__':
    main_function()

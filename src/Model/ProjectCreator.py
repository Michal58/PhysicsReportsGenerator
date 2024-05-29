import os.path
import sys

from src.Model.SettingsSaver import SettingsSaver
from src.settings_namespace import *


class ProjectCreator:
    def __init__(self, creation_dir: str) -> None:
        self.basic_settings: dict[str, str] = {}
        self.creation_dir: str = creation_dir

    def create_settings(self) -> None:
        # json field->path to directory with files
        self.basic_settings = {setting_field: os.path.join(self.creation_dir, setting_field) for setting_field in
                               SETTINGS_FIELDS_LIST}
        SettingsSaver.save(self.creation_dir, self.basic_settings)

    def create(self) -> bool:
        try:
            self.create_settings()
            for directory_path in self.basic_settings.values():
                os.mkdir(directory_path)
            return True
        except (FileNotFoundError, NotADirectoryError):
            return False


def main_function() -> None:
    USER_PATH: str = sys.argv[1]
    creator: ProjectCreator = ProjectCreator(USER_PATH)
    print(creator.create())


if __name__ == '__main__':
    main_function()

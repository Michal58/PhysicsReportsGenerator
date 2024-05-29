import json
import os.path

from src.settings_namespace import SETTINGS_FILE_NAME


class SettingsSaver:
    def __init__(self) -> None:
        pass

    @staticmethod
    def save(save_dir, fields_values: dict[str, str]) -> None:
        filepath = os.path.join(save_dir, SETTINGS_FILE_NAME)

        with open(filepath, 'w') as settings_file:
            json.dump(fields_values, settings_file, ensure_ascii=False)


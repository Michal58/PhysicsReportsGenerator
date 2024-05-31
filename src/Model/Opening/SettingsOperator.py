import json
import os.path

from src.settings_namespace import SETTINGS_FILE_NAME, SETTINGS_FIELDS_LIST, ENCODING


class SettingsOperator:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_settings_filepath(directory_path: str) -> str:
        return os.path.join(directory_path, SETTINGS_FILE_NAME)

    @staticmethod
    def save(save_dir: str, fields_values: dict[str, str]) -> None:
        filepath: str = SettingsOperator.get_settings_filepath(save_dir)
        try:
            with open(filepath, 'w', encoding=ENCODING) as settings_file:
                json.dump(fields_values, settings_file, ensure_ascii=False)
        except FileNotFoundError:
            pass

    @staticmethod
    def validate_settings(settings: dict[str, str]) -> bool:
        for setting_field in SETTINGS_FIELDS_LIST:
            if setting_field not in settings:
                return False
        return True

    @staticmethod
    def read(read_dir: str) -> dict[str, str]:
        filepath: str = SettingsOperator.get_settings_filepath(read_dir)

        try:
            with open(filepath, 'r', encoding=ENCODING) as setting_file:
                read_fields: dict[str, str] = json.load(setting_file)
                if SettingsOperator.validate_settings(read_fields):
                    return read_fields
                else:
                    return {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

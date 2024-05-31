import os.path

from settings_namespace import ENCODING


class GeneratedFilesManager:
    GENERATED_TEX_PARTS_EXTENSION = 'texpart'

    def __int__(self):
        pass

    @staticmethod
    def save_from_str(content: str, dir_path: str, base_name: str) -> bool:
        try:
            full_path: str = os.path.join(dir_path, f'{base_name}.{GeneratedFilesManager.GENERATED_TEX_PARTS_EXTENSION}')
            with open(full_path, 'w',encoding=ENCODING) as file:
                file.write(content)
                return True
        except FileNotFoundError:
            return False

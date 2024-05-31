import os.path


class GeneratedFilesManager:
    GENERATED_TEX_PARTS_EXTENSION = 'texpart'

    def __int__(self):
        pass

    @staticmethod
    def save_from_str(content: str, dir_path: str, base_name: str) -> bool:
        try:
            full_path: str = os.path.join(dir_path, f'{base_name}.{GeneratedFilesManager.GENERATED_TEX_PARTS_EXTENSION}')
            with open(full_path, 'w') as file:
                file.write(content)
                return True
        except FileNotFoundError:
            return False

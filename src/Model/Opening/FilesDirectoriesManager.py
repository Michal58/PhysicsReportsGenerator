import os


class FilesDirectoriesManager:
    def __init__(self):
        pass

    @staticmethod
    def create_non_existent_directories(settings: dict[str, str]) -> bool:
        # we return result of creation of all of these directories

        try:
            for directory_path in settings.values():
                if not (os.path.exists(directory_path) and os.path.isdir(directory_path)):
                    os.mkdir(directory_path)
            return True
        except (FileNotFoundError, NotADirectoryError, FileExistsError):
            return False

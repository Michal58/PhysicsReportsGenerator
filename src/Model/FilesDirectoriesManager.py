import os


class FilesDirectoriesManager:
    def __init__(self, settings: dict[str, str]):
        self.settings = settings

    def create_non_existent_directories(self) -> bool:
        # we return result of creation of all of these directories

        try:
            for directory_path in self.settings.values():
                if not (os.path.exists(directory_path) and os.path.isdir(directory_path)):
                    os.mkdir(directory_path)
            return True
        except (FileNotFoundError, NotADirectoryError, FileExistsError):
            return False

    def read_files_from_directory(self, file_type: str) -> list[str]:
        try:
            files: list[str] = [file for file in os.listdir(self.settings[file_type])
                                if not os.path.isdir(os.path.join(file, self.settings[file_type]))]
            return files
        except FileNotFoundError:
            return []

    def save_file_to_directory(self, file_type: str, file_name: str, content: str) -> bool:
        self.create_non_existent_directories()
        full_path = os.path.join(self.settings[file_type], file_name)
        try:
            with open(full_path, 'w') as file:
                file.write(content)
                return True
        except FileNotFoundError:
            return False

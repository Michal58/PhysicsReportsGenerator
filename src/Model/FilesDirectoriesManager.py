import os
import shutil

from settings_namespace import ENCODING


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
                                if not os.path.isdir(os.path.join(self.settings[file_type], file))]
            return files
        except FileNotFoundError:
            return []

    def save_file_to_directory(self, file_type: str, file_name: str, content: str) -> bool:
        self.create_non_existent_directories()
        full_path = os.path.join(self.settings[file_type], file_name)
        try:
            with open(full_path, 'w', encoding=ENCODING) as file:
                file.write(content)
                return True
        except FileNotFoundError:
            return False

    def copy_file_to_directory(self, file_path: str, file_type: str) -> bool:
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            return False
        try:
            base_name: str = os.path.basename(file_path)
            dest_path = os.path.join(self.settings[file_type], base_name)
            if base_name == dest_path:
                return False
            shutil.copyfile(file_path, dest_path)
            return True
        except FileNotFoundError:
            return False

    def copy_all_files_to_directory(self, source_file_type: str, dest_file_type: str) -> bool:
        try:
            all_source_files: list[str] = self.read_files_from_directory(source_file_type)
            for source_file in all_source_files:
                source_path: str=os.path.join(self.settings[source_file_type],source_file)
                dest_path = os.path.join(self.settings[dest_file_type], source_file)
                shutil.copyfile(source_path, dest_path)
            return True
        except FileNotFoundError as e:
            print(e)
            return False

    def remove_file(self, file_path: str) -> bool:
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            return False
        try:
            os.remove(file_path)
            return True
        except FileNotFoundError:
            return False

    def rename_file(self, file_path: str, new_path: str) -> bool:
        try:
            os.rename(file_path, new_path)
            return True
        except FileNotFoundError:
            return False


if __name__ == '__main__':
    local_settings = {dir_type: f'..\\..\\example\\{dir_type}' for dir_type in
                      ['baseFiles', 'sourceFiles', 'generatedFiles']}

    manager = FilesDirectoriesManager(local_settings)
    print(manager.copy_all_files_to_directory('sourceFiles','generatedFiles'))

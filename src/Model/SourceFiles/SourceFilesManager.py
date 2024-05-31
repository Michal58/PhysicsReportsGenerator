import re

from Model.FilesDirectoriesManager import FilesDirectoriesManager
from settings_namespace import SOURCE_FILES


class SourceFilesManager:
    # format of source file - {number}_{name of file}
    EXTENSION: str='tex'
    FILE_FORMAT: str = fr'^(\d+)_(\w+).{EXTENSION}$'
    BAD_FORMAT_NUMER: int = -1
    START_COUNT: int = 0

    def __init__(self, settings: dict[str, str]):
        self.settings = settings
        self.source_files_directory = settings[SOURCE_FILES]
        self.files_list: list[str] = []
        self.sorting_key: callable = lambda file: self.file_name_decomposer(file)[0]
        self.directories_manager = FilesDirectoriesManager(self.settings)

    def get_list_of_files(self) -> None:
        files_directories_manager = FilesDirectoriesManager(self.settings)
        self.files_list = files_directories_manager.read_files_from_directory(SOURCE_FILES)

    def file_name_decomposer(self, file_name: str) -> tuple[int, str]:
        match_result = re.match(SourceFilesManager.FILE_FORMAT, file_name)
        if match_result:
            return match_result.group(1), match_result.group(2)
        else:
            return SourceFilesManager.BAD_FORMAT_NUMER, file_name

    def return_ordered_files(self) -> list[str]:
        return sorted(self.files_list, key=self.sorting_key)

    def find_the_last_file(self) -> str | None:
        if len(self.files_list) > 0:
            last_file = max(self.files_list, key=self.sorting_key)
            return last_file
        else:
            return None

    def next_file_name(self, name_part: str):
        last_file = self.find_the_last_file()
        if last_file is None:
            return f'{SourceFilesManager.START_COUNT}_{name_part}.{SourceFilesManager.EXTENSION}'
        num, _ = self.file_name_decomposer(last_file)
        return f'{num + 1}_{name_part}.{SourceFilesManager.EXTENSION}'

    def save_source_file(self, file_name: str, content: str) -> bool:
        return self.directories_manager.save_file_to_directory(SOURCE_FILES, file_name, content)

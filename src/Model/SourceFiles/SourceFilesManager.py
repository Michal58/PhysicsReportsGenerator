import os.path
import re

from Model.FilesDirectoriesManager import FilesDirectoriesManager
from settings_namespace import SOURCE_FILES


class SourceFilesManager:
    # format of source file - {number}_{name of file}
    EXTENSION: str = 'tex'
    NAME_FORMAT: str = r'([\w ]+)'
    FILE_FORMAT: str = fr'^(\d+)_{NAME_FORMAT}\.{EXTENSION}$'
    BAD_FORMAT_NUMER: int = -1
    BAD_FILE_NAME: str = ''
    START_COUNT: int = 0

    def __init__(self, settings: dict[str, str]):
        self.settings = settings
        self.source_files_directory = settings[SOURCE_FILES]
        self.files_list: list[str] = []
        self.sorting_key: callable = lambda file: int(self.file_name_decomposer(file)[0])
        self.directories_manager = FilesDirectoriesManager(self.settings)

    def _get_list_of_files(self) -> None:
        files_directories_manager = FilesDirectoriesManager(self.settings)
        self.files_list = list(
            filter(lambda file_name: re.fullmatch(SourceFilesManager.FILE_FORMAT, file_name) is not None,
                   files_directories_manager.read_files_from_directory(SOURCE_FILES)))

    def get_list_of_files(self) -> None:
        self._get_list_of_files()
        self.renumber_source_files()

    def file_name_decomposer(self, file_name: str) -> tuple[int, str]:
        match_result = re.fullmatch(SourceFilesManager.FILE_FORMAT, file_name)
        if match_result:
            return match_result.group(1), match_result.group(2)
        else:
            return SourceFilesManager.BAD_FORMAT_NUMER, file_name

    def _return_ordered_files(self) -> list[str]:
        self._get_list_of_files()
        return sorted(self.files_list, key=self.sorting_key)

    def return_ordered_files(self) -> list[str]:
        self.get_list_of_files()
        return sorted(self.files_list, key=self.sorting_key)

    def find_the_last_file(self) -> str | None:
        self.get_list_of_files()
        if len(self.files_list) > 0:
            last_file = max(self.files_list, key=self.sorting_key)
            return last_file
        else:
            return None

    def get_filepath(self, base_name: str) -> str:
        return os.path.join(self.settings[SOURCE_FILES], base_name)

    def create_source_file_name(self, num: int, name_part: str) -> str:
        return f'{num}_{name_part}.{SourceFilesManager.EXTENSION}'

    def next_file_name(self, name_part: str) -> str:
        if re.fullmatch(SourceFilesManager.NAME_FORMAT, name_part) is None:
            return SourceFilesManager.BAD_FILE_NAME
        last_file = self.find_the_last_file()
        if last_file is None:
            return self.create_source_file_name(SourceFilesManager.START_COUNT, name_part)
        num, _ = self.file_name_decomposer(last_file)
        return self.create_source_file_name(int(num) + 1, name_part)

    def save_source_file(self, file_name: str, content: str) -> bool:
        return self.directories_manager.save_file_to_directory(SOURCE_FILES, file_name, content)

    def renumber_source_files(self) -> bool:
        self._get_list_of_files()
        files_directories_manager = FilesDirectoriesManager(self.settings)
        sorted_files: list[str] = self._return_ordered_files()
        for i in range(len(sorted_files)):
            num, name = self.file_name_decomposer(sorted_files[i])
            file_path: str = self.get_filepath(self.create_source_file_name(int(num), name))
            new_path: str = self.get_filepath(self.create_source_file_name(i + SourceFilesManager.START_COUNT, name))
            if file_path != new_path:
                if not files_directories_manager.rename_file(file_path, new_path):
                    return False
        self._get_list_of_files()
        return True

    def _has_file_number_checker(self, number: int) -> callable:
        def file_number_checker(filename: str) -> bool:
            num, _ = self.file_name_decomposer(filename)
            return int(num) == number

        return file_number_checker

    def _shift(self, list_obj: list, current_index: int, next_index: int) -> bool:
        if current_index == next_index or current_index < 0 or current_index >= len(list_obj):
            return False
        if next_index < 0 or next_index >= len(list_obj):
            return False

        i: int = current_index
        incr: int = 1 if current_index < next_index else -1
        aux = list_obj[i]

        while i != next_index:
            list_obj[i] = list_obj[i + incr]
            i += incr

        list_obj[i] = aux
        return True

    def _rename_as_ordered(self, source_files: list[str]) -> bool:
        files_directories_manager = FilesDirectoriesManager(self.settings)
        result: bool

        for i, source_file in enumerate(source_files):
            num, name = self.file_name_decomposer(source_file)
            if int(num) - SourceFilesManager.START_COUNT != i:
                old_path: str = self.get_filepath(source_file)
                new_path: str = self.get_filepath(
                    self.create_source_file_name(i + SourceFilesManager.START_COUNT, name))
                result = files_directories_manager.rename_file(old_path, new_path)
                if not result:
                    return False
        return True

    def change_position_of_file(self, current_position: int, next_position: int) -> bool:
        self.get_list_of_files()

        if not len(list(filter(self._has_file_number_checker(current_position), self.files_list))) == 1:
            return False

        sorted_files: list[str] = self._return_ordered_files()

        current_index: int = current_position - SourceFilesManager.START_COUNT
        next_index: int = next_position - SourceFilesManager.START_COUNT

        if not self._shift(sorted_files, current_index, next_index):
            return False

        return self._rename_as_ordered(sorted_files)


if __name__ == '__main__':
    local_settings = {dir_type: f'..\\..\\..\\example\\{dir_type}' for dir_type in
                      ['baseFiles', 'sourceFiles', 'generatedFiles']}
    manager=SourceFilesManager(local_settings)
    manager.change_position_of_file(4, 1)

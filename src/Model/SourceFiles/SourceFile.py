import os.path
import re
import shutil
from typing import AnyStr

from settings_namespace import ENCODING


class SourceFile:
    EXTENSION: str = 'tex'
    MARK_CAPTURE_PATTERN: str = r'\(\\w\+\)'
    FILE_INPUT_FORMAT: str = r'^\\input{(\w+)}|([^\\])\\input{(\w+)}'
    GROUP_OF_NAME_BEGINNING = 1
    GROUP_OF_PREVIOUS_CHARACTER = 2
    GROUP_OF_NAME_MIDDLE = 3

    def __init__(self, full_path: str):
        self.full_path: str = full_path

    @staticmethod
    def get_input_mark(input_command: str) -> str:
        # We assume that yet input command syntax is valid
        """
        Extract mark from whole command e.g: \\\\input{thisMark}->thisMark
        :param input_command:
        :return: mark of whole command structure
        """

        groups_match: re.Match[str] | None = re.match(SourceFile.FILE_INPUT_FORMAT, input_command)
        mark_beginning: AnyStr = groups_match.group(SourceFile.GROUP_OF_NAME_BEGINNING)
        mark_middle: AnyStr = groups_match.group(SourceFile.GROUP_OF_NAME_MIDDLE)

        if mark_beginning:
            return mark_beginning
        else:
            return mark_middle

    @staticmethod
    def create_input_command(mark: str) -> str:
        return fr'\input{{{mark}}}'

    def read_content_of_file(self) -> tuple[bool, str]:
        try:
            with open(self.full_path, 'r', encoding=ENCODING) as file:
                text_of_file: str = file.read()
                return True, text_of_file
        except FileNotFoundError:
            return False, ''

    def save_content_to_file(self, content: str) -> bool:
        try:
            with open(self.full_path, 'w', encoding=ENCODING) as file:
                file.write(content)
                return True
        except FileNotFoundError:
            return False

    def create_copy_to_another_directory(self, directory: str) -> tuple[bool, str]:
        try:
            save_path: str = os.path.join(directory, os.path.basename(self.filepath))
            shutil.copyfile(self.filepath, save_path)
            return True, save_path
        except FileNotFoundError:
            return False, ''

    def remove(self)->bool:
        try:
            os.remove(self.filepath)
            return True
        except FileNotFoundError:
            return False

    def rename(self, new_name:str)->bool:
        try:
            new_filepath:str=os.path.join(os.path.dirname(self.filepath), new_name)
            if os.path.exists(new_filepath):
                os.remove(new_filepath)
            os.rename(self.filepath,new_filepath)
            return True
        except FileNotFoundError:
            return False

    def get_all_marks(self) -> list[str]:
        """
        Get all marks in source file, which object represents
        :return: list[str] - ordered marks (as they were occurring in the file)
        """
        was_success, text_of_file = self.read_content_of_file()
        if not was_success:
            return []

        marks: list = []
        for matched_text in re.finditer(SourceFile.FILE_INPUT_FORMAT, text_of_file):
            if matched_text.group(SourceFile.GROUP_OF_NAME_BEGINNING) is not None:
                marks.append(matched_text.group(SourceFile.GROUP_OF_NAME_BEGINNING))
            else:
                marks.append(matched_text.group(SourceFile.GROUP_OF_NAME_MIDDLE))

        return list(dict.fromkeys(marks))

    def _replacement(self, input_filename: str, matched_text: re.Match) -> str:
        if matched_text.group(SourceFile.GROUP_OF_NAME_BEGINNING) is not None:
            return SourceFile.create_input_command(input_filename)
        else:
            return f'{matched_text.group(SourceFile.GROUP_OF_PREVIOUS_CHARACTER)}{SourceFile.create_input_command(input_filename)}'

    def _hard_replacement(self, content: str, matched_text: re.Match):
        if matched_text.group(SourceFile.GROUP_OF_NAME_BEGINNING) is not None:
            return content
        else:
            return f'{matched_text.group(SourceFile.GROUP_OF_PREVIOUS_CHARACTER)}{content}'

    def _refactor_filename(self, file_path: str) -> str:
        input_filename = os.path.basename(file_path)
        input_filename = re.sub(fr'\.{SourceFile.EXTENSION}$', '', input_filename)
        return input_filename

    def _replacement_conductor(self, replacer: callable, mark: str, content: str) -> bool:
        was_success, text_of_file = self.read_content_of_file()
        if not was_success:
            return False
        format_to_replace: str = re.sub(SourceFile.MARK_CAPTURE_PATTERN, f'({mark})', SourceFile.FILE_INPUT_FORMAT)
        text_of_file = re.sub(pattern=format_to_replace,
                              repl=lambda matched_text: replacer(content, matched_text),
                              string=text_of_file)
        self.save_content_to_file(text_of_file)
        return True

    def replace_input(self, mark: str, file_path: str) -> bool:
        input_filename = self._refactor_filename(file_path)
        return self._replacement_conductor(self._replacement, mark, input_filename)

    def hard_replace(self, mark: str, content: str) -> bool:
        return self._replacement_conductor(self._hard_replacement, mark, content)

    @property
    def filepath(self) -> str:
        return self.full_path

    def basename(self)->str:
        return os.path.basename(self.filepath)

    def __str__(self):
        return self.filepath

    def __repr__(self):
        return self.__str__()


def _replacement_conductor(text_of_file, replacer: callable, mark: str, content: str):
    format_to_replace: str = re.sub(SourceFile.MARK_CAPTURE_PATTERN, f'({mark})', SourceFile.FILE_INPUT_FORMAT)
    print(format_to_replace)
    text_of_file = re.sub(pattern=format_to_replace,
                          repl=lambda matched_text: replacer(content, matched_text),
                          string=text_of_file)
    return text_of_file


if __name__ == '__main__':
    local_settings = {dir_type: f'..\\..\\..\\example\\{dir_type}' for dir_type in
                      ['baseFiles', 'sourceFiles', 'generatedFiles']}

    source_file = SourceFile(f'..\\..\\..\\example\\sourceFiles\\6_check1.tex')

    source_file2 = SourceFile(f'..\\..\\..\\example\\sourceFiles\\7_check2.tex')
    source_file3 = SourceFile(f'..\\..\\..\\example\\sourceFiles\\8_check3.tex')

    print(source_file.get_all_marks())
    # source_file.replace_include('mark1',f'..\\..\\..\\example\\sourceFiles\\7_check2.tex')
    # source_file.replace_include('mark2',f'..\\..\\..\\example\\sourceFiles\\8_check3.tex')

    source_file.hard_replace('8_check3', source_file3.read_content_of_file()[1])

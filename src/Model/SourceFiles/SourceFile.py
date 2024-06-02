import os.path
import re
from typing import AnyStr

from settings_namespace import ENCODING


class SourceFile:
    EXTENSION: str = 'tex'
    MARK_CAPTURE_PATTERN: str = r'\(\\w\+\)'
    FILE_INCLUDE_FORMAT: str = r'^\\include{(\w+)}|([^\\])\\include{(\w+)}'
    GROUP_OF_NAME_BEGINNING = 1
    GROUP_OF_PREVIOUS_CHARACTER = 2
    GROUP_OF_NAME_MIDDLE = 3

    def __init__(self, full_path: str):
        self.full_path: str = full_path

    @staticmethod
    def get_include_mark(include_command: str) -> str:
        # We assume that yet include command syntax is valid
        """
        Extract mark from whole command e.g: \\\\include{thisMark}->thisMark
        :param include_command:
        :return: mark of whole command structure
        """

        groups_match: re.Match[str] | None = re.match(SourceFile.FILE_INCLUDE_FORMAT, include_command)
        mark_beginning: AnyStr = groups_match.group(SourceFile.GROUP_OF_NAME_BEGINNING)
        mark_middle: AnyStr = groups_match.group(SourceFile.GROUP_OF_NAME_MIDDLE)

        if mark_beginning:
            return mark_beginning
        else:
            return mark_middle

    @staticmethod
    def create_include_command(mark: str) -> str:
        return fr'\include{{{mark}}}'

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

    def get_all_marks(self) -> list[str]:
        was_success, text_of_file = self.read_content_of_file()
        if not was_success:
            return []

        marks: set = set()
        for matched_text in re.finditer(SourceFile.FILE_INCLUDE_FORMAT, text_of_file):
            if matched_text.group(SourceFile.GROUP_OF_NAME_BEGINNING) is not None:
                marks.add(matched_text.group(SourceFile.GROUP_OF_NAME_BEGINNING))
            else:
                marks.add(matched_text.group(SourceFile.GROUP_OF_NAME_MIDDLE))
        return list(marks)

    def _replacement(self, include_filename: str, matched_text: re.Match) -> str:
        if matched_text.group(SourceFile.GROUP_OF_NAME_BEGINNING) is not None:
            return SourceFile.create_include_command(include_filename)
        else:
            return f'{matched_text.group(SourceFile.GROUP_OF_PREVIOUS_CHARACTER)}{SourceFile.create_include_command(include_filename)}'

    def _hard_replacement(self, content: str, matched_text: re.Match):
        if matched_text.group(SourceFile.GROUP_OF_NAME_BEGINNING) is not None:
            return content
        else:
            return f'{matched_text.group(SourceFile.GROUP_OF_PREVIOUS_CHARACTER)}{content}'

    def _refactor_filename(self, file_path: str) -> str:
        include_filename = os.path.basename(file_path)
        include_filename = re.sub(fr'\.{SourceFile.EXTENSION}$', '', include_filename)
        return include_filename

    def _replacement_conductor(self, replacer: callable, mark: str, content: str) -> bool:
        was_success, text_of_file = self.read_content_of_file()
        if not was_success:
            return False
        format_to_replace: str = re.sub(SourceFile.MARK_CAPTURE_PATTERN, f'({mark})', SourceFile.FILE_INCLUDE_FORMAT)
        text_of_file = re.sub(pattern=format_to_replace,
                              repl=lambda matched_text: replacer(content, matched_text),
                              string=text_of_file)
        self.save_content_to_file(text_of_file)
        return True

    def replace_include(self, mark: str, file_path: str) -> bool:
        include_filename = self._refactor_filename(file_path)
        return self._replacement_conductor(self._replacement, mark, include_filename)

    def hard_replace(self, mark: str, content: str) -> bool:
        return self._replacement_conductor(self._hard_replacement, mark, content)


def _replacement_conductor(text_of_file, replacer: callable, mark: str, content: str):
    format_to_replace: str = re.sub(SourceFile.MARK_CAPTURE_PATTERN, f'({mark})', SourceFile.FILE_INCLUDE_FORMAT)
    print(format_to_replace)
    text_of_file = re.sub(pattern=format_to_replace,
                          repl=lambda matched_text: replacer(content, matched_text),
                          string=text_of_file)
    return text_of_file


if __name__ == '__main__':
    local_settings = {dir_type: f'..\\..\\..\\example\\{dir_type}' for dir_type in
                      ['baseFiles', 'sourceFiles', 'generatedFiles']}

    source_file=SourceFile(f'..\\..\\..\\example\\sourceFiles\\6_check1.tex')

    source_file2=SourceFile(f'..\\..\\..\\example\\sourceFiles\\7_check2.tex')
    source_file3=SourceFile(f'..\\..\\..\\example\\sourceFiles\\8_check3.tex')

    print(source_file.get_all_marks())
    # source_file.replace_include('mark1',f'..\\..\\..\\example\\sourceFiles\\7_check2.tex')
    # source_file.replace_include('mark2',f'..\\..\\..\\example\\sourceFiles\\8_check3.tex')

    source_file.hard_replace('8_check3',source_file3.read_content_of_file()[1])
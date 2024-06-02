import re
from typing import AnyStr


class SourceFile:
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

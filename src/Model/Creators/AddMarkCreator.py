import re
import sys

from PySide6.QtWidgets import QWidget, QDialog, QFileDialog, QApplication

from Model.Creators.Creator import Creator
from Model.Creators.CreatorListener import CreatorListener
from Model.SourceFiles.SourceFile import SourceFile
from settings_namespace import ENCODING, SOURCE_FILES


class AddMarkCreator(Creator):
    TITLE: str = "Add mark creator"
    BASE_MARK_NAME: str = 'mark'
    ASSUMED_MARK_FORMAT = r'[a-zA-Z]+([1-9]\d*)'

    def __init__(self, settings: dict[str, str], creator_listener: CreatorListener, parent_widget: QWidget):
        super().__init__(settings, creator_listener, parent_widget)
        self.file_to_add_mark: str = ''
        self.dialog_for_adding_include_mark: QFileDialog = QFileDialog(self.parent_widget)

    def get_title(self) -> str:
        return AddMarkCreator.TITLE

    def get_use_dialog(self) -> QDialog:
        return self.dialog_for_adding_include_mark

    def set_data(self) -> None:
        options = QFileDialog.Options()
        self.file_to_add_mark, _ = self.dialog_for_adding_include_mark.getOpenFileName(
            self.dialog_for_adding_include_mark.parent(), 'Add include mark', self.settings[SOURCE_FILES],
            "TeX Files (*.tex)", options=options)

    def validate_data(self) -> bool:
        return self.file_to_add_mark != ''

    def get_next_mark(self) -> str:
        source_file: SourceFile = SourceFile(self.file_to_add_mark)
        marks: list[str] = source_file.get_all_marks()
        extracted_numbers = [int(re.match(AddMarkCreator.ASSUMED_MARK_FORMAT, mark).group(1)) for mark in marks if
                             (re.match(AddMarkCreator.ASSUMED_MARK_FORMAT, mark) is not None)]
        if not extracted_numbers:
            return SourceFile.create_include_command(AddMarkCreator.BASE_MARK_NAME + '1')
        return SourceFile.create_include_command(AddMarkCreator.BASE_MARK_NAME + str(max(extracted_numbers) + 1))

    def perform_operations(self) -> bool:
        try:
            next_mark=self.get_next_mark()
            with open(self.file_to_add_mark, 'a', encoding=ENCODING) as file:
                file.write(f'\n{next_mark}')
                return True
        except FileNotFoundError:
            return False


if __name__ == '__main__':
    local_settings = {dir_type: f'..\\..\\..\\example\\{dir_type}' for dir_type in
                      ['baseFiles', 'sourceFiles', 'generatedFiles']}

    class Listener(CreatorListener):
        def notify_about_result_of_main_function(self, result: bool):
            print(result)


    app = QApplication(sys.argv)

    intro_vars = AddMarkCreator(local_settings, Listener(), None)
    intro_vars.perform_functionality()

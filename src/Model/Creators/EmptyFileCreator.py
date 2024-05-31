import os.path
import re
import sys

from PySide6.QtWidgets import QWidget, QDialog, QApplication, QGridLayout, QLabel, QLineEdit, QPushButton

from Model.Creators.Creator import Creator
from Model.Creators.CreatorListener import CreatorListener
from Model.SourceFiles.SourceFilesManager import SourceFilesManager
from settings_namespace import BASE_FILES, ENCODING


class FileCreatorDialog(QDialog):
    def __init__(self, parent_widget: QWidget):
        super().__init__(parent_widget)
        self.setWindowTitle('Document creator')
        layout = QGridLayout()

        self.title_label = QLabel('Title:')
        self.title_input = QLineEdit(self)
        layout.addWidget(self.title_label, 0, 0)
        layout.addWidget(self.title_input, 0, 1)

        self.extension_label = QLabel('Extension:')
        self.extension_input = QLineEdit(self)
        layout.addWidget(self.extension_label, 1, 0)
        layout.addWidget(self.extension_input, 1, 1)

        self.ok_button = QPushButton('OK', self)

        layout.addWidget(self.ok_button, 2, 0, 1, 2)

        self.setLayout(layout)
        self.ok_button.clicked.connect(self.accept)

    def get_user_input(self) -> tuple[str, str]:
        return self.title_input.text().strip(), self.extension_input.text().strip()


class EmptyFileCreator(Creator):
    TITLE: str = 'Create empty file'
    EXTENSION_FORMAT: str = r'[a-zA-Z0-9]+'

    def __init__(self, settings: dict[str, str], creator_listener: CreatorListener, parent_widget: QWidget) -> None:
        super().__init__(settings, creator_listener, parent_widget)
        self.file_extension: str = ''
        self.file_title: str = ''
        self.file_path: str = ''
        self.dialog: FileCreatorDialog = FileCreatorDialog(parent_widget)
        self.dialog_execution: int = QDialog.Rejected

    def set_info_about_empty_file(self, title: str, extension: str) -> None:
        self.file_title = title
        self.file_extension = extension
        self.file_path = os.path.join(self.settings[BASE_FILES], f'{title}.{extension}')

    def set_data(self) -> None:
        self.dialog_execution = self.dialog.exec()
        title, extension = self.dialog.get_user_input()
        self.set_info_about_empty_file(title, extension)

    def validate_new_file_name(self) -> bool:
        return re.fullmatch(EmptyFileCreator.EXTENSION_FORMAT, self.file_extension) is not None and re.fullmatch(
            SourceFilesManager.NAME_FORMAT, self.file_title) is not None

    def validate_data(self) -> bool:
        return self.dialog_execution == QDialog.Accepted and self.validate_new_file_name()

    def create_file(self) -> bool:
        try:
            with open(self.file_path, 'w', encoding=ENCODING):
                pass
            return True
        except (FileNotFoundError, IsADirectoryError):
            return False

    def perform_operations(self) -> bool:
        return self.create_file()

    def get_title(self) -> str:
        return EmptyFileCreator.TITLE

    def get_use_dialog(self) -> QDialog:
        return self.dialog


if __name__ == '__main__':
    local_settings = {dir_type: f'..\\..\\..\\example\\{dir_type}' for dir_type in
                      ['baseFiles', 'sourceFiles', 'generatedFiles']}


    class Listener(CreatorListener):
        def notify_about_result_of_main_function(self, result: bool):
            print(result)


    app = QApplication(sys.argv)
    add_creator = EmptyFileCreator(local_settings, Listener(), None)
    add_creator.perform_functionality()

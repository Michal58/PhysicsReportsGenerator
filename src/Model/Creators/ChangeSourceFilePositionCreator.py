import sys

from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QDialog, QGridLayout, QLabel, QLineEdit, QPushButton, QWidget, QApplication

from Model.Creators.Creator import Creator
from Model.Creators.CreatorListener import CreatorListener
from Model.SourceFiles.SourceFilesManager import SourceFilesManager


class ShiftPositionDialog(QDialog):
    def __init__(self, lower_bound: int, upper_bound: int) -> None:
        super().__init__()
        self.setWindowTitle('Source file shifter')
        self.layout = QGridLayout()

        self.current_position_label: QLabel = QLabel('Current position of file')
        self.current_position_input: QLineEdit = QLineEdit(self)
        self.current_position_input.setValidator(QIntValidator(lower_bound, upper_bound, self))
        self.layout.addWidget(self.current_position_label, 0, 0)
        self.layout.addWidget(self.current_position_input, 0, 1)

        self.next_position_label: QLabel = QLabel('Next position of file')
        self.next_position_input: QLineEdit = QLineEdit(self)
        self.next_position_input.setValidator(QIntValidator(lower_bound, upper_bound, self))
        self.layout.addWidget(self.next_position_label, 1, 0)
        self.layout.addWidget(self.next_position_input, 1, 1)

        self.ok_button = QPushButton('OK', self)

        self.layout.addWidget(self.ok_button, 2, 0, 1, 2)

        self.setLayout(self.layout)
        self.ok_button.clicked.connect(self.accept)

    def get_user_input(self) -> tuple[str, str]:
        return self.current_position_input.text(), self.next_position_input.text()


class ChangeSourceFilePositionCreator(Creator):
    TITLE: str = 'Change source file position'
    WRONG_POSITION: int=-1

    def __init__(self, settings: dict[str, str], creator_listener: CreatorListener, parent_widget: QWidget):
        super().__init__(settings, creator_listener, parent_widget)
        self.source_files_manager: SourceFilesManager = SourceFilesManager(settings)
        self.source_files_manager.get_list_of_files()
        self.current_position: int = ChangeSourceFilePositionCreator.WRONG_POSITION
        self.next_position: int = ChangeSourceFilePositionCreator.WRONG_POSITION
        self.dialog_execution = QDialog.Rejected
        self.dialog: ShiftPositionDialog = ShiftPositionDialog(SourceFilesManager.START_COUNT, len(self.source_files_manager.files_list) - 1 + SourceFilesManager.START_COUNT)

    def set_data(self) -> None:
        self.dialog_execution=self.dialog.exec()
        current_position, next_position = self.dialog.get_user_input()
        self.current_position=int(current_position) if current_position!='' else self.current_position
        self.next_position=int(next_position) if next_position!='' else self.next_position

    def validate_data(self) -> bool:
        return (self.dialog_execution == QDialog.Accepted
                and self.current_position!=ChangeSourceFilePositionCreator.WRONG_POSITION
                and self.next_position!=ChangeSourceFilePositionCreator.WRONG_POSITION)

    def perform_operations(self) -> bool:
        return self.source_files_manager.change_position_of_file(self.current_position, self.next_position)

    def get_title(self) -> str:
        return ChangeSourceFilePositionCreator.TITLE

    def get_use_dialog(self) -> QDialog:
        return self.dialog


if __name__ == '__main__':
    local_settings = {dir_type: f'..\\..\\..\\example\\{dir_type}' for dir_type in
                      ['baseFiles', 'sourceFiles', 'generatedFiles']}


    class Listener(CreatorListener):
        def notify_about_result_of_main_function(self, result: bool):
            print(result)


    app = QApplication(sys.argv)
    change_position_creator = ChangeSourceFilePositionCreator(local_settings, Listener(), None)

    change_position_creator.perform_functionality()

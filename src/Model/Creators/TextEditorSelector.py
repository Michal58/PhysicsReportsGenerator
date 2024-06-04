from PySide6.QtWidgets import QDialog, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton

from Model.Creators.Creator import Creator
from Model.Creators.CreatorListener import CreatorListener
from Model.Variables.VariablesConsumer import VariablesConsumer
from Model.Variables.variables_namespace import TEXT_EDITOR_VARIABLE


class TextEditorCommandDialog(QDialog):
    def __init__(self, parent_widget: QWidget):
        super().__init__(parent_widget)
        self.setWindowTitle(TextEditorSelector.TITLE)
        layout = QGridLayout()

        self.title_label = QLabel('Code editor command:')
        self.text_editor_command_input = QLineEdit(self)
        layout.addWidget(self.title_label, 0, 0)
        layout.addWidget(self.text_editor_command_input, 0, 1)

        self.ok_button = QPushButton('OK', self)
        layout.addWidget(self.ok_button, 4, 0, 1, 2)

        self.setLayout(layout)
        self.ok_button.clicked.connect(self.accept)

    def get_user_input(self) -> str:
        return self.text_editor_command_input.text().strip()


class TextEditorSelector(Creator, VariablesConsumer):
    TITLE: str = 'Text editor selector'

    def __init__(self, settings: dict[str, str], creator_listener: CreatorListener, parent_widget: QWidget):
        super().__init__(settings, creator_listener, parent_widget)
        self.getting_result:int = QDialog.Rejected
        self.text_editor_command:str = ''
        self.dialog:TextEditorCommandDialog=TextEditorCommandDialog(parent_widget)

    def get_title(self) -> str:
        return TextEditorSelector.TITLE

    def get_use_dialog(self) -> QDialog:
        return self.dialog

    def set_data(self) -> None:
        self.getting_result=self.dialog.exec()
        self.text_editor_command=self.dialog.get_user_input()

    def validate_data(self) -> bool:
        return self.getting_result==QDialog.Accepted

    def perform_operations(self) -> bool:
        self.variables[TEXT_EDITOR_VARIABLE]=self.text_editor_command
        return True

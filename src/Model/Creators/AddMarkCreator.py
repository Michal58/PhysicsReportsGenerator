from PySide6.QtWidgets import QWidget, QDialog

from Controller.MainController import MainController
from Model.Creators.Creator import Creator
from Model.Creators.CreatorListener import CreatorListener
from Model.Variables.VariablesConsumer import VariablesConsumer
from settings_namespace import ENCODING


class AddMarkCreator(Creator, VariablesConsumer):
    TITLE: str = "Add mark creator"
    BASE_MARK_NAME: str='MARK'

    def __init__(self, settings: dict[str, str], creator_listener: CreatorListener, parent_widget: QWidget):
        super().__init__(settings, creator_listener, parent_widget)
        self.file_to_add_mark: str = ''
        self.empty_dialog = QDialog()

    def get_title(self) -> str:
        return AddMarkCreator.TITLE

    def get_use_dialog(self) -> QDialog:
        return self.empty_dialog

    def set_data(self) -> None:
        self.file_to_add_mark = self.variables[MainController.SELECTED_ITEMS_VARIABLE_NAME]

    def validate_data(self) -> bool:
        return self.file_to_add_mark != ''

    def get_next_mark(self)->str:

    def perform_operations(self) -> bool:
        try:
            with open(self.file_to_add_mark,'a',encoding=ENCODING) as file:
                file.write(f'\n{self.get_next_mark()}')
                return True
        except FileNotFoundError:
            return False


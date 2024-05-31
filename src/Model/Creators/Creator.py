import abc

from PySide6.QtWidgets import QWidget, QDialog

from Model.Creators.CreatorListener import CreatorListener


class Creator:
    def __init__(self, settings: dict[str, str], creator_listener: CreatorListener, paren_widget: QWidget):
        self.settings=settings
        self.creator_listener = creator_listener
        self.parent_widget=paren_widget

    @abc.abstractmethod
    def get_title(self) -> str:
        pass

    @abc.abstractmethod
    def get_use_dialog(self) -> QDialog:
        pass

    @abc.abstractmethod
    def set_data(self)->None:
        pass

    @abc.abstractmethod
    def validate_data(self) -> bool:
        pass

    @abc.abstractmethod
    def perform_operations(self) -> bool:
        pass

    def perform_functionality(self) -> None:
        self.set_data()
        if not self.validate_data():
            self.creator_listener.notify_about_result_of_main_function(False)
            return
        result: bool = self.perform_operations()
        self.creator_listener.notify_about_result_of_main_function(result)

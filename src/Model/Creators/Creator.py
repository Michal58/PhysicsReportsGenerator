import abc
from typing import Any

from PySide6.QtWidgets import QWidget, QDialog

from Model.Creators.CreatorListener import CreatorListener


class Creator:
    def __init__(self, settings: dict[str, str], creator_listener: CreatorListener, parent_widget: QWidget):
        self.settings: dict[str, str] = settings
        self.creator_listener: CreatorListener = creator_listener
        self.parent_widget: QWidget = parent_widget

    @abc.abstractmethod
    def get_title(self) -> str:
        """
        :return: Name of creator for UI
        """
        pass

    @abc.abstractmethod
    def get_use_dialog(self) -> QDialog:
        """
        Method allows to get dedicated dialog for use of creator
        :return: QDialog
        """
        pass

    @abc.abstractmethod
    def set_data(self) -> None:
        """
        Order for creator to assign appropriate values of user to variables
        """
        pass

    @abc.abstractmethod
    def validate_data(self) -> bool:
        """
        Check if user input was valid. Method validates if user entry was
        initially correct. Checking correctness of deeper mechanisms IS NOT
        purpose of this method.
        :return:bool
        """
        pass

    @abc.abstractmethod
    def perform_operations(self) -> bool:
        """
        Execute main functionality of creator
        :return: bool - was operation successful
        """
        pass

    def perform_functionality(self) -> None:
        """
        General template for performing next steps needed to do actual task
        """
        self.set_data()
        if not self.validate_data():
            self.creator_listener.notify_about_result_of_main_function(False)
            return
        result: bool = self.perform_operations()
        self.creator_listener.notify_about_result_of_main_function(result)

from typing import Any
import os
import sys

from PySide6.QtCore import QFileInfo
from PySide6.QtWidgets import QApplication

from src.Model.Opening.ProjectCreator import ProjectCreator
from src.Model.Opening.ProjectOpener import ProjectOpener
from src.UI.MainWindow import MainWindow
from src.UI.OpeningWindow import OpeningWindow


class MainController:
    SELECT_DIR_CAPTION: str='Select dir'

    def __init__(self):
        self.selected_directory: str = ''
        self.application: QApplication = QApplication(sys.argv)
        self.opening_window: OpeningWindow = OpeningWindow()
        self.main_window: MainWindow = MainWindow()
        self.settings: dict[str, str] = {}
        self.variables: dict[str, Any] = {}

    def connect_components_with_actions(self) -> None:
        self.opening_window.create_button.clicked.connect(self.select_workspace_by_create)
        self.opening_window.open_button.clicked.connect(self.select_workspace_by_open)

    def select_opening_directory(self) -> str:
        return self.opening_window.directory_dialog.getExistingDirectory(parent=self.opening_window,
                                                                         caption=MainController.SELECT_DIR_CAPTION,
                                                                         dir=QFileInfo(os.getcwd()).absolutePath())

    def select_workspace_by_open(self) -> None:
        self.selected_directory: str = self.select_opening_directory()
        opener: ProjectOpener = ProjectOpener(self.selected_directory)
        was_open_successful: bool = opener.open_project()
        if was_open_successful:
            self.settings = opener.get_settings()
            self.variables = opener.get_variables()
            self.opening_window.close()
        else:
            self.opening_window.communicate_operation_failure()

    def select_workspace_by_create(self) -> None:
        self.selected_directory: str = self.select_opening_directory()
        selected_directory: str = os.path.normpath(self.selected_directory)
        creator: ProjectCreator = ProjectCreator(selected_directory)
        was_open_successful: bool = creator.create()
        if was_open_successful:
            self.settings = creator.get_settings()
            self.opening_window.close()
        else:
            self.opening_window.communicate_operation_failure()

    def fill_panels(self)->None:
        pass

    def run(self) -> None:
        self.connect_components_with_actions()
        self.opening_window.exec()
        if self.settings == {}:
            exit(0)
        else:
            self.fill_panels()
            self.main_window.show()
            exit(self.application.exec())


def main_function():
    controller = MainController()
    controller.run()


if __name__ == '__main__':
    main_function()

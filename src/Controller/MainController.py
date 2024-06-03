import importlib
import pkgutil
from types import ModuleType
from typing import Any
import os
import sys

from PySide6.QtCore import QFileInfo
from PySide6.QtWidgets import QApplication, QMessageBox, QVBoxLayout
from pylatex import Document, NoEscape

import Model
from Controller.Wrappers import CreatorWrapper, FilepathWrapper
from Model.Creators.AddTexCreator import AddTexCreator
from Model.Creators.Creator import Creator
from Model.Creators.CreatorListener import CreatorListener
from Model.Creators.EmptyFileCreator import EmptyFileCreator
from Model.Creators.RemFileCreator import RemFileCreator
from Model.FilesDirectoriesManager import FilesDirectoriesManager
from Model.SourceFiles.SourceFile import SourceFile
from Model.SourceFiles.SourceFilesLinker import SourceFilesLinker
from Model.SourceFiles.SourceFilesManager import SourceFilesManager
from Model.Variables.VariablesConsumer import VariablesConsumer
from Model.Variables.VariablesFileOperator import VariablesFileOperator
from settings_namespace import BASE_FILES, SOURCE_FILES, GENERATED_FILES, ENCODING
from src.Model.Opening.ProjectCreator import ProjectCreator
from src.Model.Opening.ProjectOpener import ProjectOpener
from src.UI.MainWindow import MainWindow
from src.UI.OpeningWindow import OpeningWindow


class MainController(CreatorListener):
    SELECT_DIR_CAPTION: str = 'Select dir'
    # name of variable for interactions with variables consumers
    SELECTED_ITEMS_VARIABLE_NAME: str = '__selected_items__'

    def __init__(self):
        super().__init__()
        self.selected_directory: str = ''
        self.application: QApplication = QApplication(sys.argv)
        self.opening_window: OpeningWindow = OpeningWindow()
        self.main_window: MainWindow = MainWindow()
        self.settings: dict[str, str] = {}
        self.variables: dict[str, Any] = {}

        self.directories_manager: FilesDirectoriesManager | None = None
        self.source_files_manager: SourceFilesManager | None = None

        self.creators: list[Creator] = []
        self.base_files_list: list[str] = []
        self.source_files_list: list[str] = []

    def connect_components_with_actions(self) -> None:
        self.opening_window.create_button.clicked.connect(self.select_workspace_by_create)
        self.opening_window.open_button.clicked.connect(self.select_workspace_by_open)

        self.main_window.use_creator_button.clicked.connect(self.use_creator)

        self.main_window.base_files_panel.files_operations_section.add_button.clicked.connect(self.add_base_file)
        self.main_window.source_files_panel.files_operations_section.add_button.clicked.connect(self.add_source_file)

        self.main_window.base_files_panel.files_operations_section.rem_button.clicked.connect(
            self.remove_selected_file(BASE_FILES))
        self.main_window.source_files_panel.files_operations_section.rem_button.clicked.connect(
            self.remove_selected_file(SOURCE_FILES))

        self.main_window.generate_report_button.clicked.connect(self.generate_pdf)

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

    def throw_failure_of_operation(self, additional_text: str = '') -> None:
        msg = self.main_window.create_failure_message_box(additional_text)
        msg.exec()

    def notify_about_result_of_main_function(self, result: bool):
        if not result:
            self.throw_failure_of_operation()

    def use_creator(self) -> None:
        selected_creator: Creator = self.main_window.selected_creator
        if selected_creator is None:
            self.throw_failure_of_operation()
            return
        if isinstance(selected_creator, VariablesConsumer):
            selected_creator.set_variables(self.variables)
        selected_creator.perform_functionality()
        self.fill_panels()

    def add_base_file(self):
        empty_file_creator: EmptyFileCreator = EmptyFileCreator(self.settings, self, self.main_window)
        empty_file_creator.perform_functionality()
        self.fill_panels()

    def add_source_file(self):
        add_tex_creator: AddTexCreator = AddTexCreator(self.settings, self, self.main_window)
        add_tex_creator.perform_functionality()
        self.fill_panels()

    def remove_selected_file(self, file_type: str) -> callable:
        def remove_selected_file_closure():
            rem_filepath: str | None = self.main_window.selected_base_file if file_type == BASE_FILES else self.main_window.selected_source_file
            if rem_filepath is None:
                self.throw_failure_of_operation()
                return
            self.directories_manager.remove_file(rem_filepath)
            self.fill_panels()

        return remove_selected_file_closure

    def _generate_pdf(self, source_filepath: str) -> None:
        try:
            base_source: SourceFile = SourceFile(source_filepath)
            latex_base: str = base_source.filepath
            tex: str
            with open(latex_base, 'r', encoding=ENCODING) as file:
                tex = file.read()
            doc = Document()
            doc.append(NoEscape(tex))
            doc.generate_pdf(os.path.join(self.settings[GENERATED_FILES], base_source.basename()), clean=True,
                             clean_tex=True)
            self.fill_panels()
        except Exception as e:
            self.throw_failure_of_operation(e.__str__())

    def generate_pdf(self) -> None:
        if self.source_files_manager.are_source_files_empty():
            self.throw_failure_of_operation()
            return
        linker: SourceFilesLinker = SourceFilesLinker(self.settings)
        linker.soft_link()
        base_source: SourceFile = SourceFile(self.source_files_manager.get_first_file())
        self._generate_pdf(base_source.filepath)

    def generate_tex_and_pdf(self) -> None:
        if self.source_files_manager.are_source_files_empty():
            self.throw_failure_of_operation()
            return
        linker: SourceFilesLinker = SourceFilesLinker(self.settings)
        linker.hard_link()
        self._generate_pdf(linker.get_output_path_of_hard_link())

    def fill_creators_list(self) -> None:
        CHANGED_PROJECT_INFO: str = 'Changed project'
        self.creators = []
        for loader, module_absolute_math, is_pkg in pkgutil.walk_packages(Model.Creators.__path__,
                                                                          Model.Creators.__name__ + '.'):
            if not is_pkg:
                split_sign: str = '.'
                module: ModuleType = importlib.import_module(module_absolute_math)
                short_module_name: str = module_absolute_math.split(split_sign)[-1]
                if (short_module_name != Creator.__name__.split(split_sign)[-1]
                        and short_module_name != '__init__'
                        and short_module_name != CreatorListener.__name__.split(split_sign)[-1]):
                    if hasattr(module, short_module_name):
                        creator: Creator = getattr(module, short_module_name)(self.settings, self, self.main_window)
                        self.creators.append(creator)
                    else:
                        raise Exception(CHANGED_PROJECT_INFO)

    def fill_source_files_list(self):
        self.source_files_list = list(map(lambda file: os.path.join(self.settings[SOURCE_FILES], file),
                                          self.source_files_manager.return_ordered_files()))

    def fill_base_files_list(self):
        self.base_files_list = list(map(lambda file: os.path.join(self.settings[BASE_FILES], file),
                                        self.directories_manager.read_files_from_directory(BASE_FILES)))

    def refresh_lists(self):
        self.fill_creators_list()
        self.fill_base_files_list()
        self.fill_source_files_list()

    def fill_panels(self) -> None:
        self.refresh_lists()
        self.main_window.update_panels([CreatorWrapper(creator) for creator in self.creators],
                                       [FilepathWrapper(base_file) for base_file in self.base_files_list],
                                       [FilepathWrapper(source_file) for source_file in self.source_files_list])

    def run(self) -> None:
        self.connect_components_with_actions()
        self.opening_window.exec()
        if self.settings == {}:
            exit(0)
        else:
            self.directories_manager = FilesDirectoriesManager(self.settings)
            self.source_files_manager = SourceFilesManager(self.settings)

            self.fill_panels()
            self.main_window.show()
            self.application.exec()
            variables_operator = VariablesFileOperator(self.selected_directory)
            variables_operator.save_variables(self.variables)
            exit(0)


def main_function():
    controller = MainController()
    controller.run()


if __name__ == '__main__':
    main_function()

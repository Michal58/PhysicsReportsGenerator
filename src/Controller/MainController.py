import importlib
import pkgutil
import re
import subprocess
from types import ModuleType
from typing import Any
import os
import sys

from PySide6.QtCore import QFileInfo
from PySide6.QtWidgets import QApplication
from pylatex import Document, NoEscape

import Model
from Controller.Wrappers import CreatorWrapper, FilepathWrapper
from Model.Creators.AddTexCreator import AddTexCreator
from Model.Creators.Creator import Creator
from Model.Creators.CreatorListener import CreatorListener
from Model.Creators.EmptyFileCreator import EmptyFileCreator
from Model.Creators.TextEditorSelector import TextEditorSelector
from Model.FilesDirectoriesManager import FilesDirectoriesManager
from Model.SourceFiles.SourceFile import SourceFile
from Model.SourceFiles.SourceFilesLinker import SourceFilesLinker
from Model.SourceFiles.SourceFilesManager import SourceFilesManager
from Model.Variables.VariablesConsumer import VariablesConsumer
from Model.Variables.VariablesFileOperator import VariablesFileOperator
from Model.Variables.variables_namespace import TEXT_EDITOR_VARIABLE
from documentation_getter import get_documentation_text
from settings_namespace import BASE_FILES, SOURCE_FILES, GENERATED_FILES, ENCODING
from src.Model.Opening.ProjectCreator import ProjectCreator
from src.Model.Opening.ProjectOpener import ProjectOpener
from src.UI.MainWindow import MainWindow
from src.UI.OpeningWindow import OpeningWindow


class MainController(CreatorListener):
    SELECT_DIR_CAPTION: str = 'Select dir'
    LINKING_ERROR_MESSAGE: str = 'Linking error'

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

        self.main_window.creators_panel.filter_input.textChanged.connect(self.filter_creators_list)
        self.main_window.creators_panel.regex_checkbox.clicked.connect(self.filter_creators_list)

        self.main_window.generate_report_button.clicked.connect(self.generate_tex_and_pdf)

        self.main_window.close_menu.aboutToShow.connect(lambda: QApplication.instance().quit())
        self.main_window.help_menu.aboutToShow.connect(self.exec_help_dialog)
        self.main_window.variables_menu.aboutToShow.connect(self.exec_variable_display)

        self.main_window.link_marks.triggered.connect(self.generate_soft_links)
        self.main_window.generate_tex.triggered.connect(self.prepare_tex)
        self.main_window.generate_tex_and_pdf.triggered.connect(self.generate_tex_and_pdf)

        self.main_window.creators_panel.list_widget.doubleClicked.connect(self.use_creator)
        self.main_window.base_files_panel.list_widget.doubleClicked.connect(lambda: self.open_file_in_text_editor(self.main_window.selected_base_file))
        self.main_window.source_files_panel.list_widget.doubleClicked.connect(lambda: self.open_file_in_text_editor(self.main_window.selected_source_file))

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
            if TEXT_EDITOR_VARIABLE not in self.variables:
                self.variables[TEXT_EDITOR_VARIABLE]=''
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
            self.variables[TEXT_EDITOR_VARIABLE]=''
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

    def filter_creators_list(self) -> None:
        filter_text = self.main_window.creators_panel.filter_input.text()
        should_be_regex: bool = self.main_window.creators_panel.regex_checkbox.isChecked()

        if should_be_regex:
            try:
                re.compile(filter_text)
            except re.error:
                filter_text = ''
                should_be_regex = False

        for index in range(self.main_window.creators_panel.list_widget.count()):
            item = self.main_window.creators_panel.list_widget.item(index)
            item.setHidden(filter_text not in item.text()
                           if not should_be_regex or filter_text == ''
                           else re.match(filter_text, item.text()) is None)

    def generate_pdf(self, source_file: SourceFile) -> None:
        try:
            latex_base: str = source_file.filepath
            tex: str
            with open(latex_base, 'r', encoding=ENCODING) as file:
                tex = file.read()
            # doc = Document()
            # doc.append(NoEscape(tex))
            # doc.generate_pdf(os.path.join(self.settings[GENERATED_FILES], source_file.basename()), clean=True,
            #                  clean_tex=True)
            subprocess.Popen(['pdflatex', f'{source_file}', f'{os.path.join(self.settings[GENERATED_FILES], source_file.basename())}'])
            os.system(f'pdflatex {source_file}'+f'{os.path.join(self.settings[GENERATED_FILES], source_file.basename())}')
            self.fill_panels()
        except Exception as e:
            self.throw_failure_of_operation(e.__str__())

    def generate_soft_links(self) -> None:
        self.prepare_tex(True)

    def prepare_tex(self, soft_link: bool = False) -> str:
        linker: SourceFilesLinker = SourceFilesLinker(self.settings)
        method: callable = linker.hard_link if not soft_link else linker.soft_link
        _, mechanically_conducted_linking = method()
        if not mechanically_conducted_linking:
            self.throw_failure_of_operation(MainController.LINKING_ERROR_MESSAGE)
            return ''
        if soft_link:
            return ''
        return linker.get_output_path_of_hard_link()

    def generate_tex_and_pdf(self) -> None:
        generated_tex_file: str = self.prepare_tex()
        if generated_tex_file == '':
            return
        self.generate_pdf(SourceFile(generated_tex_file))

    def _get_help_text(self) -> str:
        try:
            return get_documentation_text()
        except FileNotFoundError:
            return ''

    def exec_help_dialog(self):
        self.main_window.get_help_window(self._get_help_text()).exec()

    def exec_variable_display(self):
        self.main_window.get_variables_display(self.variables).exec()

    def open_file_in_text_editor(self,filepath:str):
        if self.variables[TEXT_EDITOR_VARIABLE] == '':
            selector: TextEditorSelector=TextEditorSelector(self.settings, self, self.main_window)
            selector.set_variables(self.variables)
            selector.perform_functionality()
        try:
            command=self.variables[TEXT_EDITOR_VARIABLE]
            os.system(f'{command} "{filepath}"')
        except subprocess.CalledProcessError:
            self.throw_failure_of_operation()

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

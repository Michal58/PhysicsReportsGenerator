import os.path
import re
import shutil
import sys

from PySide6.QtWidgets import QFileDialog, QWidget, QDialog, QApplication

from Model.Creators.Creator import Creator
from Model.Creators.CreatorListener import CreatorListener
from Model.SourceFiles.SourceFilesManager import SourceFilesManager
from settings_namespace import SOURCE_FILES, BASE_FILES


class AddTexCreator(Creator):
    TITLE: str = 'Add .tex file'
    TEX_EXTENSION: str='tex'
    TEX_FILE_FORMAT = fr'.+\.{TEX_EXTENSION}'

    def __init__(self, settings: dict[str, str], creator_listener: CreatorListener, parent_widget: QWidget) -> None:
        super().__init__(settings, creator_listener, parent_widget)
        self.pathfile_to_add: str = ''
        self.new_file_name: str = ''
        self.new_source_file_path: str = ''
        self.source_files_manager: SourceFilesManager = SourceFilesManager(settings)
        self.file_dialog: QFileDialog = QFileDialog(parent_widget)

    def set_info_about_chosen_file(self, file_path: str) -> None:
        self.pathfile_to_add: str = file_path
        self.new_file_name: str = self.source_files_manager.next_file_name(os.path.basename(file_path).rstrip(f'.{AddTexCreator.TEX_EXTENSION}'))
        self.new_source_file_path: str = os.path.join(self.settings[SOURCE_FILES], self.new_file_name)

    def set_data(self) -> None:
        options = QFileDialog.Options()
        file_path, _ = self.file_dialog.getOpenFileName(self.file_dialog.parent(), "Select .tex",
                                                        self.settings[BASE_FILES], "TeX Files (*.tex)", options=options)

        self.set_info_about_chosen_file(file_path)

    def validate_chosen_file(self) -> bool:
        return self.new_file_name != '' and re.fullmatch(AddTexCreator.TEX_FILE_FORMAT, os.path.basename(self.pathfile_to_add)) is not None and self.new_source_file_path != self.pathfile_to_add

    def validate_data(self) -> bool:
        return self.validate_chosen_file()

    def add_tex_file(self) -> bool:
        if not self.validate_chosen_file():
            return False
        try:
            shutil.copyfile(self.pathfile_to_add, self.new_source_file_path)
            return True
        except (FileNotFoundError, IsADirectoryError):
            return False

    def perform_operations(self) -> bool:
        return self.add_tex_file()

    def get_title(self) -> str:
        return AddTexCreator.TITLE

    def get_use_dialog(self) -> QDialog:
        return self.file_dialog


if __name__ == '__main__':
    local_settings = {dir_type: f'..\\..\\..\\example\\{dir_type}' for dir_type in
                      ['baseFiles', 'sourceFiles', 'generatedFiles']}


    class Listener(CreatorListener):
        def notify_about_result_of_main_function(self, result: bool):
            print(result)


    app = QApplication(sys.argv)
    add_creator = AddTexCreator(local_settings, Listener(), None)
    add_creator.perform_functionality()

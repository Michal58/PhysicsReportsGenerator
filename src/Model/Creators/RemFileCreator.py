import os.path
import sys

from PySide6.QtWidgets import QWidget, QFileDialog, QDialog, QApplication

from Model.Creators.Creator import Creator
from Model.Creators.CreatorListener import CreatorListener
from Model.FilesDirectoriesManager import FilesDirectoriesManager
from settings_namespace import SOURCE_FILES


class RemFileCreator(Creator):
    TITLE: str = 'File remover'

    def __init__(self, settings: dict[str, str], creator_listener: CreatorListener, parent_widget: QWidget):
        super().__init__(settings, creator_listener, parent_widget)
        self.pathfile_to_rem: str = ''
        self.rem_dialog: QFileDialog = QFileDialog(parent_widget)
        self.default_directory: str = settings[SOURCE_FILES]
        self.files_directories_manager=FilesDirectoriesManager(self.settings)

    def get_title(self) -> str:
        return RemFileCreator.TITLE

    def set_info_about_chosen_file(self, file_path: str) -> None:
        self.pathfile_to_rem: str = file_path

    def set_data(self) -> None:
        options = QFileDialog.Options()
        file_path, _ = self.rem_dialog.getOpenFileName(self.rem_dialog.parent(), "Remove file", self.default_directory,
                                                       "Any File (*.*)", options=options)

        self.set_info_about_chosen_file(file_path)

    def validate_chosen_file(self) -> bool:
        return self.pathfile_to_rem != '' and not os.path.isdir(self.pathfile_to_rem)

    def validate_data(self) -> bool:
        return self.validate_chosen_file()

    def set_default_directory(self, directory: str) -> None:
        self.default_directory = directory

    def perform_operations(self) -> bool:
        return self.files_directories_manager.remove_file(self.pathfile_to_rem)

    def get_use_dialog(self) -> QDialog:
        return self.rem_dialog


if __name__ == '__main__':
    local_settings = {dir_type: f'..\\..\\..\\example\\{dir_type}' for dir_type in
                      ['baseFiles', 'sourceFiles', 'generatedFiles']}


    class Listener(CreatorListener):
        def notify_about_result_of_main_function(self, result: bool):
            print(result)


    app = QApplication(sys.argv)
    add_creator = RemFileCreator(local_settings, Listener(), None)
    add_creator.perform_functionality()

import os.path
import shutil

from PySide6.QtWidgets import QWidget, QDialog

from Model.Creators.Creator import Creator
from Model.Creators.CreatorListener import CreatorListener
from settings_namespace import BASE_FILES


class TransformerLibraryCreator(Creator):
    TITLE: str = 'Creator of transform library'

    def __init__(self, settings: dict[str, str], creator_listener: CreatorListener, parent_widget: QWidget):
        super().__init__(settings, creator_listener, parent_widget)

    def get_title(self) -> str:
        return TransformerLibraryCreator.TITLE

    def get_use_dialog(self) -> QDialog:
        raise NotImplementedError

    def set_data(self) -> None:
        pass

    def validate_data(self) -> bool:
        return True

    def perform_operations(self) -> bool:
        from Model import TableTransformer
        transformer_filepath: str = TableTransformer.__file__
        try:
            shutil.copyfile(transformer_filepath, os.path.join(self.settings[BASE_FILES], os.path.basename(transformer_filepath)))
            return True
        except FileNotFoundError:
            return False

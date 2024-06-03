import os

from PySide6.QtWidgets import QListWidgetItem

from Model.Creators.Creator import Creator


class FilepathWrapper(QListWidgetItem):
    def __init__(self, filepath: str):
        super().__init__(os.path.basename(filepath))
        self.filepath = filepath

    def __repr__(self):
        return os.path.basename(self.filepath)


class CreatorWrapper(QListWidgetItem):
    def __init__(self, creator: Creator):
        super().__init__(creator.get_title())
        self.creator = creator

    def __repr__(self):
        self.creator.get_title()

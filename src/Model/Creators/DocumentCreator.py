import sys
from datetime import datetime

from PySide6.QtWidgets import QWidget, QDialog, QGridLayout, QLabel, QLineEdit, QPushButton, QApplication
from pylatex import NoEscape, Command

from Model.Creators.Creator import Creator
from Model.Creators.CreatorListener import CreatorListener
from Model.SourceFiles.SourceFile import SourceFile
from Model.SourceFiles.SourceFilesManager import SourceFilesManager


class TitleCreatorDialog(QDialog):
    def __init__(self, parent_widget: QWidget):
        super().__init__(parent_widget)
        self.setWindowTitle('Document creator')
        layout = QGridLayout()

        self.title_label = QLabel('Title:')
        self.title_input = QLineEdit(self)
        layout.addWidget(self.title_label, 0, 0)
        layout.addWidget(self.title_input, 0, 1)

        self.author_label = QLabel('Author:')
        self.author_input = QLineEdit(self)
        layout.addWidget(self.author_label, 1, 0)
        layout.addWidget(self.author_input, 1, 1)

        self.ok_button = QPushButton('OK', self)

        layout.addWidget(self.ok_button, 2, 0, 1, 2)

        self.setLayout(layout)
        self.ok_button.clicked.connect(self.accept)

    def get_user_input(self):
        return self.title_input.text().strip(), self.author_input.text().strip()


class DocumentCreator(Creator):
    TITLE: str = "Document creator"
    BODY_MARK: str = "Body"

    def __init__(self, settings: dict[str, str], creator_listener: CreatorListener):
        self.dialog: TitleCreatorDialog
        self.creator_listener: CreatorListener = creator_listener
        self.file_name: str = ''
        self.author: str = ''
        self.title: str = ''
        self.settings = settings
        self.source_files_manger = SourceFilesManager(self.settings)

    def get_title(self) -> str:
        return DocumentCreator.TITLE

    def set_info_for_document(self, title: str, author: str) -> None:
        self.title = title
        self.file_name = self.source_files_manger.next_file_name(title)
        self.author = author

    def validate_user_info(self) -> bool:
        return len(self.author) > 0

    def create_document(self) -> None:
        title, author=self.dialog.get_user_input()
        self.set_info_for_document(title, author)

        if not self.validate_user_info():
            self.creator_listener.notify_about_result_of_main_function(False)
            return
        body_include_mark: str = SourceFile.create_include_command(DocumentCreator.BODY_MARK)
        basic_document: str = (f'{NoEscape(r'\documentclass{article}')}\n'
                               f'{NoEscape(r'\usepackage{graphicx}')}\n'
                               f'{NoEscape(r'\usepackage{float}')}\n\n'
                               f'{Command('title', self.title).dumps()}\n'
                               f'{Command('author', self.author).dumps()}\n'
                               f'{Command('date', datetime.now().strftime("%d %B %Y")).dumps()}\n\n'
                               f'{NoEscape(r'\begin{document}')}\n'
                               f'{NoEscape(r'\maketitle')}\n'
                               f'{body_include_mark}\n'
                               f'{NoEscape(r'\end{document}')}\n')
        result = self.source_files_manger.save_source_file(self.file_name, basic_document)
        self.creator_listener.notify_about_result_of_main_function(result)

    def get_use_dialog(self, parent_widget: QWidget) -> QDialog:
        self.dialog = TitleCreatorDialog(parent_widget)
        return self.dialog


if __name__ == '__main__':
    settings = {dir_type: f'..\\..\\..\\example\\{dir_type}' for dir_type in
                ['baseFiles', 'sourceFiles', 'generatedFiles']}


    class Listener(CreatorListener):
        def notify_about_result_of_main_function(self, result: bool):
            print(result)


    doc_creator = DocumentCreator(settings, Listener())

    app = QApplication(sys.argv)
    dialog = doc_creator.get_use_dialog(None)

    if dialog.exec() == QDialog.Accepted:
        title, author = dialog.get_user_input()
        doc_creator.set_info_for_document(title, author)
        doc_creator.create_document()

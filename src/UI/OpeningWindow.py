import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QLabel, QDialog, QGridLayout, QApplication, QSizePolicy, QFileDialog


class OpeningWindow(QDialog):
    DIALOG_TITLE: str = 'Select workspace option'
    CREATE_TITLE: str = 'Create workspace'
    OPEN_TITLE: str = 'Open workspace'
    FAILED_OPERATION_TEXT: str = 'Operation failed'

    MINIMUM_WIDTH: int = 300
    MINIMUM_HEIGHT: int = 50

    def __init__(self) -> None:
        super().__init__()
        self.setVisible(False)
        self.setWindowTitle(OpeningWindow.DIALOG_TITLE)

        self.directory_dialog=QFileDialog(self)
        self.directory_dialog.setFileMode(QFileDialog.Directory)

        self.setMinimumSize(OpeningWindow.MINIMUM_WIDTH, OpeningWindow.MINIMUM_HEIGHT)

        self.create_button: QPushButton = QPushButton(OpeningWindow.CREATE_TITLE)
        self.open_button: QPushButton = QPushButton(OpeningWindow.OPEN_TITLE)

        self.create_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.open_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.failure_label = QLabel(OpeningWindow.FAILED_OPERATION_TEXT)
        self.failure_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.failure_label.setStyleSheet('color:red')
        self.failure_label.setVisible(False)

        self.main_layout: QGridLayout = QGridLayout()
        self._build_structure()

    def _build_structure(self) -> None:
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.open_button, 0, 0)
        self.main_layout.addWidget(self.create_button, 0, 1)
        self.main_layout.addWidget(self.failure_label, 1, 0, 1, 2)

    def communicate_operation_failure(self) -> None:
        self.failure_label.setVisible(True)
        self.repaint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    opening_window = OpeningWindow()
    opening_window.show()
    sys.exit(app.exec())

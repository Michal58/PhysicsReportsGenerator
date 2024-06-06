from PySide6.QtWidgets import QDialog, QGridLayout, QLabel, QLineEdit, QWidget


class PairInputsDialog(QDialog):
    def __init__(self, parent_widget: QWidget):
        super().__init__(parent_widget)

    def add_pair(self, row: int, label_name: str, layout: QGridLayout) -> tuple[QLabel, QLineEdit]:
        label: QLabel = QLabel(label_name)
        input_for_user: QLineEdit = QLineEdit()
        layout.addWidget(label, row, 0)
        layout.addWidget(input_for_user, row, 1)
        return label, input_for_user

    def add_one_element(self, row: int, widget: QWidget, layout: QGridLayout) -> QWidget:
        layout.addWidget(widget, row, 0, 1, 2)
        return widget

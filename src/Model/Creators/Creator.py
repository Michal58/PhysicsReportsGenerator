import abc

from PySide6.QtWidgets import QWidget, QDialog


class Creator:
    @abc.abstractmethod
    def get_title(self) -> str:
        pass

    @abc.abstractmethod
    def get_use_dialog(self, parent_widget: QWidget) -> QDialog:
        pass

import abc
from typing import Any

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QMenu, QGridLayout, QFrame, QVBoxLayout, QListWidget, QPushButton, QWidget, \
    QHBoxLayout, QLabel, QLineEdit, QCheckBox, QGroupBox, QListWidgetItem, QDialog, QMessageBox, QTextEdit, \
    QTableWidget, QTableWidgetItem, QScrollArea

from Controller.Wrappers import FilepathWrapper, CreatorWrapper
from Model.Creators.Creator import Creator


class DisplayPanel(QGroupBox):
    def __init__(self) -> None:
        super().__init__(self.get_title())
        # self.setStyleSheet('background-color:orange')
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)

    @abc.abstractmethod
    def get_title(self) -> str:
        pass


class CreatorsPanel(DisplayPanel):
    MAIN_TITLE: str = 'Creators'
    FILTER_LABEL_TITLE: str = 'FILTER'
    CHECK_BOX_INFO: str = 'Regex'
    FILTER_PLACEHOLDER: str = 'filter'

    def __init__(self) -> None:
        super().__init__()
        self._build_filtering_part()

    def _build_filtering_part(self) -> None:
        self.filter_frame: QFrame = QFrame()
        self.filter_layout: QHBoxLayout = QHBoxLayout()
        self.filter_frame.setLayout(self.filter_layout)

        self.filter_label: QLabel = QLabel(CreatorsPanel.FILTER_LABEL_TITLE)
        self.filter_layout.addWidget(self.filter_label)

        self.filter_input: QLineEdit = QLineEdit()
        self.filter_input.setPlaceholderText(CreatorsPanel.FILTER_PLACEHOLDER)
        self.filter_layout.addWidget(self.filter_input)

        self.regex_checkbox: QCheckBox = QCheckBox(CreatorsPanel.CHECK_BOX_INFO)
        self.filter_layout.addWidget(self.regex_checkbox)

        self.layout().addWidget(self.filter_frame)

    def get_title(self) -> str:
        return CreatorsPanel.MAIN_TITLE


class AddRemButtonsSection(QFrame):
    ADD_TITLE: str = 'Add'
    REM_TITLE: str = 'Remove'

    def __init__(self):
        super().__init__()
        self.local_layout: QHBoxLayout = QHBoxLayout()
        self.setLayout(self.local_layout)
        self.add_button: QPushButton = QPushButton(AddRemButtonsSection.ADD_TITLE)
        self.rem_button: QPushButton = QPushButton(AddRemButtonsSection.REM_TITLE)
        self.local_layout.addWidget(self.add_button)
        self.local_layout.addWidget(self.rem_button)


class BaseFilesPanel(DisplayPanel):
    MAIN_TITLE: str = 'Base files'

    def __init__(self) -> None:
        super().__init__()
        self.files_operations_section: AddRemButtonsSection = AddRemButtonsSection()
        self.layout().addWidget(self.files_operations_section)

    def get_title(self) -> str:
        return BaseFilesPanel.MAIN_TITLE


class SourceFilesPanel(DisplayPanel):
    MAIN_TITLE: str = 'Source files'

    def __init__(self) -> None:
        super().__init__()
        self.files_operations_section: AddRemButtonsSection = AddRemButtonsSection()
        self.layout().addWidget(self.files_operations_section)

    def get_title(self) -> str:
        return SourceFilesPanel.MAIN_TITLE


class HelpDisplay(QDialog):
    def __init__(self, parent: QWidget, content: str):
        super().__init__(parent)
        self.setWindowTitle('Help')

        self.scroll_area: QScrollArea=QScrollArea()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.scroll_area)

        layout = QVBoxLayout(self)

        self.text_edit: QTextEdit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(content)
        layout.addWidget(self.text_edit)
        self.setMinimumWidth(500)

        self.scroll_area.setLayout(layout)


class VariablesDisplayPanel(QDialog):
    def __init__(self, parent: QWidget, variables: dict[str, Any]):
        super().__init__(parent)
        self.setWindowTitle('Variables')
        self.setLayout(QVBoxLayout())
        self.scroll_area=QScrollArea()
        layout = QVBoxLayout()
        self.scroll_area.setLayout(layout)
        self.pairs_table: QTableWidget = QTableWidget(len(variables), 2)
        self.pairs_table.setHorizontalHeaderLabels(["Variable", "Value"])
        for row, name in enumerate(variables):
            item_key = QTableWidgetItem(name)
            variable_display=str(variables[name])
            max_size_of_variable=50
            variable_display=variable_display[:max_size_of_variable] if len(variable_display)>max_size_of_variable else variable_display
            item_value = QTableWidgetItem(variable_display)
            self.pairs_table.setItem(row, 0, item_key)
            self.pairs_table.setItem(row, 1, item_value)
        layout.addWidget(self.pairs_table)
        self.layout().addWidget(self.scroll_area)

class MainWindow(QMainWindow):
    TITLE: str = 'PhysicsReportsGenerator'

    GENERATE_MENUS_TITLE: str = 'Generate'
    VARIABLES_MENUS_TITLE: str = 'Variables'
    MANUAL_MENUS_TITLE: str = 'Manual'
    CLOSE_MENU_TITLE: str = 'Close'
    LINK_MARKS: str = 'Link marks'

    MENUS_LIST: list[str] = [GENERATE_MENUS_TITLE, VARIABLES_MENUS_TITLE, MANUAL_MENUS_TITLE,
                             CLOSE_MENU_TITLE]

    MENU_BAR_CONTRAST_FACTOR: int = 200

    GENERATE_TEX_TITLE: str = 'Generate .tex'
    GENERATE_TEX_AND_PDF: str = 'Generate .tex and pdf'

    SET_BASE_FILES_TITLE: str = 'Base files dir'
    SET_SOURCE_FILES_TITLE: str = 'Source files dir'
    SET_GENERATED_FILES_TITLE: str = 'Generated files dir'

    USE_BUTTON_TITLE: str = 'USE'
    GENERATE_REPORT_BUTTON_TITLE: str = 'GENERATE REPORT'

    MAX_HEIGHT_OF_LOWER_BAR: int = 75
    MIN_HEIGHT_OF_LOWER_BAR: int = 40

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(MainWindow.TITLE)
        background_color = self.palette().color(self.backgroundRole())
        self.menuBar().setStyleSheet(
            f"background-color: {background_color.lighter(MainWindow.MENU_BAR_CONTRAST_FACTOR).name()}")
        # self.menuBar().setLayoutDirection(Qt.LeftToRight)

        self._create_menus()
        self._create_content_layout()

    def produce_null_action(self) -> QAction:
        null_action: QAction = QAction('')
        null_action.setVisible(False)
        return null_action

    def _create_menus(self) -> None:
        self._create_and_connect_generate_menu()

        self.variables_menu: QMenu = QMenu(MainWindow.VARIABLES_MENUS_TITLE, self)
        self.menuBar().addMenu(self.variables_menu)

        self.null_action = self.produce_null_action()
        self.help_menu: QMenu = QMenu(MainWindow.MANUAL_MENUS_TITLE, self)
        self.help_menu.addAction(self.null_action)
        self.menuBar().addMenu(self.help_menu)

        self.close_menu: QMenu = QMenu(MainWindow.CLOSE_MENU_TITLE, self)
        self.menuBar().addMenu(self.close_menu)

    def _create_and_connect_generate_menu(self) -> None:
        self.generate_menu: QMenu = QMenu(MainWindow.GENERATE_MENUS_TITLE, self)
        self.menuBar().addMenu(self.generate_menu)

        self.link_marks: QAction = QAction(MainWindow.LINK_MARKS)
        self.generate_menu.addAction(self.link_marks)

        self.generate_tex: QAction = QAction(MainWindow.GENERATE_TEX_TITLE)
        self.generate_menu.addAction(self.generate_tex)

        self.generate_tex_and_pdf: QAction = QAction(MainWindow.GENERATE_TEX_AND_PDF)
        self.generate_menu.addAction(self.generate_tex_and_pdf)

    def _create_content_layout(self) -> None:
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        main_layout: QGridLayout = QGridLayout()
        self.main_widget.setLayout(main_layout)

        self.creators_panel: CreatorsPanel = CreatorsPanel()
        main_layout.addWidget(self.creators_panel, 0, 0)

        self.base_files_panel: BaseFilesPanel = BaseFilesPanel()
        main_layout.addWidget(self.base_files_panel, 0, 1)

        self.source_files_panel: SourceFilesPanel = SourceFilesPanel()
        main_layout.addWidget(self.source_files_panel, 0, 2)

        self.use_creator_button: QPushButton = QPushButton(MainWindow.USE_BUTTON_TITLE)
        self.use_creator_button.setMaximumHeight(MainWindow.MAX_HEIGHT_OF_LOWER_BAR)
        self.use_creator_button.setMinimumHeight(MainWindow.MIN_HEIGHT_OF_LOWER_BAR)
        main_layout.addWidget(self.use_creator_button, 1, 0)

        self.generate_report_button: QPushButton = QPushButton(MainWindow.GENERATE_REPORT_BUTTON_TITLE)
        self.generate_report_button.setMaximumHeight(MainWindow.MAX_HEIGHT_OF_LOWER_BAR)
        self.generate_report_button.setMinimumHeight(MainWindow.MIN_HEIGHT_OF_LOWER_BAR)
        main_layout.addWidget(self.generate_report_button, 1, 1, 1, 2)

    def update_panels(self, creators_list: list[CreatorWrapper], base_files: list[FilepathWrapper],
                      source_files: list[FilepathWrapper]) -> None:
        for panel, new_list in zip([self.creators_panel, self.base_files_panel, self.source_files_panel],
                                   [creators_list, base_files, source_files]):
            panel.list_widget.clear()
            for element in new_list:
                panel.list_widget.addItem(element)

    def _get_selected_items(self, panel: DisplayPanel) -> list[QListWidgetItem]:
        return panel.list_widget.selectedItems()

    @property
    def selected_creator(self) -> Creator | None:
        selected_items = self._get_selected_items(self.creators_panel)
        if selected_items == []:
            return None
        return selected_items[0].creator

    @property
    def selected_base_file(self) -> str | None:
        selected_items = self._get_selected_items(self.base_files_panel)
        if selected_items == []:
            return None
        return selected_items[0].filepath

    @property
    def selected_source_file(self) -> str | None:
        selected_items = self._get_selected_items(self.source_files_panel)
        if selected_items == []:
            return None
        return selected_items[0].filepath

    def create_failure_message_box(self, additional_message='') -> QDialog:
        OPERATION_FAILED_TEXT: str = 'Operation failure - tried operation couldn\'t be completed'
        WINDOW_TITLE: str = "Operation failure"

        msg = QDialog(self)
        layout: QVBoxLayout = QVBoxLayout()
        msg.setLayout(layout)
        msg.setWindowTitle(WINDOW_TITLE)
        layout.addWidget(QLabel(OPERATION_FAILED_TEXT))
        if additional_message != '':
            layout.addWidget(QLabel(additional_message))
        accept_button: QPushButton = QPushButton('OK')
        layout.addWidget(accept_button)

        accept_button.clicked.connect(msg.accept)

        return msg

    def get_help_window(self, content: str) -> HelpDisplay:
        return HelpDisplay(self, content)

    def get_variables_display(self,variables:dict[str,str])->VariablesDisplayPanel:
        return VariablesDisplayPanel(self,variables)
import abc

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QMenu, QGridLayout, QFrame, QVBoxLayout, QListWidget, QPushButton, QWidget, \
    QHBoxLayout, QLabel, QLineEdit, QCheckBox, QGroupBox


class DisplayPanel(QGroupBox):
    def __init__(self) -> None:
        super().__init__(self.get_title())
        # self.setStyleSheet('background-color:orange')
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.list = QListWidget()
        main_layout.addWidget(self.list)

    @abc.abstractmethod
    def get_title(self) -> str:
        pass


class CreatorsPanel(DisplayPanel):
    MAIN_TITLE: str = 'Creators'
    FILTER_LABEL_TITLE: str = 'FILTER'
    CHECK_BOX_INFO: str = 'Regex'

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


class MainWindow(QMainWindow):
    TITLE: str = 'PhysicsReportsGenerator'

    GENERATE_MENUS_TITLE: str = 'Generate'
    VARIABLES_MENUS_TITLE: str = 'Variables'
    SETTINGS_MENUS_TITLE: str = 'Settings'
    MANUAL_MENUS_TITLE: str = 'Manual'
    CLOSE_MENU_TITLE: str = 'Close'

    MENUS_LIST: list[str] = [GENERATE_MENUS_TITLE, VARIABLES_MENUS_TITLE, SETTINGS_MENUS_TITLE, MANUAL_MENUS_TITLE,
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

    def _create_menus(self) -> None:
        self._create_and_connect_generate_menu()
        self._create_and_connect_settings()

        self.variables_menu: QMenu = QMenu(MainWindow.VARIABLES_MENUS_TITLE, self)
        self.menuBar().addMenu(self.variables_menu)

        self.manual_menu: QMenu = QMenu(MainWindow.MANUAL_MENUS_TITLE, self)
        self.menuBar().addMenu(self.manual_menu)

        self.close_menu: QMenu = QMenu(MainWindow.CLOSE_MENU_TITLE, self)
        self.menuBar().addMenu(self.close_menu)

    def _create_and_connect_generate_menu(self) -> None:
        self.generate_menu: QMenu = QMenu(MainWindow.GENERATE_MENUS_TITLE, self)
        self.menuBar().addMenu(self.generate_menu)

        self.generate_tex: QAction = QAction(MainWindow.GENERATE_TEX_TITLE)
        self.generate_menu.addAction(self.generate_tex)

        self.generate_tex_and_pdf: QAction = QAction(MainWindow.GENERATE_TEX_AND_PDF)
        self.generate_menu.addAction(self.generate_tex_and_pdf)

    def _create_and_connect_settings(self) -> None:
        self.settings_menu: QMenu = QMenu(MainWindow.SETTINGS_MENUS_TITLE, self)
        self.menuBar().addMenu(self.settings_menu)

        self.set_base_files_directory: QAction = QAction(MainWindow.SET_BASE_FILES_TITLE)
        self.settings_menu.addAction(self.set_base_files_directory)

        self.set_source_files_directory: QAction = QAction(MainWindow.SET_SOURCE_FILES_TITLE)
        self.settings_menu.addAction(self.set_source_files_directory)

        self.set_generated_files_directory: QAction = QAction(MainWindow.SET_GENERATED_FILES_TITLE)
        self.settings_menu.addAction(self.set_generated_files_directory)

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

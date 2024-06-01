import sys

from PySide6.QtWidgets import QWidget, QDialog, QLabel, QFileDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, \
    QApplication, QCheckBox, QGroupBox, QListWidget, QListWidgetItem

from Model.Creators.Creator import Creator
from Model.Creators.CreatorListener import CreatorListener
from Model.Variables.VariablesConsumer import VariablesConsumer
from settings_namespace import BASE_FILES

class AddingGroupBox(QGroupBox):
    def __init__(self, title):
        super().__init__(title)
        self.layout: QVBoxLayout = QVBoxLayout()

        self.added_elements_list: QListWidget = QListWidget()
        self.added_elements_list.setMaximumHeight(TableCreatorDialog.MAXIMUM_HEIGHTS_OF_LISTS)
        self.added_elements_list.setVisible(False)
        self.layout.addWidget(self.added_elements_list)

        self.new_elements_control_panel: QVBoxLayout = QVBoxLayout()

        self.add_elements_grouper: QHBoxLayout = QHBoxLayout()
        self.add_element_button: QPushButton = QPushButton('Add')
        self.name_of_element_input: QLineEdit = QLineEdit()

        self.add_elements_grouper.addWidget(self.add_element_button)
        self.add_elements_grouper.addWidget(self.name_of_element_input)
        self.new_elements_control_panel.addLayout(self.add_elements_grouper)

        self.remove_element_button: QPushButton = QPushButton('Remove')
        self.new_elements_control_panel.addWidget(self.remove_element_button)

        self.layout.addStretch()
        self.layout.addLayout(self.new_elements_control_panel)

        self.setLayout(self.layout)

    def add_element(self) -> None:
        if self.name_of_element_input.text() != '':
            self.added_elements_list.addItem(self.name_of_element_input.text())
            self.name_of_element_input.setText('')
            self.added_elements_list.setVisible(True)

    def remove_element(self) -> None:
        selected_columns: list[QListWidgetItem] = self.added_elements_list.selectedItems()
        if selected_columns:
            self.added_elements_list.takeItem(self.added_elements_list.currentRow())
            if self.added_elements_list.count() == 0:
                self.added_elements_list.setVisible(False)
                self.update()

    def make_connections(self) -> None:
        self.add_element_button.clicked.connect(self.add_element)
        self.remove_element_button.clicked.connect(self.remove_element)

    def get_all_items(self) -> list[str]:
        return [self.added_elements_list.item(i).text() for i in range(self.added_elements_list.count() - 1)]


class SelectFileSection(QVBoxLayout):
    def __init__(self, label_title: str, file_select_dialog: QFileDialog, dialog_caption: str, dialog_base_dir: str,
                 dialog_filters: str) -> None:
        super().__init__()
        self.file_select_dialog: QFileDialog = file_select_dialog
        self.dialog_caption: str = dialog_caption
        self.dialog_base_dir: str = dialog_base_dir
        self.dialog_filters: str = dialog_filters

        self.select_layout: QHBoxLayout = QHBoxLayout()
        self.select_label: QLabel = QLabel(label_title)
        self.select_table_button: QPushButton = QPushButton("Select")

        self.select_layout.addWidget(self.select_label)
        self.select_layout.addWidget(self.select_table_button)
        self.addLayout(self.select_layout)

        self.select_displayer: QLineEdit = QLineEdit()
        self.select_displayer.setReadOnly(True)
        self.addWidget(self.select_displayer)

    def select_file(self) -> None:
        options: QFileDialog.Option = QFileDialog.Options()
        file, _ = self.file_select_dialog.getOpenFileName(self.file_select_dialog.parent(), self.dialog_caption,
                                                          self.dialog_base_dir,
                                                          self.dialog_filters, options=options)
        self.file_path: str = file
        self.select_displayer.setText(self.file_path)

    def make_connections(self):
        self.select_table_button.clicked.connect(self.select_file)


class TableCreatorDialog(QDialog):
    MAXIMUM_HEIGHTS_OF_LISTS = 350

    def __init__(self, parent_widget: QWidget, settings: dict[str, str]) -> None:
        super().__init__(parent_widget)
        self.settings = settings
        self.setWindowTitle("Table creator")
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.file_select_dialog: QFileDialog = QFileDialog(self)
        self.select_table_section: SelectFileSection = SelectFileSection('Base table', self.file_select_dialog,
                                                                         'Select base table', self.settings[BASE_FILES],
                                                                         "Raw Table (*.txt);;Saved Table (*.csv)")
        self.main_layout.addLayout(self.select_table_section)
        self.create_index_option: QCheckBox = QCheckBox("Create index")
        self.main_layout.addWidget(self.create_index_option)
        self._build_name_of_name_table_section()
        self.add_columns_group = AddingGroupBox('New columns')
        self.main_layout.addWidget(self.add_columns_group)
        self.add_rows_group = AddingGroupBox('New rows')
        self.main_layout.addWidget(self.add_rows_group)
        self.calculating_script_section: SelectFileSection = SelectFileSection('Calculating script',
                                                                               self.file_select_dialog,
                                                                               'Select calculating script',
                                                                               self.settings[BASE_FILES],
                                                                               "Python script (*.py)")
        self.main_layout.addLayout(self.calculating_script_section)
        self.formatting_script_section: SelectFileSection = SelectFileSection('Formatting script',
                                                                              self.file_select_dialog,
                                                                              'Select formatting script',
                                                                              self.settings[BASE_FILES],
                                                                              "Python script (*.py)")
        self.main_layout.addLayout(self.formatting_script_section)

        self.checkboxes: QHBoxLayout = QHBoxLayout()

        self.gspread_save: QCheckBox = QCheckBox('Save to gspread')
        self.csv_save: QCheckBox = QCheckBox('Save to csv')
        self.as_source_save: QCheckBox = QCheckBox('Convert table into source file')
        self.checkboxes.addWidget(self.gspread_save)
        self.checkboxes.addWidget(self.csv_save)
        self.checkboxes.addWidget(self.as_source_save)

        self.main_layout.addLayout(self.checkboxes)

        self.ok_button: QPushButton = QPushButton('OK')

        self.main_layout.addWidget(self.ok_button)

        self._make_connections()
        self.resize(500, -1)

    def _build_name_of_name_table_section(self):
        self.local_layout: QHBoxLayout = QHBoxLayout()

        self.name_table_label: QLabel = QLabel("Table name")
        self.name_table_input: QLineEdit = QLineEdit()

        self.local_layout.addWidget(self.name_table_label)
        self.local_layout.addWidget(self.name_table_input)

        self.main_layout.addLayout(self.local_layout)

    def _make_connections(self) -> None:
        self.select_table_section.make_connections()
        self.add_columns_group.make_connections()
        self.add_rows_group.make_connections()
        self.calculating_script_section.make_connections()
        self.formatting_script_section.make_connections()
        self.ok_button.clicked.connect(self.accept)

    def get_user_input(self) -> dict[str, str | bool | list[str]]:
        data_pack: dict[str, str | bool | list[str]] = {'base_table': self.select_table_section.select_displayer.text(),
                                                        'index_to_create': self.create_index_option.isChecked(),
                                                        'table_name': self.name_table_input.text(),
                                                        'columns': self.add_columns_group.get_all_items(),
                                                        'rows': self.add_rows_group.get_all_items(),
                                                        'calc_script': self.calculating_script_section.select_displayer.text(),
                                                        'formatting_script': self.formatting_script_section.select_displayer.text(),
                                                        'gspread': self.gspread_save.isChecked(),
                                                        'csv': self.csv_save.isChecked(),
                                                        'source': self.as_source_save.isChecked()}

        return data_pack


class TableCreator(Creator, VariablesConsumer):
    def __init__(self, settings: dict[str, str], creator_listener: CreatorListener, parent_widget: QWidget):
        super().__init__(settings, creator_listener, parent_widget)


if __name__ == '__main__':
    local_settings = {dir_type: f'..\\..\\..\\example\\{dir_type}' for dir_type in
                      ['baseFiles', 'sourceFiles', 'generatedFiles']}
    app = QApplication(sys.argv)
    dialog = TableCreatorDialog(None, local_settings)
    d_exec = dialog.exec()
    print(d_exec == QDialog.Accepted)

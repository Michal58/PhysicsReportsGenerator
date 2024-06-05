import os

import gspread
import re
import sys
from types import ModuleType

import numpy as np
import pandas as pd
import sympy as sym

from PySide6.QtWidgets import QWidget, QDialog, QLabel, QFileDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, \
    QApplication, QCheckBox, QGroupBox, QListWidget, QListWidgetItem
from gspread import Client, Spreadsheet, Worksheet, Cell

from Model.Creators.Creator import Creator
from Model.Creators.CreatorListener import CreatorListener
from Model.SourceFiles.SourceFilesManager import SourceFilesManager
from Model.Variables.VariablesConsumer import VariablesConsumer
from Model.utils import path_to_module
from settings_namespace import BASE_FILES, ENCODING, SOURCE_FILES


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
        return [self.added_elements_list.item(i).text() for i in range(self.added_elements_list.count())]


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
        self.create_index_option.setChecked(True)
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

        self._build_gspread_input()

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

    def _build_gspread_input(self):
        self.local_layout = QHBoxLayout()
        self.spreadsheet_key_label = QLabel('Spreadsheet key')
        self.spreadsheet_key_input = QLineEdit()
        self.spreadsheet_key_input.setEnabled(False)
        self.local_layout.addWidget(self.spreadsheet_key_label)
        self.local_layout.addWidget(self.spreadsheet_key_input)
        self.main_layout.addLayout(self.local_layout)

    def gspread_clicked(self):
        if not self.gspread_save.isChecked():
            self.spreadsheet_key_input.setText('')
            self.spreadsheet_key_input.setEnabled(False)
        else:
            self.spreadsheet_key_input.setEnabled(True)

    def _make_connections(self) -> None:
        self.select_table_section.make_connections()
        self.add_columns_group.make_connections()
        self.add_rows_group.make_connections()
        self.calculating_script_section.make_connections()
        self.formatting_script_section.make_connections()
        self.ok_button.clicked.connect(self.accept)
        self.gspread_save.clicked.connect(self.gspread_clicked)

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
                                                        'source': self.as_source_save.isChecked(),
                                                        'key': self.spreadsheet_key_input.text()}

        return data_pack


class TableCreator(Creator, VariablesConsumer):
    TITLE: str = 'Table Creator'
    TABLE_VALID_FORMAT: str = SourceFilesManager.NAME_FORMAT
    BASE_FILE_COLUMNS_SPLIT_DELIMITER_FORMAT: str = r'\s*,\s*'
    FLOAT_FORMAT: str = r'[-+]?(?:\d*\.?\d+)'
    INT_FORMAT: str = r'[-+]?\d+'
    CSV_SEPARATOR: str = ','

    INVALID_SCRIPT_MESSAGE: str = 'Provided script cannot perform its task'
    SAVE_PROBLEMS:str="Problems occurred while saving"
    CALCULATING_SCRIPT_RUN_FUNCTION: str = 'calc'
    FORMATTING_SCRIPT_TRANSFORMER: str = 'transform'
    FORMATTING_SCRIPT_SOURCE_SAVER: str = 'save_to_source'
    FORMATTED_TABLE_PREFIX: str = 'Formatted_'

    INDEX_NAME: str = 'No.'

    GSPREAD_SCOPES: list[str] = ['https://www.googleapis.com/auth/spreadsheets']

    def __init__(self, settings: dict[str, str], creator_listener: CreatorListener, parent_widget: QWidget):
        super().__init__(settings, creator_listener, parent_widget)
        self.table_create_dialog: TableCreatorDialog = TableCreatorDialog(parent_widget, self.settings)
        self.dialog_result: int = QDialog.Rejected

        self.base_table_path: str = ''
        self.should_create_index: bool = False
        self.table_name: str = ''
        self.columns: list[str] = []
        self.rows: list[str] = []
        self.calculating_script_path: str = ''
        self.formatting_script_path: str = ''
        self.should_save_to_gspread: bool = False
        self.should_save_csv: bool = False
        self.should_make_source_file: bool = False
        self.spreadsheet_key: str = ''

    def get_title(self) -> str:
        return TableCreator.TITLE

    def get_use_dialog(self) -> QDialog:
        return self.table_create_dialog

    def set_data(self) -> None:
        self.dialog_result = self.table_create_dialog.exec()
        data_pack: dict[str, str | bool | list[str]] = self.table_create_dialog.get_user_input()

        self.base_table_path = data_pack['base_table']
        self.should_create_index = data_pack['index_to_create']
        self.table_name = data_pack['table_name']
        self.columns = data_pack['columns']
        self.rows = data_pack['rows']
        self.calculating_script_path = data_pack['calc_script']
        self.formatting_script_path = data_pack['formatting_script']
        self.should_save_to_gspread = data_pack['gspread']
        self.should_save_csv = data_pack['csv']
        self.should_make_source_file = data_pack['source']
        self.spreadsheet_key = data_pack['key']

    def validate_input(self) -> bool:
        return re.fullmatch(TableCreator.TABLE_VALID_FORMAT, self.table_name) is not None

    def validate_data(self) -> bool:
        return self.dialog_result == QDialog.Accepted and self.validate_input()

    def get_columns_from_file(self) -> list[str]:
        with open(self.base_table_path, 'r', encoding=ENCODING) as file:
            first_line: str = file.readline().strip()
            columns: list[str] = re.split(TableCreator.BASE_FILE_COLUMNS_SPLIT_DELIMITER_FORMAT, first_line)
            return columns

    def raw_value_converter(self, raw_value: str) -> str | float | int:
        if re.fullmatch(TableCreator.FLOAT_FORMAT, raw_value) is not None:
            return float(raw_value)
        elif re.fullmatch(TableCreator.INT_FORMAT, raw_value) is not None:
            return int(raw_value)
        else:
            return raw_value

    def create_row_from_base_file(self, line: str, number_of_columns: int) -> list[str | float | int]:
        raw_values: list[str] = re.split(TableCreator.BASE_FILE_COLUMNS_SPLIT_DELIMITER_FORMAT, line)

        refactored_values: list[str | float | int] = list(map(self.raw_value_converter, raw_values))
        if len(refactored_values) >= number_of_columns:
            return refactored_values[:number_of_columns]
        else:
            return refactored_values + [np.NAN] * (number_of_columns - len(refactored_values))

    def load_table_from_text_file(self) -> pd.DataFrame:
        columns = self.get_columns_from_file()

        collected_data: list[list[str | float | int]] = []

        with open(self.base_table_path, 'r', encoding=ENCODING) as file:
            for i, line in enumerate(file):
                line = line.rstrip()
                if i != 0:
                    collected_data.append(self.create_row_from_base_file(line, len(columns)))

        return pd.DataFrame(data=collected_data, columns=columns)

    def load_table_from_file(self) -> pd.DataFrame:
        if self.base_table_path.endswith('.txt'):
            return self.load_table_from_text_file()
        else:
            return pd.read_csv(self.base_table_path, index_col=0, sep=TableCreator.CSV_SEPARATOR)

    def run_calculating_script(self) -> None:
        script: ModuleType = path_to_module(self.calculating_script_path)
        if hasattr(script, TableCreator.CALCULATING_SCRIPT_RUN_FUNCTION):
            self.variables[self.table_name] = script.run(self.variables[self.table_name])
        else:
            raise ValueError(TableCreator.INVALID_SCRIPT_MESSAGE)

    def get_formatted_table_name(self) -> str:
        return f'{TableCreator.FORMATTED_TABLE_PREFIX}{self.table_name}'

    def run_formatting_script(self) -> None:
        script: ModuleType = path_to_module(self.formatting_script_path)
        if hasattr(script, TableCreator.FORMATTING_SCRIPT_TRANSFORMER):
            name_of_formatted_frame: str = self.get_formatted_table_name()
            self.variables[name_of_formatted_frame] = script.transform(self.variables[self.table_name])
        else:
            raise ValueError(TableCreator.INVALID_SCRIPT_MESSAGE)

    def save_data_frame_to_spreadsheet(self, variable_id: str) -> None:
        client: Client = gspread.oauth()
        spreadsheet: Spreadsheet = client.open_by_key(self.spreadsheet_key)
        worksheet_name = variable_id
        worksheet: Worksheet

        data_frame: pd.DataFrame = self.variables[variable_id]
        copy_of_frame: pd.DataFrame=data_frame.copy(True).fillna('')
        data_frame = copy_of_frame

        if worksheet_name not in [sheet.title for sheet in spreadsheet.worksheets()]:
            rows, columns = data_frame.shape

            worksheet = spreadsheet.add_worksheet(worksheet_name, rows + 1, columns + 1)
        else:
            worksheet = spreadsheet.worksheet(worksheet_name)

        cells_to_update: list[Cell] = []

        offset: int = 1
        if self.should_create_index:
            cells_to_update.append(Cell(offset, offset, data_frame.index.name))
        cells_to_update += [Cell(offset, i + offset + (1 if self.should_create_index else 0), column)
                            for i, column in enumerate(data_frame.columns)]
        for i, (index_name, row) in enumerate(data_frame.iterrows()):
            index_name: int | str | float = index_name
            elements_list: list[int | str | float] = ([index_name] if self.should_create_index else []) + list(row)
            for j, element in enumerate(elements_list):
                cells_to_update.append(Cell(i + offset + 1, j + offset, element))
        worksheet.update_cells(cells_to_update)

    def save_table_with_formatting_script(self):
        script: ModuleType = path_to_module(self.formatting_script_path)
        if hasattr(script, TableCreator.FORMATTING_SCRIPT_SOURCE_SAVER):
            formatted_table: pd.DataFrame = self.variables[self.get_formatted_table_name()]
            script.save_to_source(formatted_table, self.settings[SOURCE_FILES])
        else:
            self.save_table_to_source_as_default(self.variables[self.get_formatted_table_name()])

    def save_table_to_source_as_default(self, data_frame: pd.DataFrame) -> None:
        copy_od_data_frame=data_frame.copy(True).fillna('')

        latex_content: str = copy_od_data_frame.to_latex(index=True, caption=self.table_name, label=f'tab:{self.table_name}',escape=False, position='H',longtable=True)
        files_manager: SourceFilesManager=SourceFilesManager(self.settings)
        if not files_manager.save_next_source_file(self.table_name,latex_content):
            raise Exception(TableCreator.SAVE_PROBLEMS)

    def construct_table_and_save(self) -> bool:
        data_frame: pd.DataFrame = pd.DataFrame()
        if self.base_table_path != '':
            try:
                if self.base_table_path != '':
                    data_frame = self.load_table_from_file()
                if self.should_create_index:
                    data_frame.index.name = TableCreator.INDEX_NAME
                for column in self.columns:
                    data_frame[column] = np.nan
                if len(self.rows) > 0:
                    data_frame = pd.concat(
                        [data_frame, pd.DataFrame(index=self.rows, columns=list(data_frame.columns))])
                self.variables[self.table_name] = data_frame
                if self.calculating_script_path != '':
                    self.run_calculating_script()
                if self.formatting_script_path != '':
                    self.run_formatting_script()
                if self.should_save_to_gspread:
                    self.save_data_frame_to_spreadsheet(self.table_name)
                    if self.formatting_script_path != '':
                        self.save_data_frame_to_spreadsheet(self.get_formatted_table_name())
                if self.should_save_csv:
                    data_frame: pd.DataFrame = self.variables[self.table_name]
                    copy_od_data_frame: pd.DataFrame=data_frame.copy(True).fillna('')
                    copy_od_data_frame.to_csv(os.path.join(self.settings[BASE_FILES], f'{self.table_name}.csv'), index=self.should_create_index, sep=TableCreator.CSV_SEPARATOR, encoding=ENCODING)
                    if self.formatting_script_path != '':
                        formatted_frame: pd.DataFrame = self.variables[self.get_formatted_table_name()]
                        formatted_frame.to_csv(self.settings[BASE_FILES], index=self.should_create_index,
                                               sep=TableCreator.CSV_SEPARATOR)
                if self.should_make_source_file:
                    if self.formatting_script_path != '':
                        self.save_table_with_formatting_script()
                    else:
                        self.save_table_to_source_as_default(self.variables[self.table_name])
                return True
            except Exception as e:
                print(e)
                return False

    def perform_operations(self) -> bool:
        return self.construct_table_and_save()


if __name__ == '__main__':
    local_settings = {dir_type: f'..\\..\\..\\example\\{dir_type}' for dir_type in
                      ['baseFiles', 'sourceFiles', 'generatedFiles']}

    variables = {'eq': sym.sympify('h^2/2')}


    class Listener(CreatorListener):
        def notify_about_result_of_main_function(self, result: bool):
            print(result)


    app = QApplication(sys.argv)
    table_creator = TableCreator(local_settings, Listener(), None)
    table_creator.set_variables(variables)
    table_creator.perform_functionality()
    print(variables)

    # tab_creator = TableCreator(local_settings, Listener(), None)
    # tab_creator.set_variables({})
    #
    # tab_creator.base_table_path = '..\\..\\..\\example\\baseFiles\\BaseRows.txt'
    #
    # print(tab_creator.load_table_from_text_file())

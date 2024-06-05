import sys

import numpy as np
import pandas as pd
import sympy as sym
from PySide6.QtWidgets import QWidget, QDialog, QGridLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QApplication
from sklearn.linear_model import LinearRegression

from Model.Creators.Creator import Creator
from Model.Creators.CreatorListener import CreatorListener
from Model.Creators.TableCreator import TableCreator
from Model.SourceFiles.SourceFilesManager import SourceFilesManager
from Model.Variables.VariablesConsumer import VariablesConsumer
from UI.PairInputsDialog import PairInputsDialog


class RegressionDialog(PairInputsDialog):
    def __init__(self, parent_widget: QWidget):
        super().__init__(parent_widget)
        self.setWindowTitle('Conduct regression')
        layout = QGridLayout()

        self.add_pair(0, 'Input name of variable with data:', layout)
        self.add_pair(1, 'Input name of variable with prediction results:', layout)
        self.add_pair(2, 'Input name of saved results:', layout)

        self.save_as_source_file_check: QCheckBox = QCheckBox('Save in source file')
        layout.addWidget(self.save_as_source_file_check, 3, 0, 1, 2)

        self.changing_visible_rows_start_index = 4

        self.add_pair(4, 'Input coefficient header:', layout)
        self.add_pair(5, 'Input coefficient error header:', layout)
        self.add_pair(6, 'Input intercept header:', layout)
        self.add_pair(7, 'Input intercept error header:', layout)

        self.changing_visible_rows_end_index = 7

        self.ok_button: QPushButton = QPushButton('OK')
        layout.addWidget(self.ok_button, 8, 0, 1, 2)

        self.setLayout(layout)

        self.change_visibility(False)

        self.save_as_source_file_check.clicked.connect(
            lambda: self.change_visibility(self.save_as_source_file_check.isChecked()))
        self.ok_button.clicked.connect(self.accept)

    def change_visibility(self, new_visible_stance: bool):
        for i in range(self.changing_visible_rows_start_index, self.changing_visible_rows_end_index + 1):
            self.layout().itemAtPosition(i, 0).widget().setVisible(new_visible_stance)
            self.layout().itemAtPosition(i, 1).widget().setVisible(new_visible_stance)

    def get_user_input(self) -> list[str]:
        return [self.layout().itemAtPosition(i, 1).widget().text() for i in range(9) if i!=3 and i!=8]


class RegressionResults:
    def __init__(self, a_coefficient: float, b_offset: float, uA_error: float, uB_error: float) -> None:
        self.a_coefficient: float = a_coefficient
        self.b_intercept: float = b_offset
        self.uA_error: float = uA_error
        self.uB_error: float = uB_error

    def __str__(self):
        return f'{self.a_coefficient};{self.b_intercept};{self.uA_error};{self.uB_error}'

    def __repr__(self):
        return self.__str__()

class RegressionConductor(Creator, VariablesConsumer):
    TITLE: str = 'Linear regression creator'

    def __init__(self, settings: dict[str, str], creator_listener: CreatorListener, parent_widget: QWidget):
        super().__init__(settings, creator_listener, parent_widget)
        self.dialog = RegressionDialog(parent_widget)
        self.getting_result: int = QDialog.Rejected
        self.x_axis_name: str = ''
        self.y_axis_name: str = ''
        self.new_var_name: str = ''
        self.table_headers: list[str] = []

    def get_title(self) -> str:
        return RegressionConductor.TITLE

    def get_use_dialog(self) -> QDialog:
        return self.dialog

    def set_data(self) -> None:
        self.getting_result = self.dialog.exec()
        user_input: list[str] = self.dialog.get_user_input()
        self.x_axis_name = user_input[0]
        self.y_axis_name = user_input[1]
        self.new_var_name = user_input[2]
        self.table_headers = user_input[3:]

    def check_if_variables_names_are_valid(self):
        return self.x_axis_name in self.variables.keys() and self.y_axis_name in self.variables.keys() and self.new_var_name != '' and (
                    set(self.table_headers) == {''} or '' not in self.table_headers)

    def validate_data(self) -> bool:
        return self.getting_result == QDialog.Accepted and self.check_if_variables_names_are_valid()

    def square_error(self, y: pd.Series, y_predicted: pd.Series) -> np.float64:
        return np.sum((y - y_predicted) ** 2)

    def regression_slope_error(self, x: pd.Series, y: pd.Series, y_predicted: pd.Series) -> np.float64:
        return np.sqrt(self.square_error(y, y_predicted) / (len(y) - 2)) / np.sqrt(self.square_error(x, np.mean(x)))

    def regression_intercept_error(self, x: pd.Series, slope_error: np.float64) -> np.float64:
        return np.sqrt(1 / len(x) * slope_error ** 2 * np.sum(x ** 2))

    def conduct_linear_regression(self, x_axis: pd.Series, y_axis: pd.Series) -> RegressionResults:
        regression: LinearRegression = LinearRegression().fit(x_axis.to_numpy().reshape(-1, 1), y_axis.to_numpy())
        slope_error: np.float64 = self.regression_slope_error(x_axis, y_axis,
                                                              regression.predict(x_axis.to_numpy().reshape(-1, 1)))
        intercept_error: np.float64 = self.regression_intercept_error(x_axis, slope_error)
        result: RegressionResults = RegressionResults(regression.coef_[0], regression.intercept_, float(slope_error),
                                                      float(intercept_error))
        return result

    def perform_operations(self) -> bool:
        try:
            regression_result: RegressionResults = self.conduct_linear_regression(self.variables[self.x_axis_name],
                                                                                  self.variables[self.y_axis_name])
            self.variables[self.new_var_name] = regression_result
            if self.table_headers[0] == '':
                return True

            latex_content: str = (pd.Series(index=self.table_headers,
                                            data=[regression_result.a_coefficient,
                                                  regression_result.b_intercept,
                                                  regression_result.uA_error,
                                                  regression_result.uB_error])
                                  .to_latex(caption=self.new_var_name, header=False,
                                            label=f'tab:{self.new_var_name}',
                                            escape=False, position='H', longtable=True))
            files_manager: SourceFilesManager = SourceFilesManager(self.settings)
            if not files_manager.save_next_source_file(self.new_var_name, latex_content):
                raise Exception(TableCreator.SAVE_PROBLEMS)

            return True
        except Exception:
            return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    reg = RegressionConductor({}, None, None)
    res = reg.conduct_linear_regression(pd.Series([1, 2, 3, 4, 5, 6]), pd.Series([5, 9, 15, 18, 27, 30]))
    print(f'{res.a_coefficient};{res.b_intercept};{res.uA_error};{res.uB_error}')

    local_settings = {dir_type: f'..\\..\\..\\example\\{dir_type}' for dir_type in
                      ['baseFiles', 'sourceFiles', 'generatedFiles']}

    variables = {'eq': sym.sympify('h^2/2'),
                 'a': pd.Series([1, 2, 3, 4, 5, 6]),
                 'b': pd.Series([5, 9, 15, 18, 27, 30])}


    class Listener(CreatorListener):
        def notify_about_result_of_main_function(self, result: bool):
            print(result)

    regressor = RegressionConductor(local_settings, Listener(), None)
    regressor.set_variables(variables)
    regressor.perform_functionality()

import os.path
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sympy as sym
from PySide6.QtWidgets import QWidget, QApplication, QDialog, QGridLayout, QPushButton, QCheckBox
from pylatex import NoEscape

from Model.Creators.Creator import Creator
from Model.Creators.CreatorListener import CreatorListener
from Model.SourceFiles.SourceFilesManager import SourceFilesManager
from Model.Variables.VariablesConsumer import VariablesConsumer
from UI.PairInputsDialog import PairInputsDialog
from settings_namespace import BASE_FILES


class PlotInput(PairInputsDialog):
    def __init__(self, parent_widget: QWidget) -> None:
        super().__init__(parent_widget)
        layout: QGridLayout = QGridLayout()
        self.add_pair(0, 'Input output name:', layout)
        self.add_pair(1, 'Input variable of x data:', layout)
        self.add_pair(2, 'Input variable x axis label:', layout)
        self.add_pair(3, 'Input variable of y data:', layout)
        self.add_pair(4, 'Input y axis label:', layout)
        self.add_pair(5, 'Input x errors variable name:', layout)
        self.add_pair(6, 'Input y errors variable name:', layout)
        self.add_pair(7, 'Input variable of regression result:', layout)

        self.include_in_source_check_box: QCheckBox = QCheckBox('Include in source')
        layout.addWidget(self.include_in_source_check_box, 8, 0, 1, 2)

        self.ok_button: QPushButton = QPushButton('OK')
        layout.addWidget(self.ok_button, 9, 0, 1, 2)

        self.setLayout(layout)

        self.ok_button.clicked.connect(self.accept)

    def get_input(self) -> tuple[list[str], bool]:
        return [self.layout().itemAtPosition(i, 1).widget().text() for i in
                range(8)], self.include_in_source_check_box.isChecked()


class PlotCreator(Creator, VariablesConsumer):
    PADDING_COEFFICIENT: float = 0.05
    STYLE: str = 'darkgrid'
    COLOR: str = 'k'
    ECOLOR: str = 'black'
    CAPSIZE: int = 5
    REGRESSION_COLOR: str = 'tab:red'
    TITLE: str = 'plotter'

    def __init__(self, settings: dict[str, str], creator_listener: CreatorListener, parent_widget: QWidget):
        super().__init__(settings, creator_listener, parent_widget)

        self.regression_result_varname: str = ''
        self.y_errors_varname: str = ''
        self.x_errors_varname: str = ''
        self.y_axis_label: str = ''
        self.x_axis_label: str = ''
        self.x_axis_varname: str = ''
        self.y_axis_varname: str = ''
        self.output_name: str = ''
        self.should_include_in_source: bool = False

        self.dialog: PlotInput = PlotInput(self.parent_widget)
        self.getting_result: int = QDialog.Rejected

    def get_title(self) -> str:
        return PlotCreator.TITLE

    def get_use_dialog(self) -> QDialog:
        return self.dialog

    def set_data(self) -> None:
        self.getting_result = self.dialog.exec()
        data_list, self.should_include_in_source = self.dialog.get_input()

        self.output_name = data_list[0]
        self.x_axis_varname = data_list[1]
        self.x_axis_label = data_list[2]
        self.y_axis_varname = data_list[3]
        self.y_axis_label = data_list[4]
        self.x_errors_varname = data_list[5]
        self.y_errors_varname = data_list[6]
        self.regression_result_varname = data_list[7]

    def validate_data(self) -> bool:
        result: bool = True
        result = result and self.output_name != ''
        result = result and self.x_axis_varname in self.variables
        result = result and self.y_axis_varname in self.variables
        result = result and self.x_errors_varname in self.variables
        result = result and self.y_errors_varname in self.variables
        result = result and self.regression_result_varname in self.variables
        return result

    def regression_model(self, parameters: list[float], arguments: np.ndarray) -> np.ndarray:
        a, b = parameters
        return a * arguments + b

    def png_save_name(self):
        return os.path.join(self.settings[BASE_FILES], f'{self.output_name}.png')

    def create_regression_plot(self, x_axis: pd.Series, x_label: str, y_axis: pd.Series, y_label: str,
                               x_errors: pd.Series, y_errors: pd.Series, a_coefficient: float,
                               b_intercept: float = 0) -> str:
        """
        :return: path to created .png file
        """
        plot_frame: pd.DataFrame = pd.DataFrame({x_label: x_axis, y_label: y_axis})
        regression_arguments: np.ndarray = np.linspace(start=min(x_axis) - self.padding,
                                                       stop=max(x_axis) + self.padding,
                                                       num=len(x_axis) + 2 * self.padding)
        regression_values: np.ndarray = self.regression_model(parameters=[a_coefficient, b_intercept],
                                                              arguments=regression_arguments)
        sns.set_theme(style=PlotCreator.STYLE)
        sns.scatterplot(data=plot_frame, x=x_label, y=y_label, color=PlotCreator.COLOR)
        plt.errorbar(data=plot_frame, x=x_label, y=y_label, xerr=x_errors, yerr=y_errors, fmt='none',
                     ecolor=PlotCreator.ECOLOR, capsize=PlotCreator.CAPSIZE)
        plt.plot(regression_arguments, regression_values, color=PlotCreator.REGRESSION_COLOR)
        plt.xlabel(x_label)
        plt.ylabel(y_label)

        save_path: str = self.png_save_name()
        plt.savefig(save_path, bbox_inches='tight')
        return save_path

    def include_plot_in_source(self, base_filepath: str) -> bool:
        table_name: str = os.path.basename(base_filepath).rstrip('.png')
        relative_path: str = f'../{BASE_FILES}/{table_name}'

        include_graphic_command: str = r'\includegraphics[width=0.5\linewidth]{' + relative_path + '}'
        caption: str = r'\caption{' + table_name + '}'
        label: str = r'\label{fig:' + relative_path + '}'

        source_content: str = (f'{NoEscape(r'\begin{figure}[H]')}\n'
                               f'{NoEscape(r'\centering')}\n'
                               f'{NoEscape(include_graphic_command)}\n'
                               f'{NoEscape(caption)}\n'
                               f'{NoEscape(label)}\n'
                               f'{NoEscape(r'end{figure}')}')
        manager: SourceFilesManager = SourceFilesManager(self.settings)
        return manager.save_next_source_file(table_name, source_content)

    @property
    def padding(self) -> int:
        return int(PlotCreator.PADDING_COEFFICIENT * len(self.variables[self.x_axis_varname]))

    def perform_operations(self) -> bool:
        try:
            save_name: str = self.create_regression_plot(
                self.variables[self.x_axis_varname],
                self.x_axis_label,
                self.variables[self.y_axis_varname],
                self.y_axis_label,
                self.variables[self.x_errors_varname],
                self.variables[self.y_errors_varname],
                self.variables[self.regression_result_varname].a_coefficient,
                self.variables[self.regression_result_varname].b_intercept
            )
            if self.should_include_in_source:
                if not self.include_plot_in_source(save_name):
                    return False
            return True
        except Exception:
            return False


if __name__ == '__main__':
    app = QApplication(sys.argv)

    local_settings = {dir_type: f'..\\..\\..\\example\\{dir_type}' for dir_type in
                      ['baseFiles', 'sourceFiles', 'generatedFiles']}

    variables = {'eq': sym.sympify('h^2/2'),
                 'a': pd.Series([1, 2, 3, 4, 5, 6]),
                 'err1': pd.Series([i * 0.1 for i in [1, 2, 3, 4, 5, 6]]),
                 'b': pd.Series([5, 9, 15, 18, 27, 30]),
                 'err2': pd.Series([i * 0.1 for i in [5, 9, 15, 18, 27, 30]])}


    class Listener(CreatorListener):
        def notify_about_result_of_main_function(self, result: bool):
            print(result)


    plotter = PlotCreator(local_settings, Listener(), None)
    plotter.set_variables(variables)
    plotter.output_name = 'png_file'
    plotter.x_axis_varname = 'a'
    a = plotter.create_regression_plot(variables['a'], 'a', variables['b'], 'b', variables['err1'], variables['err2'],
                                       5.2, -0.86666667)
    plotter.include_plot_in_source(a)

    # regressor.set_variables(variables)
    # regressor.perform_functionality()

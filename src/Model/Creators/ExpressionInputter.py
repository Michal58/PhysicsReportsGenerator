import sys
from typing import Any

import sympy as sp
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QCheckBox, QDialog, QApplication, QVBoxLayout, \
    QLineEdit
from sympy import latex

from Model.Creators.Creator import Creator
from Model.Creators.CreatorListener import CreatorListener
from Model.SourceFiles.SourceFilesManager import SourceFilesManager
from Model.Variables.VariablesConsumer import VariablesConsumer
from Model.Variables.variables_namespace import LATEX_SUBSTITUTIONS_VARIABLE
from UI.PairInputsDialog import PairInputsDialog


class ExpressionInputDialog(PairInputsDialog):
    def __init__(self, parent_widget: QWidget) -> None:
        super().__init__(parent_widget)
        layout: QGridLayout = QGridLayout()
        _, self.equation_varname = self.add_pair(0, 'Input variable name of equation: ', layout)
        _, self.expression = self.add_pair(1, 'Input your equation: ', layout)
        self.should_save_into_source_file: QCheckBox = QCheckBox('Save equation in source file')
        self.add_one_element(2, self.should_save_into_source_file, layout)
        self.should_display_in_dialog: QCheckBox = QCheckBox('Display on screen')
        self.add_one_element(3, self.should_display_in_dialog, layout)
        self.should_expand_with_existing_variables: QCheckBox = QCheckBox('Expand equation')
        self.add_one_element(4, self.should_expand_with_existing_variables, layout)

        self.ok_button: QPushButton = QPushButton('OK')
        layout.addWidget(self.ok_button, 5, 0, 1, 2)

        self.ok_button.clicked.connect(self.accept)
        self.setLayout(layout)

    def get_user_input(self) -> tuple[str, str, bool, bool, bool]:
        return (self.equation_varname.text(),
                self.expression.text(),
                self.should_save_into_source_file.isChecked(),
                self.should_display_in_dialog.isChecked(),
                self.should_expand_with_existing_variables.isChecked())


class EquationDisplay(QDialog):
    def __init__(self, parent_widget: QWidget, equation: str) -> None:
        super().__init__(parent_widget)
        self.setWindowTitle('Equation')
        self.setLayout(QVBoxLayout())
        self.display: QLineEdit = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setText(equation)
        self.layout().addWidget(self.display)
        self.ok_button: QPushButton = QPushButton('OK')
        self.ok_button.clicked.connect(self.accept)
        self.layout().addWidget(self.ok_button)


class EquationsChain:
    def __init__(self) -> None:
        self._expressions: list[sp.Expr] = []
        # symbol string representation -> latex replacement
        self._substitutions: dict[str, str] = {}

    def append(self, expression: sp.Expr) -> None:
        self._expressions.append(expression)

    def get_chain(self) -> list[sp.Expr]:
        return self._expressions

    def get_last_expression(self) -> sp.Expr:
        return self._expressions[-1]

    def _build_latex_substitutions(self, expression: sp.Expr) -> dict[sp.Basic, str]:
        symbols: set[sp.Basic] = expression.free_symbols
        return {symbol: self._substitutions[str(symbol)] for symbol in symbols if str(symbol) in self._substitutions}

    def set_substitutions(self, subs: dict[str, str]) -> None:
        self._substitutions = subs

    def __str__(self) -> str:
        return f'${'='.join([latex(expression, symbol_names=self._build_latex_substitutions(expression)) for expression in self._expressions])}$'

    def __repr__(self) -> str:
        return self.__str__()


class ExpressionInputter(Creator, VariablesConsumer):
    """
    Class which purpose is to process user mathematical expressions.
    User can input expression or 'equation - like expression', where first side
    of equation won't be evaluated. After inputting valid to retrieve expression,
    it will be converted into sympy expression, and saved in variable. If user marked option for
    expanding, expression will try to be firstly substituted with available variables,
    and then simplified.
    """

    TITLE: str = 'Equation inputter'

    def __init__(self, settings: dict[str, str], creator_listener: CreatorListener, parent_widget: QWidget):
        super().__init__(settings, creator_listener, parent_widget)
        self.dialog: ExpressionInputDialog = ExpressionInputDialog(self.parent_widget)
        self.getting_status: int = QDialog.Rejected
        self.expression_varname: str = ''
        self.raw_expression: str = ''
        self.should_save_source_file: bool = False
        self.should_display_dialog: bool = False
        self.should_expand_expression: bool = False

    def get_title(self) -> str:
        return ExpressionInputter.TITLE

    def get_use_dialog(self) -> QDialog:
        return self.dialog

    def set_data(self) -> None:
        self.getting_status = self.dialog.exec()
        user_input: tuple[str, str, bool, bool, bool] = self.dialog.get_user_input()
        self.expression_varname = user_input[0]
        self.raw_expression: str = user_input[1]
        self.should_save_source_file = user_input[2]
        self.should_display_dialog = user_input[3]
        self.should_expand_expression = user_input[4]

    def validate_data(self) -> bool:
        result: bool = True
        result = result and self.getting_status == QDialog.Accepted
        result = result and self.expression_varname != '' and self.expression_varname not in self.variables
        result = result and self.raw_expression != ''
        return result

    def expand_expression(self, equations: EquationsChain) -> None:
        last_expression: sp.Expr = equations.get_last_expression()
        if last_expression.is_Number:
            return

        def simplification(value: float) -> float | int:
            return int(value) if value.is_integer() else value

        symbols_of_expression: set[sp.Basic] = last_expression.free_symbols
        symbols_substitutions: list[tuple[str, float]] = [(str(symbol), simplification(self.variables[str(symbol)]))
                                                          for symbol in symbols_of_expression
                                                          if str(symbol) in self.variables]
        with sp.evaluate(False):
            intermediate_expression: sp.Expr = last_expression.subs(symbols_substitutions)
            equations.append(intermediate_expression)
            if intermediate_expression.is_Number:
                return

        final_expression: sp.Expr = intermediate_expression.simplify()
        equations.append(final_expression)

    def equations_to_source_file(self, equations: EquationsChain) -> bool:
        source_files_manager: SourceFilesManager = SourceFilesManager(self.settings)
        return source_files_manager.save_next_source_file(self.expression_varname, str(equations))

    def display_equation(self, equation: EquationsChain) -> None:
        EquationDisplay(self.parent_widget, str(equation)).exec()

    def perform_operations(self) -> bool:
        try:
            expressions: list[str] = self.raw_expression.split('=')
            if len(expressions) > 2:
                return False

            equation_chain: EquationsChain = EquationsChain()
            if LATEX_SUBSTITUTIONS_VARIABLE in self.variables:
                equation_chain.set_substitutions(self.variables[LATEX_SUBSTITUTIONS_VARIABLE])

            for expression in expressions:
                converted_expression: sp.Expr = sp.sympify(expression, evaluate=False)
                equation_chain.append(converted_expression)

            self.variables[self.expression_varname] = equation_chain

            if self.should_expand_expression:
                self.expand_expression(equation_chain)

            if self.should_save_source_file:
                if not self.equations_to_source_file(equation_chain):
                    return False

            if self.should_display_dialog:
                self.display_equation(equation_chain)

            return True

        except (sp.SympifyError, ValueError):
            return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    local_settings = {dir_type: f'..\\..\\..\\example\\{dir_type}' for dir_type in
                      ['baseFiles', 'sourceFiles', 'generatedFiles']}

    variables = {'v1': sp.latex(sp.sympify('h^2/2'), mode='inline'), 'v2': 45, 'v3': 'another text',
                 'v4': ' made_space ', 'a': 45, 'b': 7, LATEX_SUBSTITUTIONS_VARIABLE: {'b': r'\lambda'}}


    class Listener(CreatorListener):
        def notify_about_result_of_main_function(self, result: bool):
            print(result)


    intro_vars = ExpressionInputter(local_settings, Listener(), None)
    intro_vars.set_variables(variables)
    intro_vars.perform_functionality()
    print(variables)

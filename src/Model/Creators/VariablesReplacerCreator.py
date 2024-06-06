import re
import sys

import sympy as sym

from Model.SourceFiles.SourceFile import SourceFile
from Model.Variables.variables_namespace import VAR_COMMAND_FORMAT

from PySide6.QtWidgets import QWidget, QFileDialog, QDialog, QApplication

from Model.Creators.Creator import Creator
from Model.Creators.CreatorListener import CreatorListener
from Model.Variables.VariablesConsumer import VariablesConsumer
from settings_namespace import SOURCE_FILES, ENCODING


class VariablesReplacerCreator(Creator, VariablesConsumer):
    TITLE: str = 'Variables replacer'

    def __init__(self, settings: dict[str, str], creator_listener: CreatorListener, parent_widget: QWidget) -> None:
        super().__init__(settings, creator_listener, parent_widget)
        self.dialog_for_files_to_replace: QFileDialog = QFileDialog(self.parent_widget)
        self.files_to_replace: list[str] = []

    def get_title(self) -> str:
        return VariablesReplacerCreator.TITLE

    def get_use_dialog(self) -> QDialog:
        return self.dialog_for_files_to_replace

    def set_data(self) -> None:
        options = QFileDialog.Options()
        self.files_to_replace, _ = self.dialog_for_files_to_replace.getOpenFileNames(
            self.dialog_for_files_to_replace.parent(), 'Replace variables', self.settings[SOURCE_FILES],
            "TeX Files (*.tex)", options=options)

    def validate_data(self) -> bool:
        return len(self.files_to_replace) > 0

    def _replacement(self, matched_text: re.Match) -> str:
        if matched_text.group(1) is not None:
            return str(self.variables[matched_text.group(1)])
        else:
            return f'{matched_text.group(2)}{str(self.variables[matched_text.group(3)])}'

    def _replace_variables_in_text(self, text: str) -> str:
        return re.sub(pattern=VAR_COMMAND_FORMAT, repl=self._replacement, string=text)

    def _validate_variables_names(self, text: str) -> bool:
        for matched_text in re.finditer(VAR_COMMAND_FORMAT, text):
            if matched_text.group(1) is not None:
                if matched_text.group(1) not in self.variables:
                    return False
            elif matched_text.group(3) not in self.variables:
                return False
        return True

    def perform_operations(self) -> bool:
        # we replace all variables or none
        for filepath in self.files_to_replace:
            source_instance: SourceFile=SourceFile(filepath)
            success_info, text_to_replace = source_instance.read_content_of_file()
            if not (success_info and self._validate_variables_names(text_to_replace)):
                return False
            replaced_text: str = self._replace_variables_in_text(text_to_replace)
            if not source_instance.save_content_to_file(replaced_text):
                return False
        return True


if __name__ == '__main__':
    local_settings = {dir_type: f'..\\..\\..\\example\\{dir_type}' for dir_type in
                      ['baseFiles', 'sourceFiles', 'generatedFiles']}

    variables = {'v1': sym.latex(sym.sympify('h^2/2'), mode='inline'), 'v2': 45, 'v3': 'another text', 'v4': ' made_space '}


    class Listener(CreatorListener):
        def notify_about_result_of_main_function(self, result: bool):
            print(result)


    app = QApplication(sys.argv)
    intro_vars = VariablesReplacerCreator(local_settings, Listener(), None)
    intro_vars.set_variables(variables)
    intro_vars.perform_functionality()
    print(variables)

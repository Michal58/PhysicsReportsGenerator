import importlib.util
import os.path
import sys
import sympy as sym

from PySide6.QtWidgets import QDialog, QFileDialog, QApplication, QWidget

from Model.Creators.Creator import Creator
from Model.Creators.CreatorListener import CreatorListener
from Model.Variables.VariablesConsumer import VariablesConsumer
from settings_namespace import BASE_FILES


class OperateVariablesCreator(Creator, VariablesConsumer):
    TITLE: str = 'Variables operator'
    RUN_FUNCTION: str = 'run'

    def __init__(self, settings: dict[str, str], creator_listener: CreatorListener, parent_widget: QWidget):
        super().__init__(settings, creator_listener, parent_widget)
        self.script_path: str = ''
        self.script_dialog = QFileDialog(self.parent_widget)

    def get_title(self) -> str:
        return OperateVariablesCreator.TITLE

    def get_use_dialog(self) -> QDialog:
        return self.script_dialog

    def set_data(self) -> None:
        options = QFileDialog.Options()
        self.script_path, _ = self.script_dialog.getOpenFileName(self.script_dialog.parent(), "Select .py script",
                                                                 self.settings[BASE_FILES], "Python Files (*.py)",
                                                                 options=options)

    def validate_data(self) -> bool:
        return self.script_path != ''

    def perform_operations(self) -> bool:
        try:
            module_name = os.path.basename(self.script_path)
            spec = importlib.util.spec_from_file_location(module_name, self.script_path)
            script = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(script)
            if hasattr(script, OperateVariablesCreator.RUN_FUNCTION):
                script.run(self.variables)
                return True
            else:
                return False
        except Exception:
            return False


if __name__ == '__main__':
    local_settings = {dir_type: f'..\\..\\..\\example\\{dir_type}' for dir_type in
                      ['baseFiles', 'sourceFiles', 'generatedFiles']}

    variables = {'eq': sym.sympify('h^2/2')}


    class Listener(CreatorListener):
        def notify_about_result_of_main_function(self, result: bool):
            print(result)


    app = QApplication(sys.argv)
    intro_vars = OperateVariablesCreator(local_settings, Listener(), None)
    intro_vars.set_variables(variables)
    intro_vars.perform_functionality()
    print(variables)

import importlib.util
import os
from importlib.machinery import ModuleSpec
from types import ModuleType


def path_to_module(module_path: str) -> ModuleType:
    module_name: str = os.path.basename(module_path)
    spec: ModuleSpec = importlib.util.spec_from_file_location(module_name, module_path)
    script: ModuleType = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)
    return script

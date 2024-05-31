import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# from Model.Opening.ProjectCreator import main_function
from src.Controller.MainController import main_function

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
    sys.path.append(parent_dir)
    # main_function()
    main_function()

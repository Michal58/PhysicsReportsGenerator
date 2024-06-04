import os.path


def get_documentation_text():
    with open(os.path.join(os.path.dirname(__file__), 'Documentation.txt'), 'r') as file:
        return file.read()

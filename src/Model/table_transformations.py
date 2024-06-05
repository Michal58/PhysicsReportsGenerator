import pandas as pd
import sympy as sym


def round_up(data_frame: pd.DataFrame, column: str, offset: int):
    data_frame[column] = data_frame[column].apply(lambda element: int(element * 10 ** offset) / 10 ** offset)


def create_device_errors(new_label: str, data_frame: pd.DataFrame, column: str, percent_coeff: float, const_exp: float):
    data_frame[new_label] = data_frame[column].apply(lambda element: percent_coeff * element + const_exp)


def create_equation(str_expr:str):
    return sym.sympify(str_expr)

if __name__ == '__main__':
    pass

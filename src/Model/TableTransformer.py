import pandas as pd
import sympy as sym


class TableTransformer:
    """
    Purpose of class is to use it as wrapper on certain data table and
    refactor it within its methods, so table transformer operates only on one DataFrame
    """
    def __init__(self,data_frame:pd.DataFrame):
        self.frame: pd.DataFrame=data_frame  # frame will be frequently using, so I want to keep its name short

    def round_up(self,data_frame: pd.DataFrame, column: str, offset: int):
        data_frame[column] = data_frame[column].apply(lambda element: int(element * 10 ** offset) / 10 ** offset)


    def create_device_errors(new_label: str, data_frame: pd.DataFrame, column: str, percent_coeff: float, const_exp: float):
        data_frame[new_label] = data_frame[column].apply(lambda element: percent_coeff * element + const_exp)


    def create_equation(self,str_expr: str):
        return sym.sympify(str_expr)

if __name__ == '__main__':
    pass

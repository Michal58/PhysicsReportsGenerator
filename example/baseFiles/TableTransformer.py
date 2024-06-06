import pandas as pd


class TableTransformer:
    """
    Purpose of class is to use it as wrapper on certain data table and
    refactor it within its methods, so table transformer operates only on one DataFrame
    """

    def __init__(self, data_frame: pd.DataFrame):
        self.frame: pd.DataFrame = data_frame  # frame will be frequently using, so I want to keep its name short

    @staticmethod
    def round_up(element, offset: int) -> float:
        return int(element * 10 ** offset) / 10 ** offset

    def rounds_up(self, column: str, offset: int) -> None:
        self.frame[column] = self.frame[column].apply(lambda element: TableTransformer.round_up(element, offset))

    @staticmethod
    def device_error(element, percent_coefficient: float, const_exp: float) -> float:
        return percent_coefficient / 100 * element + const_exp

    def create_device_errors(self, new_label: str, source_column: str, percent_coefficient: float,
                             const_exp: float) -> None:
        self.frame[new_label] = self.frame[source_column].apply(
            lambda element: TableTransformer.device_error(element, percent_coefficient, const_exp))

    def return_frame(self) -> pd.DataFrame:
        return self.frame


if __name__ == '__main__':
    pass

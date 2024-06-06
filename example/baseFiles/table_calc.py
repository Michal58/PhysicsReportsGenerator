import sys
from typing import Any

import pandas as pd
from src.Model.TableTransformer import TableTransformer

columns = [r'$\epsilon$[V]', 'U[V]', 'u(U)[V]', 'I[A]', 'u(I)[A]']


def run(variables: dict[str, Any]):
    xerr = pd.Series([])
    yerr = pd.Series([])

    variables['xerr'] = xerr
    variables['yerr'] = yerr


def calc(data_frame: pd.DataFrame) -> pd.DataFrame:
    transformer: TableTransformer = TableTransformer(data_frame)
    transformer.create_device_errors('u(U)[V]', 'U[V]', 0.3, 0.01)
    transformer.rounds_up('u(U)[V]', 3)
    transformer.create_device_errors('u(I)[A]', 'I[A]', 1.2, 0.0001)

    return transformer.return_frame()


def transform(data_frame: pd.DataFrame) -> pd.DataFrame:
    transformer: TableTransformer = TableTransformer(data_frame)
    transformer.rounds_up('u(I)[A]',3)
    return transformer.return_frame()

if __name__ == '__main__':
    pass

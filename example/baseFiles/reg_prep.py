from typing import Any

import pandas as pd


def run(variables: dict[str, Any]):
    frame:pd.DataFrame=variables['Results']

    data_col=frame['U[V]']
    to_pred_col=frame['I[A]']

    variables['data']=data_col
    variables['pred']=to_pred_col

    xerr = frame['u(U)[V]']
    yerr = frame['u(I)[A]']

    variables['xerr'] = xerr
    variables['yerr'] = yerr
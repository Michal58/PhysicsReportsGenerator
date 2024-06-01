from typing import Any


def run(variables:dict[str,Any]):
    eq=variables['eq']
    variables['eval']=eq.subs('h', 5)

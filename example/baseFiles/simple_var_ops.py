from typing import Any
import sympy as sym


def run(variables:dict[str,Any]):
    print(variables)
    variables['eq']=sym.sympify('h^2/2')
    eq=variables['eq']
    variables['eval']=eq.subs('h', 5)

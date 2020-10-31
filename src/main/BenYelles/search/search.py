from .types import *
from typing import Optional
import itertools


def check_return_type(func_type: Type, return_type: Type) -> Optional[int]:
    if not isinstance(func_type, Function):
        if func_type == return_type and type(return_type) == type(func_type):
            return 0
        return None

    if func_type == return_type:
        return 0

    curry_func = func_type.curry()

    depth = check_return_type(curry_func, return_type)

    if depth is None:
        return None

    return 1 + depth


def recursive_search(cntx: dict,
                     inh_type: Type,
                     visited={}) -> list:  # secretly is a dfs

    if (cntx, inh_type) in visited:
        return visited[(cntx, inh_type)]
    terms = []

    visited[(cntx, inh_type)] = [".. " + str(inh_type) + " .."]

    for (name, cntx_type) in cntx.items():

        depth = check_return_type(cntx_type, inh_type)

        if depth is None:
            continue

        if depth == 0:
            terms.append(name)
            continue

        new_types_to_inh = cntx_type[:depth]
        results = []
        for new_type in new_types_to_inh:
            new_terms = recursive_search(cntx, new_type, visited)
            if new_terms:
                results.append(new_terms)

        for args in itertools.product(*results):
            terms.append(
                "(" + " ".join([name, *args]) + ")"
            )

    visited[(cntx, inh_type)] = terms
    return terms


# def another_recursive_search(cntx: dict,
#                              inh_type: Type):
#
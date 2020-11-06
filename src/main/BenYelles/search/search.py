from .types import *
from typing import Optional
import itertools


def check_return_type(cur_type: Type, return_type: Type) -> Optional[int]:
    if not isinstance(cur_type, Function):
        if cur_type == return_type and type(return_type) == type(cur_type):
            return 0
        return None

    if do_types_match(cur_type, return_type):
        return 0

    curry_func = cur_type.curry()

    depth = check_return_type(curry_func, return_type)

    if depth is None:
        return None

    return 1 + depth


def recursive_search(cntx: Context,
                     inh_type: Type,
                     visited={}) -> list:  # secretly is a dfs

    if (cntx, inh_type) in visited:
        return visited[(cntx, inh_type)]
    terms = []

    visited[(cntx, inh_type)] = [".. " + str(inh_type) + " .."]
    polluted_cntx = cntx.inst_return_types(inh_type)
    for (name, cntx_type) in polluted_cntx.items():

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


def check_vars(var_cntx: frozendict,
               inh_type: Type):
    terms = []
    for item in var_cntx:
        (var_name, var_type) = item
        if type(var_type) is PolType:
            raise RuntimeError("variable can't be polyporphic")

        if var_type == inh_type:
            terms.append(var_name)

    return terms


def do_types_match(term1, term2):
    if type(term1) is PolType or type(term2) is PolType:  # if one of them is polymorphic then they match
        return True

    if type(term1) != type(term2):  # if none of them are polymorphic and terms have different "types" the do not match
        return False

    if type(term1) is Type or type(term1) is Tuple:  # if terms are variables they must have same type
        return term1 == term2

    if type(term1) is Function:  # if they are functions check types of their arguments and their return types
        if len(term1) != len(term2):
            return False

        def check_sigs(term1, term2):
            for idx, sub_term in enumerate(term1):
                for dual_idx, dual_sub_term in enumerate(term1):
                    if sub_term == dual_sub_term and term2[idx] != term2[dual_idx]:
                        return False
            return True

        if not check_sigs(term1, term2):
            return False

        # here must be check that same types in term1 match same types in term2
        for arg_type1, arg_type2 in zip(term1, term2):
            if not do_types_match(arg_type1, arg_type2):
                return False

        return True

    return False


def check_functons(func_cntx: frozendict,
                   inh_type: Type):
    pass


def another_recursive_search(cntx: frozendict,
                             inh_type: Type):
    pass

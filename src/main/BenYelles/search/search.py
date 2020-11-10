from .types import *
from typing import List, Dict, Set


def recursive_search(cntx: Context, tgt_type: Type):
    filtered_cntx = cntx.filter_by_return_type(tgt_type)
    good_terms: Set[str] = set(cntx.filter_by_type(tgt_type).keys())
    terms_to_inh: Dict[str, List] = {}
    inh_terms = {}
    for (term_name, term_type) in filtered_cntx.items():
        terms_to_inh[term_name] = [recursive_search(cntx, tt) for tt in term_type[:-1]]
        inh_terms[term_name] = [set() for _ in terms_to_inh[term_name]]

    yield good_terms

    while True:
        for term_name in terms_to_inh:
            new_arguments = [next(searcher) for searcher in terms_to_inh[term_name]]
            old_arguments = inh_terms[term_name]
            all_arguments = [old | new for new, old in zip(new_arguments, old_arguments)]
            inh_terms[term_name] = all_arguments
            all_functions = itertools.product({term_name}, *all_arguments)
            new_good_terms = {"(" + " ".join(func) + ")" for func in all_functions}
            good_terms |= new_good_terms

        yield good_terms
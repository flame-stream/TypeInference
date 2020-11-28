from .types import *
from typing import List, Dict, Set


def recursive_search(cntx: Context, tgt_type: Type, ext):
    """
    This function preforms lazy search through the possible terms
     for them to have desired type "tgt_type"

    First of all check all terms in context "cnxt" and pick all of them which have desired type.
    Then get new context "filtered context" with functions which are returning desired type
    """

    # cntx with only variables which have desired type
    filtered_cntx = cntx.filter_by_return_type(tgt_type, ext)
    # accumulator to store terms with desired type
    good_terms: Set[str] = set(cntx.filter_by_type(tgt_type, ext).keys())
    terms_to_inh: Dict[str, List] = {}
    inh_terms = {}
    """
    For each such function for each of its argument initialize same recursive search in lazy way.
    """
    for (term_name, term_type) in filtered_cntx.items():
        terms_to_inh[term_name] = [recursive_search(cntx, tt, ext) for tt in term_type[:-1]]
        inh_terms[term_name] = [set() for _ in terms_to_inh[term_name]]

    """
    Return good terms that were picked from context.
    """
    yield good_terms

    """
    Until the end of the world preform one lazy step on each of those lazy seaches
     that are initialized on each of function's argument. 
     
    
    update sets of available arguments and for each function
    each element of Cartesian product of sets of arguments is
    the term we are searching for.
    
    Let here be an example:
        we are inhabitating type A. And the only function we have is h :: B -> C -> A.
        There some other terms is context: M_1 :: B, M_2 :: B, N_1 :: C, N_2 :: C, N_3 :: C
        
        after the search there will be sets of arguments for function h:
            arg1 = {M_1, M_2} for the first argument
            arg2 = {N_1, N_2, N_3} for the second argument
            then set of all terms that are inhabitating type A in given context are:
                {h} x arg1 x arg2 = {(h, M_1, N_1), (h, M_1, N_2), ..., (h, M_2, N_3)}
            where "x" denotes a Cartesian product.
            
    """
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

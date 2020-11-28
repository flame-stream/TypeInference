import sys
import re

sys.path.append("../../main/")

import BenYelles


def remove_mangling(name):
    # return name
    man = re.compile("__.*?__")
    return man.sub("", name)


if __name__ == '__main__':
    with open("cntx.hs", 'r') as input_stream:
        cntx, ext = BenYelles.hasell_sig_parser(input_stream)

    with open("inh.hs", 'r') as input_stream:
        inh, _ = BenYelles.hasell_sig_parser(input_stream)

    print(f"context: {cntx}")
    print(f"to inhabitate: {inh}")
    type_to_inh = list(inh.values())[0]
    inhabitants_searcher = BenYelles.recursive_search(cntx, type_to_inh, ext)
    aggr = set()
    while input("continue? [y]"):
        cur_aggr = next(inhabitants_searcher)
        cur_aggr = {remove_mangling(name) for name in cur_aggr}
        for inh in cur_aggr.difference(aggr):
            print(inh, "::", type_to_inh)

        aggr |= cur_aggr

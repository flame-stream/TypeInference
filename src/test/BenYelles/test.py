import sys

sys.path.append("../../main/")

import BenYelles

if __name__ == '__main__':
    with open("cntx.hs", 'r') as input_stream:
        cntx = BenYelles.hasell_sig_parser(input_stream)

    with open("inh.hs", 'r') as input_stream:
        inh = BenYelles.hasell_sig_parser(input_stream)

    print(cntx)
    print(inh)
    type_to_inh = list(inh.values())[0]
    inhbitants = BenYelles.recursive_search(cntx, type_to_inh)
    for inh in inhbitants:
        print(inh, "::", type_to_inh)

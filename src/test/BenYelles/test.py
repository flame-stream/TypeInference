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
    # print("inst return type:")
    # print("-- id:", cntx["id"].inst_return_type('Int'))
    # print("-- id:", cntx["id"].inst_return_type('Float'))
    # print("-- k:", cntx["k"].inst_return_type('Float'))
    # print("do k' and k match?:", BenYelles.do_types_match(cntx["k"], cntx["k'"]))
    inhbitants = BenYelles.recursive_search(cntx, type_to_inh)
    for inh in inhbitants:
        print(inh, "::", type_to_inh)

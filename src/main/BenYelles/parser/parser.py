from lark import Lark, Transformer
from ..search.types import *

# this parser spec is for parsing haskell-like signatures without polymorphic types

haskell_sigs = r"""
        ?signature: func_name "::" ( arrowtype | type )

        type_name: /[A-Z][A-Za-z0-9\'_]*/
        func_name: /[a-z][A-Za-z0-9\'_]*/

        arrowtype: (type "->")+ type
        tuple: "(" ((type | arrowtype) ",")+ (type | arrowtype) ")"

        type:  type_name | tuple | "(" arrowtype ")"

        // %ignore "--" (/[^\n]*/)+ "\n"

        %import common.WS
        %ignore WS



        """

# this parser spec is for parsing haskell-like signatures with polymorphic types

haskell_pol_sigs = r"""
        ?signature: func_name "::" ( arrowtype | type )

        type_name: /[A-Z][A-Za-z0-9\'_]*/
        func_name: /[a-z][A-Za-z0-9\'_]*/
        pol_type_name: /[a-z][A-Za-z0-9\'_]*/

        pol_type: pol_type_name
        arrowtype: (type "->")+ type
        // tuple: "(" ((type | arrowtype) ",")+ (type | arrowtype) ")"

        // type:  type_name | pol_type | tuple | "(" arrowtype ")"

        type:  type_name | pol_type | "(" arrowtype ")"

        // %ignore "--" (/[^\n]*/)+ "\n"

        %import common.WS
        %ignore WS



        """


class TreeToContext(Transformer):
    """ see lark example in its documentation this thing is straight from there"""

    def signature(self, sig):
        return {
            str(sig[0]): sig[1]
        }

    def func_name(self, s):
        (s,) = s
        return s

    def type_name(self, s):
        (s,) = s
        return SimpleType((str(s),))

    def pol_type_name(self, s):
        (s,) = s
        return s

    def pol_type(self, s):
        (s,) = s
        return PolType((str(s),))

    # def tuple(self, types):
    #     return Tuple(types)

    def arrowtype(self, types):
        return Function(types)

    def type(self, typename):
        typename, = typename
        return typename


def hasell_sig_parser(stream):
    """
    :param stream: steam probably from som *.hs file with signatures
    :return: context object with function signatures wrapped with type classes from types.py
    """
    haskell_signature_parser = Lark(haskell_pol_sigs, start='signature')  # parser creating
    cntx = Context()
    for line in stream:
        if "::" not in line:  # weak checker for if there is signature in line
            continue
        if line[:2] == "--":  # yep this is for comments
            continue

        parsed_line = haskell_signature_parser.parse(line)
        print(parsed_line.pretty())
        signature = TreeToContext().transform(parsed_line)
        cntx = cntx.update(signature)

    return cntx
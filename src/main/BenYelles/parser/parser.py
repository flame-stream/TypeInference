from lark import Lark, Transformer
from ..search.types import *
from frozendict import frozendict

haskell_sigs = r"""
        ?signature: name "::" ( arrowtype | typename )
        
        name: /[A-Za-z][A-Za-z0-9\'_]*/
        
        arrowtype: (typename "->")+ typename
        tuple: "(" ((typename | arrowtype) ",")+ (typename | arrowtype) ")"
        typename:  name | tuple | "(" arrowtype ")"
        
        // %ignore "--" (/[^\n]*/)+ "\n"
        
        %import common.WS
        %ignore WS
        
        
        
        """


class TreeToContext(Transformer):
    def signature(self, sig):
        return {
            str(sig[0]): sig[1]
        }

    def name(self, s):
        (s,) = s
        return Type((str(s),))

    def tuple(self, types):
        return Tuple(types)

    def arrowtype(self, types):
        return Function(types)

    def typename(self, typename):
        typename, = typename
        return typename


class Context(frozendict):
    def update(self, anther_dict: Union[frozendict, dict]):
        return self.copy(**anther_dict)


def hasell_sig_parser(stream):
    haskell_signature_parser = Lark(haskell_sigs, start='signature')
    cntx = Context()
    for line in stream:
        if "::" not in line:
            continue
        if line[:2] == "--":
            continue

        parsed_line = haskell_signature_parser.parse(line)
        # print(parsed_line.pretty())
        signature = TreeToContext().transform(parsed_line)
        cntx = cntx.update(signature)

    return cntx

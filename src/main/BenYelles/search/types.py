from typing import NoReturn, Sized, Tuple, Union, Any, Optional, List
from frozendict import frozendict
import itertools
from copy import copy
from abc import ABC, abstractmethod


class Type(ABC, tuple):
    @abstractmethod
    def is_inhabitant_of(self, tgt_type) -> bool:
        pass


class VoidType(Type):

    def is_inhabitant_of(self, tgt_type) -> bool:
        return False


class SimpleType(Type):

    def is_inhabitant_of(self, tgt_type) -> bool:
        if type(tgt_type) is PolType:
            return True

        if type(tgt_type) is not SimpleType:
            return False

        return self == tgt_type

    def __new__(cls, seq: Sized):
        if len(seq) != 1:
            raise RuntimeError(f"Illegal type construction from {seq}")
        return super(SimpleType, cls).__new__(cls, seq)

    def __str__(self):
        return str(self[0])

    def __repr__(self):
        return self.__str__()


class PolType(Type):
    def is_inhabitant_of(self, tgt_type) -> bool:
        return type(tgt_type) is PolType

    def __new__(cls, seq: Sized):
        if len(seq) != 1:
            raise RuntimeError(f"Illegal polymorphic type construction from {seq}")
        return super(PolType, cls).__new__(cls, seq)

    def __str__(self):
        return str(self[0])

    def __repr__(self):
        return self.__str__()


class Function(Type):
    def is_inhabitant_of(self, tgt_type) -> bool:

        if isinstance(tgt_type, PolType):
            return True

        if not isinstance(tgt_type, Function):
            return False

        forced_type = []
        cur_tgt_type = copy(tgt_type)
        cur_cnd_type = copy(self)
        while isinstance(cur_cnd_type, Function) and isinstance(cur_tgt_type, Function):

            if not cur_cnd_type[0].is_inhabitant_of(tgt_type[0]):
                return False

            forced_type.append(cur_cnd_type[0])

            cur_tgt_type = cur_tgt_type.curry()
            cur_cnd_type = cur_cnd_type.curry()

        # one of them is not a function now

        if not cur_cnd_type.is_inhabitant_of(cur_tgt_type):
            return False

        forced_type.append(cur_cnd_type)

        for (idx1, one), (idx2, dual) in itertools.product(enumerate(tgt_type), enumerate(tgt_type)):
            if idx1 >= len(forced_type):
                return False
            if idx2 >= len(forced_type):
                return False
            forced_one = forced_type[idx1]
            forced_dual = forced_type[idx2]
            if one == dual and forced_one != forced_dual:
                return False

        return True

    def __new__(cls, seq: Sized):
        if len(seq) < 2:
            raise RuntimeError(f"Function can't have zero arguments: {seq}")
        return super(Function, cls).__new__(cls, seq)

    def curry(self) -> Type:
        if len(self) > 2:
            curried: Function = self[1:]
            return Function(curried)
        return_type: Union[Function, Tuple, SimpleType] = self[1]
        return return_type

    def args_to_return(self, t: Type) -> List[int]:  # how many args to pass for it to return t
        if isinstance(t, PolType):
            return list(range(1, len(self)))

        if self.is_inhabitant_of(t):
            return []

        curr_func = copy(self)
        depth = 0

        while isinstance(curr_func, Function):
            curr_func = curr_func.curry()
            depth += 1
            if curr_func.is_inhabitant_of(t):
                return [depth]

        return []

    def force_return_type(self, return_type: Type):
        arities = self.args_to_return(return_type)
        if len(arities) == 0:
            return []
        if len(self) == 2:
            return [copy(self)]

        curried_funcs = []
        for arity in arities:
            if arity == len(self) - 1:
                curried_funcs.append(copy(self))
                continue

            curried_funcs.append(
                Function(
                    (
                        *self[:arity], Function(self[arity:])
                    )
                )
            )

        return curried_funcs

    def __str__(self):
        rep = ""
        for t in self[:-1]:
            rep += str(t) + " -> "

        rep += str(self[-1])
        return rep

    def __repr__(self):
        return self.__str__()


class Context(frozendict):
    def __str__(self):
        return "{" + ",\n".join([f"\'{key}\': {value}" for (key, value) in self.items()]) + "}"

    def __repr__(self):
        return self.__str__()

    def update(self, anther_dict: Union[frozendict, dict]):
        return self.copy(**anther_dict)

    def split(self):
        funcs = {}
        vars = {}
        for item in self.items():
            (_name, _type) = item
            if type(item) is SimpleType:
                vars[_name] = _type
            else:
                funcs[_name] = _type

        return frozendict(vars), frozendict(funcs)

    def force_return_types(self, t: Type):
        res = {}
        for item in self.items():
            (term_name, term_type) = item
            if isinstance(term_type, Function):
                curried_funcs = term_type.force_return_type(t)
                for i, curried_func in enumerate(curried_funcs):
                    res[term_name + "__" + str(i) + "__"] = curried_func
            else:
                res[term_name] = term_type

        return frozendict(res)

    def filter_by_return_type(self, t: Type):
        res_cntx = self.force_return_types(t)
        res = {}
        for item in res_cntx.items():
            (term_name, term_type) = item
            if isinstance(term_type, Function):
                if term_type[-1].is_inhabitant_of(t):
                    res[term_name] = term_type

        return Context(res)

    def filter_by_type(self, t: Type):
        if isinstance(t, PolType):
            return copy(self)

        res = {}
        for item in self.items():
            (term_name, term_type) = item
            if term_type.is_inhabitant_of(t):
                res[term_name] = term_type

        return Context(res)

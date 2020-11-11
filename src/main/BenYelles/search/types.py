from typing import NoReturn, Sized, Tuple, Union, Any, Optional, List
from frozendict import frozendict
import itertools
from copy import copy
from abc import ABC, abstractmethod


class Type(ABC, tuple):
    """
    abstract class for types.
    Provides interface for checking the inhabitation relation of any two types
    """

    @abstractmethod
    def is_inhabitant_of(self, tgt_type) -> bool:
        pass


class VoidType(Type):
    """
    Void type with no inhabitants.
    """

    def is_inhabitant_of(self, tgt_type) -> bool:
        return False


class SimpleType(Type):
    """
    Types from simply typed lambda calculus.
    """

    def is_inhabitant_of(self, tgt_type) -> bool:
        """
            Simple type is inhabitant of any polymorphic type
            Simple type is inhabitant of any simple type with same name
        """
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
    """
    Polymorphic type from System F.
    """

    def is_inhabitant_of(self, tgt_type: Type) -> bool:
        """
        Polymorphic type is inhabitant only of another polymorphic type
        """
        return isinstance(tgt_type, PolType)

    def __new__(cls, seq: Sized):
        if len(seq) != 1:
            raise RuntimeError(f"Illegal polymorphic type construction from {seq}")
        return super(PolType, cls).__new__(cls, seq)

    def __str__(self):
        return str(self[0])

    def __repr__(self):
        return self.__str__()


class Function(Type):
    """
    Function type from System F.
    """

    def is_inhabitant_of(self, tgt_type: Type) -> bool:

        """
        Function is an inhabitant of any polymorphic type
        Function is an inhabitant of function if their signatures "match"
        """

        if isinstance(tgt_type, PolType):
            return True

        if not isinstance(tgt_type, Function):
            return False

        """
        The main problem here is situation when in self and in tgt type there are some
        polymorphic types, some simple types and some function types. Each type of self must be
        inhabitant of corresponding type in tgt type. Corresponding in terms of currying:
            if first type of self is inhabitant of first in tgt_type, then curry and check again: 
        """
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

        """
            If everything checks, than check that same polymorphic type in different places of signature
            matches same types in corresponding signature:
            
        """

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
        """
        Currying. It is possible to curry A -> B, but then the result will no longer be function.
        """
        if len(self) > 2:
            curried: Function = self[1:]
            return Function(curried)
        return_type: Union[Function, Tuple, SimpleType] = self[1]
        return return_type

    def args_to_return(self, t: Type) -> List[int]:  # how many args to pass for it to return t
        """
        Function to check how many currying operations
        need to be done with self, for it to return desired type "t".
        Note that if "t" is polymorphic all curring operations are producing desired type "t".
        """
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
        """
        If function is returning polymorphic type then change all its occurrences
        in signature to desired type "return type".
        If there are multiple ways to do it then return all of them.
        It is relevant when it is desired for function to return polymorphic type
        """
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
    """
    Structure that stores pairs of function name and corresponding signature
    """

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
        """
        for each function force the return type. If this operation is spawning new functions
        then apply mangling and store them all.
        """
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
        """
        return a copy of the context with only those functions that return desired type "t"
        """
        res_cntx = self.force_return_types(t)
        res = {}
        for item in res_cntx.items():
            (term_name, term_type) = item
            if isinstance(term_type, Function):
                if term_type[-1].is_inhabitant_of(t):
                    res[term_name] = term_type

        return Context(res)

    def filter_by_type(self, t: Type):
        """
        return a copy of the context with only those variables that have desired type "t"
        """
        if isinstance(t, PolType):
            return copy(self)

        res = {}
        for item in self.items():
            (term_name, term_type) = item
            if term_type.is_inhabitant_of(t):
                res[term_name] = term_type

        return Context(res)

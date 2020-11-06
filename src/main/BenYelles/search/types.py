from typing import Iterable, Sized, Union
from frozendict import frozendict


class Type(tuple):
    def __new__(cls, seq: Iterable):
        return super(Type, cls).__new__(cls, seq)

    def __str__(self):
        return str(self[0])

    def __repr__(self):
        return self.__str__()


class PolType(Type):
    def __new__(cls, seq: Sized):
        return super(Type, cls).__new__(cls, seq)

    def __str__(self):
        return str(self[0]) + '\''

    def __repr__(self):
        return self.__str__()


class Function(Type):
    def __new__(cls, seq: Sized):
        if len(seq) < 2:
            raise RuntimeError("Function can't have zero arguments")
        return super(Type, cls).__new__(cls, seq)

    def curry(self):
        if len(self) > 2:
            curried: Function = self[1:]
            return Function(curried)
        return_type: Union[Function, Tuple, Type] = self[1]
        return return_type

    def inst_return_type(self, inst_type):
        ret_type = self[-1]
        if type(ret_type) is not PolType:
            return self

        inst_function = []
        for var_type in self:
            if var_type == ret_type:
                inst_function.append(inst_type)
            else:
                inst_function.append(var_type)
        return Function(tuple(inst_function))

    def __str__(self):
        rep = ""
        for t in self[:-1]:
            rep += str(t) + " -> "

        rep += str(self[-1])
        return rep

    def __repr__(self):
        return self.__str__()


class Tuple(Type):
    def __str__(self):
        return str(tuple(self))

    def __repr__(self):
        return self.__str__()


class Context(frozendict):
    def update(self, anther_dict: Union[frozendict, dict]):
        return self.copy(**anther_dict)

    def split(self):
        funcs = {}
        vars = {}
        for item in self.items():
            (_name, _type) = item
            if type(item) is Type:
                vars[_name] = _type
            else:
                funcs[_name] = _type

        return frozendict(vars), frozendict(funcs)

    def inst_return_types(self, t):
        res = {}
        for item in self.items():
            (term_name, term_type) = item
            if type(term_type) is Function:
                res[term_name] = term_type.inst_return_type(t)
            else:
                res[term_name] = term_type

        return frozendict(res)

from typing import Iterable, Sized, Union


class Type(tuple):
    def __new__(cls, seq: Iterable):
        return super(Type, cls).__new__(cls, seq)

    def __str__(self):
        return str(self[0])

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

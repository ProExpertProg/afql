from abc import ABC, abstractmethod

from afqlite.common import Tuple


class Expression(ABC):

    @abstractmethod
    # args = [tuple]
    def __call__(self, *args, **kwargs):
        pass


class Predicate(Expression, ABC):
    pass


class Value(Expression, ABC):
    pass


class BinaryPredicate(Predicate, ABC):
    def __init__(self, left: Predicate, right: Predicate):
        self.left = left
        self.right = right


class Or(BinaryPredicate):
    def __call__(self, *args, **kwargs):
        return self.left(*args, **kwargs) or self.right(*args, **kwargs)


class And(BinaryPredicate):
    def __call__(self, *args, **kwargs):
        return self.left(*args, **kwargs) and self.right(*args, **kwargs)


class Compare(Predicate):
    OPS = {
        ">": lambda x, y: x > y,
        "<": lambda x, y: x < y,
        ">=": lambda x, y: x >= y,
        "<=": lambda x, y: x <= y,
        "==": lambda x, y: x == y,
        "!=": lambda x, y: x != y,
        "<>": lambda x, y: x != y,
    }

    def __init__(self, op, arg1: Value, arg2: Value):
        self.arg1 = arg1
        self.arg2 = arg2
        self.op = op

    def __call__(self, *args, **kwargs):
        return self.OPS[self.op](self.arg1(*args, **kwargs), self.arg2(*args, **kwargs))


class Column(Value):
    def __init__(self, index: int):
        self.index = index

    def __call__(self, *args, **kwargs):
        t: Tuple = args[0]
        assert isinstance(t, Tuple)

        return t[self.index]


class Constant(Value):
    def __init__(self, c):
        self.c = c

    def __call__(self, *args, **kwargs):
        return self.c

from abc import ABC, abstractmethod


class Predicate(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

class BinaryPredicate(Predicate, ABC):
    def __init__(self, left: Predicate, right: Predicate):
        self.left = left
        self.right = right

class Or(BinaryPredicate):
    def __call__(self, *args, **kwargs):
        return self.left(args, kwargs) or self.right(args, kwargs)

class And(BinaryPredicate):
    def __call__(self, *args, **kwargs):
        return self.left(args, kwargs) and self.right(args, kwargs)
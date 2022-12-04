from abc import abstractmethod, ABC
from typing import Iterator

from afqlite.cache import Cache
from afqlite.common import Tuple, TupleDesc, td_add_alias
from afqlite.detector import Detector
from afqlite.predicates import Predicate


class Operator(ABC):
    @abstractmethod
    def run(self) -> Iterator[Tuple]:
        pass

    @abstractmethod
    def tupledesc(self) -> TupleDesc:
        pass


class Scan(Operator):
    def __init__(self, cache: Cache, ):
        self.cache = cache

    def run(self) -> Iterator[Tuple]:
        for t in self.cache.TODO():  # TODO get items from cache
            yield t

    def tupledesc(self) -> TupleDesc:
        pass


class Join(Operator):
    def __init__(self, alias1: str, alias2: str, sub_operator1: Operator, sub_operator2: Operator):
        self.alias1 = alias1
        self.alias2 = alias2
        self.sub_operator1 = sub_operator1
        self.sub_operator2 = sub_operator2

    def run(self) -> Iterator[Tuple]:
        for t in self.sub_operator1.run():
            for t2 in self.sub_operator2.run():
                if self.predicate(t, t2):  # TODO join predicate
                    yield t

    def tupledesc(self) -> TupleDesc:
        td1 = td_add_alias(self.alias1, self.sub_operator1.tupledesc())
        td2 = td_add_alias(self.alias2, self.sub_operator2.tupledesc())
        return td1 | td2

class Filter(Operator):
    def __init__(self, sub_operator: Operator, predicate: Predicate): # TODO predicate
        self.predicate = predicate
        self.sub_operator = sub_operator

    def run(self) -> Iterator[Tuple]:
        for t in self.sub_operator.run():
            if self.predicate(t):
                yield t

    def tupledesc(self) -> TupleDesc:
        return self.sub_operator.tupledesc()


class DetectorFilter(Operator):
    def __init__(self, timestamp_at: int, classes: list[str], confidences: list[float], sub_operator: Operator, detector: Detector):
        self.confidences = confidences
        self.timestamp_at = timestamp_at
        self.classes = classes
        self.sub_operator = sub_operator
        self.detector = detector

    def run(self) -> Iterator[Tuple]:
        for t in self.sub_operator.run():

            obj = self.detector.detect(t[self.timestamp_at], self.classes, self.confidences)

            # TODO figure out how to merge results
            if obj is not None:
                yield t | obj

    def tupledesc(self) -> TupleDesc:
        pass



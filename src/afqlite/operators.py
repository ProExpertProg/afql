from abc import abstractmethod, ABC
from functools import cache
from typing import Iterator

from afqlite.cache import Cache
from afqlite.common import Tuple, TupleDesc, td_add_alias
from afqlite.detector import CachedDetector
from afqlite.predicates import Predicate


class Operator(ABC):
    @abstractmethod
    def run(self) -> Iterator[Tuple]:
        pass

    @abstractmethod
    def tupledesc(self) -> TupleDesc:
        pass


class Scan(Operator):
    def __init__(self, c: Cache, table: str):
        self.cache = c
        self.table = table

    def run(self) -> Iterator[Tuple]:
        for t in self.cache.scan_table(self.table):  # TODO get items from cache
            yield Tuple(self.tupledesc(), t)

    def tupledesc(self) -> TupleDesc:
        return {
            'timestamp': 'int',
            'xmin': 'float', 'ymin': 'float', 'xmax': 'float', 'ymax': 'float',
            'confidence': 'float',
            'class': 'int'
        }


class Join(Operator):
    def __init__(self, alias1: str, alias2: str, sub_operator1: Operator, sub_operator2: Operator):
        self.alias1 = alias1
        self.alias2 = alias2
        self.sub_operator1 = sub_operator1
        self.sub_operator2 = sub_operator2

    def run(self) -> Iterator[Tuple]:
        for t in self.sub_operator1.run():
            for t2 in self.sub_operator2.run():
                yield Tuple(self.tupledesc(), (t | t2).values)

    @cache
    def tupledesc(self) -> TupleDesc:
        td1 = td_add_alias(self.alias1, self.sub_operator1.tupledesc())
        td2 = td_add_alias(self.alias2, self.sub_operator2.tupledesc())
        return td1 | td2


class Filter(Operator):
    def __init__(self, predicate: Predicate, sub_operator: Operator):  # TODO predicate
        self.predicate = predicate
        self.sub_operator = sub_operator

    def run(self) -> Iterator[Tuple]:
        for t in self.sub_operator.run():
            if self.predicate(t):
                yield t

    def tupledesc(self) -> TupleDesc:
        return self.sub_operator.tupledesc()


class DetectorFilter(Operator):
    def __init__(self, timestamp_at: int, cls: int, confidence: float, detector: CachedDetector,
                 sub_operator: Operator):
        self.confidence = confidence
        self.timestamp_at = timestamp_at
        self.cls = cls
        self.sub_operator = sub_operator
        self.detector = detector

    def run(self) -> Iterator[Tuple]:
        for t in self.sub_operator.run():

            # check confidence
            if t[6] >= self.confidence:
                yield t

            obj = self.detector.detect(t[self.timestamp_at], self.cls)

            # TODO replace bb and confidence columns
            if obj is not None:
                yield t | obj

    def tupledesc(self) -> TupleDesc:
        pass

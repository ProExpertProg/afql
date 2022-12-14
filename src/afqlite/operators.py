from abc import abstractmethod, ABC
from functools import cache
from typing import Iterator, Sequence

from afqlite.cache import Cache
from afqlite.common import Tuple, TupleDesc, td_add_alias
from afqlite.detector import CachedDetector
from afqlite.predicates import Predicate
from afqlite.video.detector import DetectionTuple


class Operator(ABC):
    @abstractmethod
    def run(self) -> Iterator[Tuple]:
        pass

    @abstractmethod
    def tupledesc(self) -> TupleDesc:
        pass

    @abstractmethod
    def explain(self, level: int = 0) -> str:
        pass

    @staticmethod
    def indent(level: int) -> str:
        return " " * 4 * level


class Scan(Operator):
    def __init__(self, low_precision: Cache, high_precision: Cache, table: str):
        self.low_precision = low_precision
        self.high_precision = high_precision
        self.table = table

    def run(self) -> Iterator[Tuple]:
        for t in self.low_precision.scan(self.high_precision):
            yield Tuple(self.tupledesc(), t)

    def tupledesc(self) -> TupleDesc:
        return [
            ('xmin', 'float'), ('ymin', 'float'), ('xmax', 'float'), ('ymax', 'float'),
            ('confidence', 'float'),
            ('class', 'int'),
            ('timestamp', 'int'),
            ('classifier', 'str')
        ]

    def explain(self, level: int = 0) -> str:
        return self.indent(level) + "Scan(table=%s)\n" % (self.table,)


class Join(Operator):
    def __init__(self, alias1: str, alias2: str, sub_operator1: Operator, sub_operator2: Operator):
        self.alias1 = alias1
        self.alias2 = alias2
        self.sub_operator1 = sub_operator1
        self.sub_operator2 = sub_operator2

    def run(self) -> Iterator[Tuple]:
        for t in self.sub_operator1.run():
            for t2 in self.sub_operator2.run():
                yield Tuple(self.tupledesc(), (t + t2).values)

    @cache
    def tupledesc(self) -> TupleDesc:
        td1 = td_add_alias(self.alias1, self.sub_operator1.tupledesc())
        td2 = td_add_alias(self.alias2, self.sub_operator2.tupledesc())
        return td1 + td2

    def explain(self, level: int = 0) -> str:
        return self.indent(level) + "Join(alias=[%s,%s])\n" % (self.alias1, self.alias2) \
            + self.sub_operator1.explain(level + 1) + self.sub_operator2.explain(level + 1)


class Filter(Operator):
    def __init__(self, predicate: Predicate, sub_operator: Operator):
        self.predicate = predicate
        self.sub_operator = sub_operator

    def run(self) -> Iterator[Tuple]:
        for t in self.sub_operator.run():
            if self.predicate(t):
                yield t

    def tupledesc(self) -> TupleDesc:
        return self.sub_operator.tupledesc()

    def explain(self, level: int = 0) -> str:
        return self.indent(level) + "Filter(%s)\n" % (self.predicate.explain(self.tupledesc()),) \
            + self.sub_operator.explain(level + 1)


class DetectorFilter(Operator):
    def __init__(self, timestamp_at: int, confidence_at, cls: int, confidence: float, detector: CachedDetector,
                 sub_operator: Operator):
        self.confidence = confidence
        self.timestamp_at = timestamp_at
        self.confidence_at = confidence_at
        self.cls = cls
        self.sub_operator = sub_operator
        self.detector = detector

    def run(self) -> Iterator[Tuple]:
        for tuples in self.group_by_timestamp():

            # check all the timestamps are the same
            timestamp = tuples[0][self.timestamp_at]
            assert all(t[self.timestamp_at] == timestamp for t in tuples)

            # if confidence is good enough on all of them, return existing tuples
            if min(t[self.confidence_at] for t in tuples) >= self.confidence:
                yield from tuples
                continue

            # run detector and replace bb columns in tuples
            detections = self.detector.detect(timestamp, self.cls)
            yield from self.match_and_replace(tuples, detections)

    @cache
    def tupledesc(self) -> TupleDesc:
        return self.sub_operator.tupledesc()

    def explain(self, level: int = 0) -> str:
        return self.indent(level) + "DetectorFilter(class=%s, confidence=%s)\n" % (self.cls, self.confidence) \
            + self.sub_operator.explain(level + 1)

    def group_by_timestamp(self) -> Iterator[list[Tuple]]:
        last_timestamp, tuples = None, []
        for t in self.sub_operator.run():
            timestamp = t[self.timestamp_at]
            if timestamp != last_timestamp and len(tuples) != 0:
                yield tuples
                tuples = []
                last_timestamp = timestamp

            tuples.append(t)

        if len(tuples) > 0:
            yield tuples

    def match_and_replace(self, tuples: list[Tuple], detections: list[DetectionTuple]) -> Sequence[Tuple]:
        """
        match_and_replace will match the given tuples with fresh detections and return updated tuples.

        :param tuples:
        :param detections:
        :return:
        """
        # TODO
        if len(detections) == 0:
            return []
        return tuples

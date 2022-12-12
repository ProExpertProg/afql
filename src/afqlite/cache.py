from typing import Iterator, Union

from afqlite.video.detector import DetectionTuple

Key = tuple[int, int]


class Cache:
    def __init__(self):
        self.detections: dict[Key, list[DetectionTuple]] = {}

    def scan(self) -> Iterator[DetectionTuple]:
        for detections in self.detections.values():
            yield from detections

    # TODO:
    #  - implement scan
    #  - find: query tuple given class, timestamp
    #   - each detector will get its own cache object
    #  -
    #  - implement replace for built-in high-precision to replace the preprocessed tuples
    #    - maybe subclass of cache
    #    - reuse replacement from DetectorFilter
    #  - implement load/construct from file
    #    - merging not allowed
    #  - implement store/write to file
    #  - static registry of caches and detectors
    def store(self, timestamp: int, cls: int, detections: list[DetectionTuple] = None):
        """
        store will save the given detections for the given timestamp and class
        :param timestamp: video timestamp
        :param cls: object class
        :param detections: if None, the cache will remember that there aren't any detections for this timestamp and class.
        :return:
        """
        # overwrite any existing detections
        self.detections[timestamp, cls] = [] if detections is None else detections

    def find(self, timestamp: int, cls: int) -> tuple[list[DetectionTuple], bool]:
        """
        find returns a list of detection tuples
        :param timestamp:
        :param cls:
        :return: (detections, found)
          exists indicates whether this was a cache hit (True) or miss (False).
          If True, detections can be empty if there weren't any detections for this class and timestamp.
        """
        key = (timestamp, cls)
        if key in self.detections:
            return self.detections[key], True

        # cache miss
        return [], False

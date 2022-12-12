from abc import abstractmethod, ABC
from typing import Iterator, Union

from afqlite.common import Tuple
from afqlite.video.detector import DetectionTuple


class Cache(ABC):
    @abstractmethod
    def scan_table(self, table: str) -> Iterator[DetectionTuple]:
        pass

    # TODO:
    #  - implement scan
    #  - find: query tuple given class, timestamp
    #   - each detector will get its own cache object
    #  -
    #  - implement replace for built-in high-precision to replace the preprocessed tuples
    #    - maybe subclass of cache
    #  - implement load/construct from file
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
        pass

    """
    find
    """

    def find(self, timestamp: int, cls: int) -> tuple[list[DetectionTuple], bool]:
        """
        find will return a list of detection tuples
        :param timestamp:
        :param cls:
        :return: (detections, exists)
          exists indicates whether this was a cache hit (True) or miss (False).
          If True, detections can be empty if there weren't any detections for this class and timestamp.
        """
        pass

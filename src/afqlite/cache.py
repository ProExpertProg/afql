from abc import abstractmethod, ABC
from typing import Iterator, Union

from afqlite.common import Tuple

CachedTuple = tuple[int, float, float, float, float, float, int]
# TODO maybe store hash of detector?

class Cache(ABC):
    @abstractmethod
    def scan_table(self, table: str) -> Iterator[CachedTuple]:
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


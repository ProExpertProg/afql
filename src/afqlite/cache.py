from typing import Iterator, Union

from afqlite.video.detector import DetectionTuple, COLUMN_TO_INDEX

# class, timestamp
Key = tuple[int, int]
DetectionStore = dict[Key, list[DetectionTuple]]


class Cache:
    def __init__(self, detections=None):
        self.detections: DetectionStore = {} if detections is None else detections

    def scan(self, other: 'Cache' = None) -> Iterator[DetectionTuple]:
        """
        scan will generate all DetectionTuples.
        If other has tuples for the same key, those will be used instead.
        """
        for key in self.detections:
            if other is not None and key in other.detections:
                yield from other.detections[key]
            else:
                yield from self.detections[key]

    def store(self, timestamp: int, cls: int, detections: list[DetectionTuple] = None):
        """
        store will save the given detections for the given timestamp and class
        :param timestamp: video timestamp
        :param cls: object class
        :param detections: if None, the cache will remember that there aren't any detections for this timestamp and class.
        :return:
        """
        # overwrite any existing detections
        self.detections[(cls, timestamp)] = [] if detections is None else detections

    def find(self, timestamp: int, cls: int) -> tuple[list[DetectionTuple], bool]:
        """
        find returns a list of detection tuples
        :param timestamp:
        :param cls:
        :return: (detections, found)
          exists indicates whether this was a cache hit (True) or miss (False).
          If True, detections can be empty if there weren't any detections for this class and timestamp.
        """
        key = (cls, timestamp)
        if key in self.detections:
            return self.detections[key], True

        # cache miss
        return [], False

    def merge(self, cached_data: Union[DetectionStore, list[DetectionTuple]]):
        """
        Items in cached_data take precedence over existing items (any data that already exists will be replaced).
        """
        # handle a list of detections passed in
        if isinstance(cached_data, list):
            data_dict : DetectionStore = {}
            for detection in cached_data:
                key = (detection[COLUMN_TO_INDEX['class']], detection[COLUMN_TO_INDEX['timestamp']])
                data_dict[key] = data_dict.get(key, []) + [DetectionTuple(detection)]
            cached_data = data_dict

        assert isinstance(cached_data, dict)
        self.detections |= cached_data

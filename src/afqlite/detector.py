from typing import Sequence

from afqlite.cache import Cache
from afqlite.video.detector import Detector, DetectionTuple, COLUMN_TO_INDEX
from afqlite.video.loader import VideoLoader


class CachedDetector:
    def __init__(self, cache: Cache, detector: Detector, classes: Sequence[int], confidence, video_loader: VideoLoader):
        self.cache = cache
        self.detector = detector
        self.confidence = confidence
        self.video_loader = video_loader
        self.classes = set(classes)
        self.classes_list = list(classes)

    def detect(self, timestamp: int, cls: int) -> list[DetectionTuple]:
        """
        detect finds all detections for the given timestamp and class.
        It looks them up in the cache and otherwise runs the detector on the appropriate frame,
        storing all detections returned for all classes.
        """

        detections, found = self.cache.find(timestamp, cls)
        if found:
            # detections could be empty (means the detector ran and returned no result)
            # or a proper list of tuples
            return detections

        raw_detections = self.detector.detect(timestamp, self.classes_list, self.confidence, self.video_loader)
        detections_by_class = self.partition_by_class(raw_detections)

        # store all detections in the cache
        for c in self.classes:
            # None if no such key
            detections_for_c = detections_by_class.get(c)
            self.cache.store(timestamp, c, detections_for_c)
            if c == cls:
                detections = [] if detections_for_c is None else detections_for_c

        return detections

    def partition_by_class(self, raw_detections: list[DetectionTuple]) -> dict[int, list[DetectionTuple]]:
        # partition by class
        detections: dict[int, list[DetectionTuple]] = {}
        for raw in raw_detections:
            raw_cls = raw[COLUMN_TO_INDEX['class']]
            detections[raw_cls] = detections.get(raw_cls, []) + [raw]

        # only detected classes that were given
        assert all(c in self.classes for c in detections)

        return detections

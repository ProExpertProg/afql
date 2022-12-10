from afqlite.cache import Cache

# TODO Detection tuple
DetectionTuple = tuple[float, float, float, float, float, int]

class CachedDetector:
    def __init__(self, cache: Cache, detector: 'Detector', classes: list[int]):
        self.cache = cache
        self.detector = detector
        self.classes = classes


    # Should also store any detections it makes in the cache
    # and look up the results in a cache
    def detect(self, timestamp: int, cls: int) -> DetectionTuple:
        detection, exists = self.cache.find(timestamp, cls) # TODO
        if exists: # TODO somehow check that the cache result is from running this detector and not preprocessing
            return detection

        #TODO handle array
        detections = self.detector.detect(timestamp, self.classes)

        if detection is None:
            self.cache.store_empty(timestamp, cls)
        else:
            self.cache.store(timestamp, cls, detection)
            return detection

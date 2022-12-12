import pickle
from typing import Union

from afqlite.cache import Cache, DetectionStore
from afqlite.video.detector import Detector, DetectionTuple

BUILTIN_LIGHT = "__builtin_lightweight__"
BUILTIN_HEAVY = "__builtin_heavyweight__"


class DatasetAlreadyExists(Exception):
    pass


class NoSuchDataset(Exception):
    pass


class NoSuchDetector(Exception):
    pass


class DetectorAlreadyExists(Exception):
    pass


class AFQLite:
    def __init__(self):
        # keyed by name, contains video path
        self.datasets: dict[str, str] = {}

        # keyed by detector name
        self.detectors: dict[str, Detector] = {
            # TODO
            BUILTIN_LIGHT: None,
            BUILTIN_HEAVY: None,
        }

        # keyed by dataset and detector hash
        self.caches: dict[tuple[str, str], Cache] = {}

        print("AFQLite initialized")

    def import_cache(self, dataset: str, detector: str, cached_data: DetectionStore):
        # cached_data will replace existing data for any overlapping keys
        # TODO maybe check that the classifier hash matches?
        self._find_cache(dataset, detector).merge(cached_data)

    def export_cache(self, dataset: str, detector: str) -> DetectionStore:
        return self._find_cache(dataset, detector).detections

    def _find_cache(self, dataset: str, detector: str) -> Cache:
        cache_key = (dataset, detector)

        if dataset not in self.datasets:
            raise NoSuchDataset
        if detector not in self.detectors:
            raise NoSuchDetector

        # we know cache must exist now
        assert cache_key in self.caches
        return self.caches[(dataset, detector)]

    # TODO maybe add support for other file types
    def write_cache_to_file(self, dataset: str, detector: str, path: str):
        data = self.export_cache(dataset, detector)
        with open(path, "wb") as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def import_cache_from_file(self, dataset: str, detector: str, path: str):
        with open(path, "rb") as handle:
            self.import_cache(dataset, detector, pickle.load(handle))

    def load_video(self, dataset: str, video_path: str, cache_path: Union[str, None]):
        if dataset in self.datasets:
            raise DatasetAlreadyExists

        self.datasets[dataset] = video_path

        # create a new cache for each existing detector
        for detector in self.detectors:
            cache_key = (dataset, detector)
            assert cache_key not in self.caches
            self.caches[cache_key] = Cache()

        if cache_path is None:
            # TODO run lightweight preprocessing and store results in cache
            self._find_cache(dataset, BUILTIN_LIGHT).merge({})
        else:
            self.import_cache_from_file(dataset, BUILTIN_LIGHT, cache_path)

    def add_detector(self, name: str, model_path: str):
        if name in self.detectors:
            raise DetectorAlreadyExists

        self.detectors[name] = Detector(model_path, name)

        # create a new cache for each existing dataset
        for dataset in self.datasets:
            cache_key = (dataset, name)
            assert cache_key not in self.caches
            self.caches[cache_key] = Cache()

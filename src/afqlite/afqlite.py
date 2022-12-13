import itertools
import pandas
import pickle
from typing import Union

from afqlite.cache import Cache, DetectionStore
from afqlite.video.detector import Detector, DetectionTuple, DETECTION_TUPLE_LEN, INDEX_TO_COLUMN, get_heavyweight, \
    get_lightweight
from afqlite.video.loader import VideoLoader

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


class UnsupportedExtension(Exception):
    pass


class InvalidDataError(Exception):
    pass


class AFQLite:
    def __init__(self, heavyweight: Detector = None, lightweight: Detector = None):
        if heavyweight is None:
            heavyweight = get_heavyweight(BUILTIN_HEAVY)

        if lightweight is None:
            lightweight = get_lightweight(BUILTIN_LIGHT)

        # keyed by name, contains video loader
        self.datasets: dict[str, VideoLoader] = {}

        # keyed by detector name
        self.detectors: dict[str, Detector] = {
            BUILTIN_LIGHT: lightweight,
            BUILTIN_HEAVY: heavyweight,
        }

        # keyed by dataset and detector hash
        self.caches: dict[tuple[str, str], Cache] = {}

    def import_cache(self, dataset: str, detector: str, cached_data: Union[DetectionStore, list[DetectionTuple]]):
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
        ext = path.split(".")[-1]
        if ext == "pickle":
            with open(path, "wb") as handle:
                pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
        elif ext == "csv":
            values = list(itertools.chain.from_iterable(data.values()))
            df = pandas.DataFrame(values, columns=INDEX_TO_COLUMN)
            df.to_csv(path, index=False)
        else:
            raise UnsupportedExtension

    def import_cache_from_file(self, dataset: str, detector: str, path: str):
        ext = path.split(".")[-1]
        if ext == "pickle":
            with open(path, "rb") as handle:
                self.import_cache(dataset, detector, pickle.load(handle))
        elif ext == "csv":
            df = pandas.read_csv(path)
            detections = df.values.tolist()
            if len(detections[0]) != DETECTION_TUPLE_LEN:
                raise InvalidDataError
            self.import_cache(dataset, detector, detections)
        else:
            raise UnsupportedExtension

    def load_video(self, dataset: str, video_path: str, cache_path: str = None):
        if dataset in self.datasets:
            raise DatasetAlreadyExists

        self.datasets[dataset] = VideoLoader(video_path)

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

    def add_detector(self, name: str, model_path: str, model_hash: str = None):
        if name in self.detectors:
            raise DetectorAlreadyExists

        self.detectors[name] = Detector(model_path, name)  # TODO , model_hash)

        # create a new cache for each existing dataset
        for dataset in self.datasets:
            cache_key = (dataset, name)
            assert cache_key not in self.caches
            self.caches[cache_key] = Cache()

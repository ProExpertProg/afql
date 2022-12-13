import os
import tempfile
from pathlib import Path
from unittest import TestCase

from afqlite.afqlite import *


class TestAFQLite(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cache_path = str(Path(__file__).parent / "../../zebra/zebra_tuples.csv")
        self.video_path = str(Path(__file__).parent / "../../zebra/zebra_giraffe_human.mp4")

        # don't want to initialize the detectors
        # noinspection PyTypeChecker
        self.afql = AFQLite(False, False)

    def test_cache_exceptions(self):
        afql = self.afql
        with self.assertRaises(UnsupportedExtension):
            afql.import_cache_from_file("zebra", BUILTIN_LIGHT, "./a.txt")

        with self.assertRaises(NoSuchDataset):
            afql.import_cache_from_file("zebra", BUILTIN_LIGHT, self.cache_path)

        with self.assertRaises(NoSuchDataset):
            temp = tempfile.mktemp()
            afql.write_cache_to_file("zebra", BUILTIN_LIGHT, temp)

            # only reached if something was written, which is a failed case
            os.remove(temp)

        # We now have the video
        afql.load_video("zebra", self.video_path, self.cache_path)

        with self.assertRaises(NoSuchDetector):
            afql.import_cache_from_file("zebra", "custom", self.cache_path)

        with self.assertRaises(NoSuchDetector):
            temp = tempfile.mktemp()
            afql.write_cache_to_file("zebra", "custom", temp)

            # only reached if something was written, which is a failed case
            os.remove(temp)

        with self.assertRaises(UnsupportedExtension):
            afql.write_cache_to_file("zebra", BUILTIN_LIGHT, "./a.txt")

    def test_read_write_cache_csv(self):
        print(os.getcwd())
        afql = self.afql

        afql.load_video("zebra", self.video_path, self.cache_path)

        out = tempfile.mktemp() + ".csv"
        afql.write_cache_to_file("zebra", BUILTIN_LIGHT, out)
        afql.import_cache_from_file("zebra", BUILTIN_HEAVY, out)
        print(out)
        # os.remove(out)

        data1 = afql._find_cache("zebra", BUILTIN_LIGHT).detections
        data2 = afql._find_cache("zebra", BUILTIN_HEAVY).detections
        self.assertCountEqual(data1, data2)
    def test_read_write_cache_pickle(self):
        print(os.getcwd())
        afql = self.afql

        with self.assertRaises(NoSuchDataset):
            afql.import_cache_from_file("zebra", "custom", self.cache_path)

        afql.load_video("zebra", self.video_path, self.cache_path)

        out = tempfile.mktemp() + ".pickle"
        afql.write_cache_to_file("zebra", BUILTIN_LIGHT, out)
        afql.import_cache_from_file("zebra", BUILTIN_HEAVY, out)
        os.remove(out)

        data1 = afql._find_cache("zebra", BUILTIN_LIGHT).detections
        data2 = afql._find_cache("zebra", BUILTIN_HEAVY).detections
        self.assertCountEqual(data1, data2)





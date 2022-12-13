import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from afqlite.afqlite import AFQLite, BUILTIN_HEAVY
from afqlite.detector import CachedDetector
from afqlite.operators import Filter, DetectorFilter, Join, Scan
from afqlite.predicates import Column, Constant, Compare, And

from afqlite.classes import INDEX_TO_CLASS, CLASS_TO_INDEX
from afqlite.video.detector import COLUMN_TO_INDEX, NUM_COLUMNS

GIRAFFE = CLASS_TO_INDEX['giraffe']
PERSON = CLASS_TO_INDEX['person']


class TestIntegration(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cache_path = str(Path(__file__).parent / "../../zebra/zebra_tuples.csv")
        self.video_path = str(Path(__file__).parent / "../../zebra/zebra_giraffe_human.mp4")

        # TODO no lightweight yet
        # noinspection PyTypeChecker
        self.afql = AFQLite(lightweight=False)
        self.afql.load_video("zebra", self.video_path, self.cache_path)
        self.light_cache, self.heavy_cache = self.afql._builtin_caches("zebra")
        self.heavy = self.afql.detectors[BUILTIN_HEAVY]
        self.video_loader = self.afql.datasets["zebra"]

    def test_query0(self):
        query = Filter(Compare("==", Column(COLUMN_TO_INDEX['class']), Constant(GIRAFFE)),
                       Scan(self.light_cache, self.heavy_cache, "zebra"))

        results = list(query.run())
        self.assertGreater(len(results), 10)

    def query1(self, confidence):
        return DetectorFilter(COLUMN_TO_INDEX['timestamp'], COLUMN_TO_INDEX['confidence'], GIRAFFE,
                              confidence,
                              CachedDetector(self.heavy_cache, self.heavy, [GIRAFFE], confidence, self.video_loader),
                              Filter(
                                  Compare("==", Column(COLUMN_TO_INDEX['class']), Constant(GIRAFFE)),
                                  Scan(self.light_cache, self.heavy_cache, "zebra"))
                              )

    def test_query1(self):
        query = self.query1(0.50)
        query_higher = self.query1(0.90)

        results = list(query.run())
        results_higher = list(query_higher.run())
        self.assertGreater(len(results), len(results_higher))


    def _test_query2(self):
        join = Join("giraffes", "people",
                    Filter(Compare("==", Column(COLUMN_TO_INDEX['class']),
                                   Constant(GIRAFFE)),
                           Scan(self.light_cache, self.heavy_cache, "zebra")),
                    Filter(Compare("==", Column(COLUMN_TO_INDEX['class']),
                                   Constant(PERSON)),
                           Scan(self.light_cache, self.heavy_cache, "zebra"))
                    )

        query = DetectorFilter(COLUMN_TO_INDEX['timestamp'], COLUMN_TO_INDEX['confidence'], GIRAFFE, 0.8,
                               CachedDetector(self.heavy_cache, self.heavy, [GIRAFFE, PERSON], 0.8, self.video_loader),
                               Filter(
                                   And(Compare("<", Column(COLUMN_TO_INDEX['xmax']),
                                               Column(COLUMN_TO_INDEX['xmin'] + NUM_COLUMNS)),
                                       Compare("==", Column(COLUMN_TO_INDEX['timestamp']),
                                               Column(COLUMN_TO_INDEX['timestamp'] + NUM_COLUMNS)),
                                       ),
                                   join
                               )
                               )

        # check just the join first
        join_results = list(join.run())

        results = list(query.run())
        # TODO

if __name__ == '__main__':
    unittest.main()

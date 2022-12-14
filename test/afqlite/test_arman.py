import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from afqlite.afqlite import AFQLite, BUILTIN_HEAVY
from afqlite.common import format_results
from afqlite.detector import CachedDetector
from afqlite.operators import Filter, DetectorFilter, Join, Scan
from afqlite.predicates import Column, Constant, Compare, And

from afqlite.classes import INDEX_TO_CLASS, CLASS_TO_INDEX
from afqlite.video.detector import COLUMN_TO_INDEX, NUM_COLUMNS

ZEBRA = CLASS_TO_INDEX['zebra']
GIRAFFE = CLASS_TO_INDEX['giraffe']
PERSON = CLASS_TO_INDEX['person']
DOG = CLASS_TO_INDEX["dog"]


class TestIntegration(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cache_path = str(Path(__file__).parent / "../../zebra/dog_ag_shortened.csv")
        self.video_path = str(Path(__file__).parent / "../../zebra/dog_ag_shortened.mp4")

        # TODO no lightweight yet
        # noinspection PyTypeChecker
        self.afql = AFQLite(lightweight=False)
        # self.afql.load_video("zebra", self.video_path, self.cache_path)
        # self.light_cache, self.heavy_cache = self.afql._builtin_caches("zebra")
        self.afql.load_video("dog_ag", self.video_path, self.cache_path)
        self.light_cache, self.heavy_cache = self.afql._builtin_caches("dog_ag")
        self.heavy = self.afql.detectors[BUILTIN_HEAVY]
        #self.video_loader = self.afql.datasets["zebra"]
        self.video_loader = self.afql.datasets["dog_ag"]

    # def test_query0(self):
    #     query = Filter(Compare("==", Column(COLUMN_TO_INDEX['class']), Constant(GIRAFFE)),
    #                    Scan(self.light_cache, self.heavy_cache, "zebra"))

    #     results = list(query.run())
    #     self.assertGreater(len(results), 10)

    def query1(self, confidence):
        return DetectorFilter(COLUMN_TO_INDEX['timestamp'], COLUMN_TO_INDEX['confidence'], PERSON,
                              confidence,
                              CachedDetector(self.heavy_cache, self.heavy, [PERSON], confidence, self.video_loader),
                              Filter(
                                  Compare("==", Column(COLUMN_TO_INDEX['class']), Constant(PERSON)),
                                  Scan(self.light_cache, self.heavy_cache, "person"))
                              )

    def test_query1(self):
        query = self.query1(0.50)
        query_higher = self.query1(0.90)

        results = list(query.run())
        results_higher = list(query_higher.run())
        self.assertGreater(len(results), len(results_higher))

    # def test_query2(self):
    #     join = Join("giraffes", "zebras",
    #                 Filter(Compare("==", Column(COLUMN_TO_INDEX['class']), Constant(GIRAFFE)),
    #                        Scan(self.light_cache, self.heavy_cache, "zebra")),
    #                 Filter(Compare("==", Column(COLUMN_TO_INDEX['class']), Constant(ZEBRA)),
    #                        Scan(self.light_cache, self.heavy_cache, "zebra"))
    #                 )

    #     query = DetectorFilter(COLUMN_TO_INDEX['timestamp'] + NUM_COLUMNS, COLUMN_TO_INDEX['confidence'] + NUM_COLUMNS, ZEBRA,
    #                    0.9,
    #                    CachedDetector(self.heavy_cache, self.heavy, [GIRAFFE, ZEBRA], 0.1, self.video_loader),
    #                    Filter(
    #                        And(Compare("<", Column(COLUMN_TO_INDEX['xmax'] + NUM_COLUMNS),  # zebra.xmax < giraffe.xmin
    #                                    Column(COLUMN_TO_INDEX['xmin'])),
    #                            Compare("==", Column(COLUMN_TO_INDEX['timestamp']),
    #                                    Column(COLUMN_TO_INDEX['timestamp'] + NUM_COLUMNS)),
    #                            ),
    #                        join
    #                    )
    #                    )

    #     # check just the join first
    #     join_results = list(join.run())

    #     results = list(query.run())
    #     # print(format_results(join_results, join.tupledesc()))
    #     print(format_results(results, query.tupledesc()))
    #     self.assertTrue(all(230 < t[COLUMN_TO_INDEX['timestamp']] < 236 for t in results))
    #     self.assertTrue(
    #         all(t[COLUMN_TO_INDEX['timestamp']] == t[COLUMN_TO_INDEX['timestamp'] + NUM_COLUMNS] for t in results))

if __name__ == '__main__':
    unittest.main()

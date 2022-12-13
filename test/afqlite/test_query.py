import unittest
from unittest.mock import Mock, MagicMock

from afqlite.classes import CLASS_TO_INDEX
from afqlite.operators import Filter, DetectorFilter, Join, Scan
from afqlite.predicates import Column, Constant, Compare, And
from afqlite.video.detector import COLUMN_TO_INDEX, NUM_COLUMNS


class TestQueries(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mock_cache = Mock()
        self.mock_cache_high = None
        self.mock_detector = Mock()

        # xmin, ymin, xmax, ymax, confidence, class, timestamp, classifier
        self.data = [
            (761.940552, 888.739929, 1387.906006, 2438.585938, 0.773518, 0, 0, "low"),
            (136.979660, 2063.324707, 541.410156, 2457.501953, 0.737668, 16, 0, "low"),
            (124.776512, 2058.910400, 570.484009, 2449.117432, 0.860716, 16, 1, "low"),
            (770.169800, 879.248901, 1388.099854, 2436.507812, 0.764172, 0, 1, "low"),
            (111.341286, 2051.248047, 574.959229, 2439.911865, 0.854964, 16, 2, "low"),
            (784.568359, 891.235718, 1389.603027, 2428.435547, 0.776998, 0, 2, "low"),
            (101.616623, 2051.115967, 582.127075, 2432.771729, 0.871185, 16, 3, "low"),
            (793.755249, 889.017944, 1387.266724, 2421.465332, 0.788094, 0, 3, "low"),
            (92.130936, 2047.976196, 583.562744, 2435.856934, 0.877330, 16, 4, "low"),
            (695.566345, 894.259644, 1394.778809, 2420.609131, 0.855311, 0, 4, "low"),
            (72.636543, 2039.401611, 594.891785, 2427.254883, 0.909762, 16, 5, "low"),
            (717.180054, 901.000000, 1391.186646, 2421.005859, 0.841077, 0, 5, "low")
        ]

        # need to make sure that every call to the generator returns fresh results
        def get_data(*args, **kwargs):
            yield from self.data

        self.mock_cache.scan = MagicMock()
        self.mock_cache.scan.side_effect = get_data
        self.mock_detector.detect = lambda timestamp, cls: []

    def test_query0(self):
        query = Filter(Compare("==", Column(COLUMN_TO_INDEX['class']), Constant(CLASS_TO_INDEX['dog'])),
                       Scan(self.mock_cache, self.mock_cache_high, "dog_video"))

        results = list(query.run())
        self.assertEqual(len(self.data) / 2, len(results))

    def query1(self, confidence):
        return DetectorFilter(COLUMN_TO_INDEX['timestamp'], COLUMN_TO_INDEX['confidence'], CLASS_TO_INDEX['dog'],
                              confidence,
                              self.mock_detector,
                              Filter(
                                  Compare("==", Column(COLUMN_TO_INDEX['class']), Constant(CLASS_TO_INDEX['dog'])),
                                  Scan(self.mock_cache, self.mock_cache_high, "dog_video"))
                              )

    def test_query1a(self):
        query = self.query1(0.73)

        # detector shouldn't be called
        self.mock_detector.detect = Mock(side_effect=RuntimeError)
        results = list(query.run())
        self.assertEqual(len(self.data) / 2, len(results))

    def test_query1b(self):
        query = self.query1(0.9)

        # detector now returns only empty tuples, so only above 0.9 should come through
        results = list(query.run())
        self.assertEqual(1, len(results))
        for i, value in enumerate(self.data[- 2]):
            self.assertEqual(value, results[0][i])

    def test_query2(self):
        join = Join("dogs", "people",
                    Filter(Compare("==", Column(COLUMN_TO_INDEX['class']),
                                   Constant(CLASS_TO_INDEX['dog'])),
                           Scan(self.mock_cache, self.mock_cache_high, "dog_video")),
                    Filter(Compare("==", Column(COLUMN_TO_INDEX['class']),
                                   Constant(CLASS_TO_INDEX['person'])),
                           Scan(self.mock_cache, self.mock_cache_high, "dog_video"))
                    )

        query = DetectorFilter(COLUMN_TO_INDEX['timestamp'], COLUMN_TO_INDEX['confidence'], CLASS_TO_INDEX['dog'], 0.7,
                               self.mock_detector,
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
        self.assertEqual(len(self.data) ** 2 / 4, len(join_results))

        results = list(query.run())
        self.assertEqual(len(self.data) / 2, len(results))

        td = results[0].tupledesc
        self.assertEqual(("dogs.xmin", 'float'), td[0])
        self.assertEqual(("people.xmin", 'float'), td[NUM_COLUMNS])


if __name__ == '__main__':
    unittest.main()

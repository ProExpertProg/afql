import unittest
from unittest.mock import Mock

from afqlite.operators import Filter, DetectorFilter, Join, Scan
from afqlite.predicates import Column, Constant, Compare, And

from afqlite.classes import INDEX_TO_CLASS, CLASS_TO_INDEX, COLUMN_TO_INDEX, NUM_COLUMNS


class TestQueries(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mock_cache = Mock()
        self.mock_detector = Mock()

        # timestamp, xmin, ymin, xmax, ymax, confidence, class
        self.data = [
            (0, 761.940552, 888.739929, 1387.906006, 2438.585938, 0.773518, 0),
            (0, 136.979660, 2063.324707, 541.410156, 2457.501953, 0.737668, 16),
            (1, 124.776512, 2058.910400, 570.484009, 2449.117432, 0.860716, 16),
            (1, 770.169800, 879.248901, 1388.099854, 2436.507812, 0.764172, 0),
            (2, 111.341286, 2051.248047, 574.959229, 2439.911865, 0.854964, 16),
            (2, 784.568359, 891.235718, 1389.603027, 2428.435547, 0.776998, 0),
            (3, 101.616623, 2051.115967, 582.127075, 2432.771729, 0.871185, 16),
            (3, 793.755249, 889.017944, 1387.266724, 2421.465332, 0.788094, 0),
            (4, 92.130936, 2047.976196, 583.562744, 2435.856934, 0.877330, 16),
            (4, 695.566345, 894.259644, 1394.778809, 2420.609131, 0.855311, 0),
            (5, 72.636543, 2039.401611, 594.891785, 2427.254883, 0.909762, 16),
            (5, 717.180054, 901.000000, 1391.186646, 2421.005859, 0.841077, 0)
        ]


        self.mock_cache.scan_table = Mock(return_value=iter(self.data))
        def detect(timestamp, ):
            pass

        self.mock_detector.detect = detect

    def test_query1(self):
        query = Filter(Compare("==", Column(COLUMN_TO_INDEX['class']), Constant(CLASS_TO_INDEX['dog'])),
                       Scan(self.mock_cache, "dog_video"))

        results = list(query.run())
        self.assertEqual(len(results), len(self.data) / 2)


def test_query1(self):
    query = DetectorFilter(0, CLASS_TO_INDEX['dog'], 0.9, self.mock_detector,
                           Filter(Compare("==", Column(COLUMN_TO_INDEX['class']), Constant(CLASS_TO_INDEX['dog'])),
                                  Scan(self.mock_cache, "dog_video")))

    results = list(query.run())
    self.assertEqual(len(results), len(self.data) / 2)


def test_query2(self):
    query = DetectorFilter(0, [CLASS_TO_INDEX['dog'], CLASS_TO_INDEX['person']], [0.9, 0.9], self.mock_detector,
                           Filter(And(Compare("<", Column(COLUMN_TO_INDEX['xmax']),
                                              Column(COLUMN_TO_INDEX['xmin'] + NUM_COLUMNS)),
                                      Compare("==", Column(COLUMN_TO_INDEX['timestamp']),
                                              Column(COLUMN_TO_INDEX['timestamp'] + NUM_COLUMNS)),
                                      ),
                                  Join("dogs", "people",
                                       Filter(Compare("==", Column(3), Constant(CLASS_TO_INDEX['dog'])),
                                              Scan(self.mock_cache, "dog_video")),
                                       Filter(Compare("==", Column(3), Constant(CLASS_TO_INDEX['person'])),
                                              Scan(self.mock_cache, "dog_video"))
                                       )
                                  )
                           )

    results = list(query.run())
    self.assertEqual(len(results), 5)


def test_split(self):
    s = 'hello world'
    self.assertEqual(s.split(), ['hello', 'world'])
    # check that s.split fails when the separator is not a string
    with self.assertRaises(TypeError):
        s.split(2)


if __name__ == '__main__':
    unittest.main()

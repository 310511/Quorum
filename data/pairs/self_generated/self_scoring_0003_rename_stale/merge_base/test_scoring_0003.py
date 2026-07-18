import unittest

from scoring_0003 import compute_total, aggregate_total


class Scoring0003Tests(unittest.TestCase):
    def test_compute_total(self):
        self.assertEqual(compute_total(6, 5), 11)

    def test_aggregate_total(self):
        self.assertEqual(aggregate_total([6, 5]), 11)

    def test_compute_total_product_shape(self):
        self.assertEqual(compute_total(6, 5) + aggregate_total([6]), 17)


if __name__ == '__main__':
    unittest.main()

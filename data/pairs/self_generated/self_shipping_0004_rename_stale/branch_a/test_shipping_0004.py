import unittest

from shipping_0004 import compute_cost_v2, aggregate_cost


class Shipping0004Tests(unittest.TestCase):
    def test_compute_cost(self):
        self.assertEqual(compute_cost_v2(7, 6), 13)

    def test_aggregate_cost(self):
        self.assertEqual(aggregate_cost([7, 6]), 13)

    def test_compute_cost_product_shape(self):
        self.assertEqual(compute_cost_v2(7, 6) + aggregate_cost([7]), 20)


if __name__ == '__main__':
    unittest.main()

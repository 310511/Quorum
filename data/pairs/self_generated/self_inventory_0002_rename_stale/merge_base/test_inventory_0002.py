import unittest

from inventory_0002 import compute_available, aggregate_available


class Inventory0002Tests(unittest.TestCase):
    def test_compute_available(self):
        self.assertEqual(compute_available(5, 4), 9)

    def test_aggregate_available(self):
        self.assertEqual(aggregate_available([5, 4]), 9)

    def test_compute_available_product_shape(self):
        self.assertEqual(compute_available(5, 4) + aggregate_available([5]), 14)


if __name__ == '__main__':
    unittest.main()

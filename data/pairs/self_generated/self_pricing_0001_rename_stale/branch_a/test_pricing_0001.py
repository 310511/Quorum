import unittest

from pricing_0001 import compute_subtotal_v2, aggregate_subtotal


class Pricing0001Tests(unittest.TestCase):
    def test_compute_subtotal(self):
        self.assertEqual(compute_subtotal_v2(4, 3), 7)

    def test_aggregate_subtotal(self):
        self.assertEqual(aggregate_subtotal([4, 3]), 7)

    def test_compute_subtotal_product_shape(self):
        self.assertEqual(compute_subtotal_v2(4, 3) + aggregate_subtotal([4]), 11)


if __name__ == '__main__':
    unittest.main()

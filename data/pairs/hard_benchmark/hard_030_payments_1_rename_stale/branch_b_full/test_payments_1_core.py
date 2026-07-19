import unittest
from payments_1_core import compute_payments_1_total, format_total

class CoreTests(unittest.TestCase):
    def test_total(self):
        self.assertEqual(compute_payments_1_total([1, 2, 3]), 6)
    def test_format(self):
        self.assertIn("6", format_total([1, 2, 3]))

if __name__ == "__main__":
    unittest.main()

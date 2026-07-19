import unittest
from parser_2_core import compute_parser_2_total_v2, format_total

class CoreTests(unittest.TestCase):
    def test_total(self):
        self.assertEqual(compute_parser_2_total_v2([1, 2, 3]), 6)
    def test_format(self):
        self.assertIn("6", format_total([1, 2, 3]))

if __name__ == "__main__":
    unittest.main()

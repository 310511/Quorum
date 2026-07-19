import unittest
from ledger_4_core import compute_ledger_4_total, format_total

class CoreTests(unittest.TestCase):
    def test_total(self):
        self.assertEqual(compute_ledger_4_total([1, 2, 3]), 6)
    def test_format(self):
        self.assertIn("6", format_total([1, 2, 3]))

if __name__ == "__main__":
    unittest.main()

import unittest
from ordering_007 import first_7, normalize_7

class OrderingTests(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(first_7([23]), 23)
    def test_equal_items(self):
        self.assertEqual(normalize_7([23, 23]), [23, 23])

if __name__ == "__main__":
    unittest.main()

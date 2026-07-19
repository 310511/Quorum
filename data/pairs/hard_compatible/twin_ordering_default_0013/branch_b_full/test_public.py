import unittest
from ordering_013 import first_13, normalize_13

class OrderingTests(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(first_13([41]), 41)
    def test_equal_items(self):
        self.assertEqual(normalize_13([41, 41]), [41, 41])

if __name__ == "__main__":
    unittest.main()

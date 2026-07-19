import unittest
from ordering_012 import first_12, normalize_12

class OrderingTests(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(first_12([38]), 38)
    def test_equal_items(self):
        self.assertEqual(normalize_12([38, 38]), [38, 38])

if __name__ == "__main__":
    unittest.main()

import unittest
from ordering_010 import first_10, normalize_10

class OrderingTests(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(first_10([32]), 32)
    def test_equal_items(self):
        self.assertEqual(normalize_10([32, 32]), [32, 32])

if __name__ == "__main__":
    unittest.main()

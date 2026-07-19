import unittest
from ordering_004 import first_4, normalize_4

class OrderingTests(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(first_4([14]), 14)
    def test_equal_items(self):
        self.assertEqual(normalize_4([14, 14]), [14, 14])

if __name__ == "__main__":
    unittest.main()

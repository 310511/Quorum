import unittest
from ordering_001 import first_1, normalize_1

class OrderingTests(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(first_1([5]), 5)
    def test_equal_items(self):
        self.assertEqual(normalize_1([5, 5]), [5, 5])

if __name__ == "__main__":
    unittest.main()

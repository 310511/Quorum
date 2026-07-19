import unittest
from ordering_011 import first_11, normalize_11

class OrderingTests(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(first_11([35]), 35)
    def test_equal_items(self):
        self.assertEqual(normalize_11([35, 35]), [35, 35])

if __name__ == "__main__":
    unittest.main()

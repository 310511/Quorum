import unittest
from ordering_014 import first_14, normalize_14

class OrderingTests(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(first_14([44]), 44)
    def test_equal_items(self):
        self.assertEqual(normalize_14([44, 44]), [44, 44])

if __name__ == "__main__":
    unittest.main()

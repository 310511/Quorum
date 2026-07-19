import unittest
from ordering_015 import first_15, normalize_15

class OrderingTests(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(first_15([47]), 47)
    def test_equal_items(self):
        self.assertEqual(normalize_15([47, 47]), [47, 47])

if __name__ == "__main__":
    unittest.main()

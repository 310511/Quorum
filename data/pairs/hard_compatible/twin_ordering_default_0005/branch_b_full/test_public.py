import unittest
from ordering_005 import first_5, normalize_5

class OrderingTests(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(first_5([17]), 17)
    def test_equal_items(self):
        self.assertEqual(normalize_5([17, 17]), [17, 17])

if __name__ == "__main__":
    unittest.main()

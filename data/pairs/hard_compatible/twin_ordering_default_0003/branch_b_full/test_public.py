import unittest
from ordering_003 import first_3, normalize_3

class OrderingTests(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(first_3([11]), 11)
    def test_equal_items(self):
        self.assertEqual(normalize_3([11, 11]), [11, 11])

if __name__ == "__main__":
    unittest.main()

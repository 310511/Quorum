import unittest
from ordering_008 import first_8, normalize_8

class OrderingTests(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(first_8([26]), 26)
    def test_equal_items(self):
        self.assertEqual(normalize_8([26, 26]), [26, 26])

if __name__ == "__main__":
    unittest.main()

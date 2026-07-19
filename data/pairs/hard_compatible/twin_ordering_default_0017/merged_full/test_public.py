import unittest
from ordering_017 import first_17, normalize_17

class OrderingTests(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(first_17([53]), 53)
    def test_equal_items(self):
        self.assertEqual(normalize_17([53, 53]), [53, 53])

if __name__ == "__main__":
    unittest.main()

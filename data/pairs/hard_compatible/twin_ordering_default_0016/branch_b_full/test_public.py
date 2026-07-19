import unittest
from ordering_016 import first_16, normalize_16

class OrderingTests(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(first_16([50]), 50)
    def test_equal_items(self):
        self.assertEqual(normalize_16([50, 50]), [50, 50])

if __name__ == "__main__":
    unittest.main()

import unittest
from ordering_009 import first_9, normalize_9

class OrderingTests(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(first_9([29]), 29)
    def test_equal_items(self):
        self.assertEqual(normalize_9([29, 29]), [29, 29])

if __name__ == "__main__":
    unittest.main()

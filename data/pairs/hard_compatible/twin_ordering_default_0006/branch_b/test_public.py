import unittest
from ordering_006 import first_6, normalize_6

class OrderingTests(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(first_6([20]), 20)
    def test_equal_items(self):
        self.assertEqual(normalize_6([20, 20]), [20, 20])

if __name__ == "__main__":
    unittest.main()

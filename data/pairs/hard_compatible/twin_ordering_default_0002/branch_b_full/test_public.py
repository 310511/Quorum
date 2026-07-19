import unittest
from ordering_002 import first_2, normalize_2

class OrderingTests(unittest.TestCase):
    def test_single_item(self):
        self.assertEqual(first_2([8]), 8)
    def test_equal_items(self):
        self.assertEqual(normalize_2([8, 8]), [8, 8])

if __name__ == "__main__":
    unittest.main()

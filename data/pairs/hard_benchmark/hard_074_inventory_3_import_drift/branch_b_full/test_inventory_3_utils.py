import unittest
from inventory_3_utils import normalize_inventory_3_token

class UtilsTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_inventory_3_token(" Ab "), "ab")

if __name__ == "__main__":
    unittest.main()

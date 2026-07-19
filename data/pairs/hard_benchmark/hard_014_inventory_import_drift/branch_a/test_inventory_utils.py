import unittest
from inventory_tokens import normalize_inventory_token

class UtilsTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_inventory_token(" Ab "), "ab")

if __name__ == "__main__":
    unittest.main()

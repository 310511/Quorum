import unittest
from shipping_1_tokens import normalize_shipping_1_token

class UtilsTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_shipping_1_token(" Ab "), "ab")

if __name__ == "__main__":
    unittest.main()

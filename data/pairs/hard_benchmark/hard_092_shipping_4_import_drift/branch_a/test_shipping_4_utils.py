import unittest
from shipping_4_tokens import normalize_shipping_4_token

class UtilsTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_shipping_4_token(" Ab "), "ab")

if __name__ == "__main__":
    unittest.main()

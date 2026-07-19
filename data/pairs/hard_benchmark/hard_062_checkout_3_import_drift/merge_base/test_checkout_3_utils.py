import unittest
from checkout_3_utils import normalize_checkout_3_token

class UtilsTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_checkout_3_token(" Ab "), "ab")

if __name__ == "__main__":
    unittest.main()

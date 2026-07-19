import unittest
from checkout_utils import normalize_checkout_token

class UtilsTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_checkout_token(" Ab "), "ab")

if __name__ == "__main__":
    unittest.main()

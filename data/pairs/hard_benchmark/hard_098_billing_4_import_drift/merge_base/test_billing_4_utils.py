import unittest
from billing_4_utils import normalize_billing_4_token

class UtilsTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_billing_4_token(" Ab "), "ab")

if __name__ == "__main__":
    unittest.main()

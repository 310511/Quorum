import unittest
from profile_1_utils import normalize_profile_1_token

class UtilsTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_profile_1_token(" Ab "), "ab")

if __name__ == "__main__":
    unittest.main()

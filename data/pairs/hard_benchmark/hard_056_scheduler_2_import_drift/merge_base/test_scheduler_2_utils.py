import unittest
from scheduler_2_utils import normalize_scheduler_2_token

class UtilsTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_scheduler_2_token(" Ab "), "ab")

if __name__ == "__main__":
    unittest.main()

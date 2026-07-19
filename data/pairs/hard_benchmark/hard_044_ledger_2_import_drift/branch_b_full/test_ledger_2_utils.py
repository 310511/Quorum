import unittest
from ledger_2_utils import normalize_ledger_2_token

class UtilsTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_ledger_2_token(" Ab "), "ab")

if __name__ == "__main__":
    unittest.main()

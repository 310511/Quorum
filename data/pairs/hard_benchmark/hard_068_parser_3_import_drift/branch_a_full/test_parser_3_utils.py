import unittest
from parser_3_tokens import normalize_parser_3_token

class UtilsTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_parser_3_token(" Ab "), "ab")

if __name__ == "__main__":
    unittest.main()

import unittest
from parser_tokens import normalize_parser_token

class UtilsTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_parser_token(" Ab "), "ab")

if __name__ == "__main__":
    unittest.main()

import unittest
from parser_013 import parse_count_13, valid_count_13

class ParserTests(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(parse_count_13("130"), 130)
        self.assertTrue(valid_count_13("130"))

if __name__ == "__main__":
    unittest.main()

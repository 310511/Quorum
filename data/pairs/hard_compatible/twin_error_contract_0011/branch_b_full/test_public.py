import unittest
from parser_011 import parse_count_11, valid_count_11

class ParserTests(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(parse_count_11("110"), 110)
        self.assertTrue(valid_count_11("110"))

if __name__ == "__main__":
    unittest.main()

import unittest
from parser_008 import parse_count_8, valid_count_8

class ParserTests(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(parse_count_8("80"), 80)
        self.assertTrue(valid_count_8("80"))

if __name__ == "__main__":
    unittest.main()

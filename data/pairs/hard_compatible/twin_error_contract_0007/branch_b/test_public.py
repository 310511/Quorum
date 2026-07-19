import unittest
from parser_007 import parse_count_7, valid_count_7

class ParserTests(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(parse_count_7("70"), 70)
        self.assertTrue(valid_count_7("70"))

if __name__ == "__main__":
    unittest.main()

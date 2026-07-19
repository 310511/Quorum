import unittest
from parser_010 import parse_count_10, valid_count_10

class ParserTests(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(parse_count_10("100"), 100)
        self.assertTrue(valid_count_10("100"))

if __name__ == "__main__":
    unittest.main()

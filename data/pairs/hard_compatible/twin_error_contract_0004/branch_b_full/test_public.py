import unittest
from parser_004 import parse_count_4, valid_count_4

class ParserTests(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(parse_count_4("40"), 40)
        self.assertTrue(valid_count_4("40"))

if __name__ == "__main__":
    unittest.main()

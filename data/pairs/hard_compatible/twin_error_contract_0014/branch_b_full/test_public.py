import unittest
from parser_014 import parse_count_14, valid_count_14

class ParserTests(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(parse_count_14("140"), 140)
        self.assertTrue(valid_count_14("140"))

if __name__ == "__main__":
    unittest.main()

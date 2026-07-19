import unittest
from parser_016 import parse_count_16, valid_count_16

class ParserTests(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(parse_count_16("160"), 160)
        self.assertTrue(valid_count_16("160"))

if __name__ == "__main__":
    unittest.main()

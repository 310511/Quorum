import unittest
from parser_015 import parse_count_15, valid_count_15

class ParserTests(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(parse_count_15("150"), 150)
        self.assertTrue(valid_count_15("150"))

if __name__ == "__main__":
    unittest.main()

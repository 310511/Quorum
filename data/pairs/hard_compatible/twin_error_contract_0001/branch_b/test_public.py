import unittest
from parser_001 import parse_count_1, valid_count_1

class ParserTests(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(parse_count_1("10"), 10)
        self.assertTrue(valid_count_1("10"))

if __name__ == "__main__":
    unittest.main()

import unittest
from parser_005 import parse_count_5, valid_count_5

class ParserTests(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(parse_count_5("50"), 50)
        self.assertTrue(valid_count_5("50"))

if __name__ == "__main__":
    unittest.main()

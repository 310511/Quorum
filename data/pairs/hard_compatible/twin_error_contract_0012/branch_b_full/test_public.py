import unittest
from parser_012 import parse_count_12, valid_count_12

class ParserTests(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(parse_count_12("120"), 120)
        self.assertTrue(valid_count_12("120"))

if __name__ == "__main__":
    unittest.main()

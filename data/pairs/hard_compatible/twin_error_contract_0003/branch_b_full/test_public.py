import unittest
from parser_003 import parse_count_3, valid_count_3

class ParserTests(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(parse_count_3("30"), 30)
        self.assertTrue(valid_count_3("30"))

if __name__ == "__main__":
    unittest.main()

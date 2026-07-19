import unittest
from parser_006 import parse_count_6, valid_count_6

class ParserTests(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(parse_count_6("60"), 60)
        self.assertTrue(valid_count_6("60"))

if __name__ == "__main__":
    unittest.main()

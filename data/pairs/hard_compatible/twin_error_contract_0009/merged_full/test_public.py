import unittest
from parser_009 import parse_count_9, valid_count_9

class ParserTests(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(parse_count_9("90"), 90)
        self.assertTrue(valid_count_9("90"))

if __name__ == "__main__":
    unittest.main()

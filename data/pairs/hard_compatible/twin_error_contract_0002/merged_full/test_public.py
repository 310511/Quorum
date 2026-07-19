import unittest
from parser_002 import parse_count_2, valid_count_2

class ParserTests(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(parse_count_2("20"), 20)
        self.assertTrue(valid_count_2("20"))

if __name__ == "__main__":
    unittest.main()

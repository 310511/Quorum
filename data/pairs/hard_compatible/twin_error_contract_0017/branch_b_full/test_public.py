import unittest
from parser_017 import parse_count_17, valid_count_17

class ParserTests(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(parse_count_17("170"), 170)
        self.assertTrue(valid_count_17("170"))

if __name__ == "__main__":
    unittest.main()

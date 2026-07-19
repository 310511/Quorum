import unittest
from parser_1_guard import ensure_parser_1_positive, Parser_1Gone

class GuardTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(ensure_parser_1_positive(2), 2)
    def test_bad(self):
        with self.assertRaises(Parser_1Gone):
            ensure_parser_1_positive(0)

if __name__ == "__main__":
    unittest.main()

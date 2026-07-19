import unittest
from parser_4_guard import ensure_parser_4_positive, Parser_4Gone

class GuardTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(ensure_parser_4_positive(2), 2)
    def test_bad(self):
        with self.assertRaises(Parser_4Gone):
            ensure_parser_4_positive(0)

if __name__ == "__main__":
    unittest.main()

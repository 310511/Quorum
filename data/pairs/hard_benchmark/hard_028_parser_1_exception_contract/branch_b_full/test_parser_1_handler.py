import unittest
from parser_1_handler import safe_parser_1

class HandlerTests(unittest.TestCase):
    def test_safe(self):
        self.assertEqual(safe_parser_1(0), 0)
        self.assertEqual(safe_parser_1(4), 4)

if __name__ == "__main__":
    unittest.main()

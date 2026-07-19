import unittest
from parser_ok8_alpha import alpha_parser_ok8

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_parser_ok8(1), 2)

if __name__ == "__main__":
    unittest.main()

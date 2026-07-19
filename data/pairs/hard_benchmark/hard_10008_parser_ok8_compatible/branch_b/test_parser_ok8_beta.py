import unittest
from parser_ok8_beta import beta_parser_ok8

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_parser_ok8(3), 6)

if __name__ == "__main__":
    unittest.main()

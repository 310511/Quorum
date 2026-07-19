import unittest
from parser_ok28_beta import beta_parser_ok28

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_parser_ok28(3), 6)

if __name__ == "__main__":
    unittest.main()

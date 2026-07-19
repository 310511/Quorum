import unittest
from pricing_ok9_beta import beta_pricing_ok9

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_pricing_ok9(3), 6)

if __name__ == "__main__":
    unittest.main()

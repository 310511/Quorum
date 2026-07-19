import unittest
from pricing_ok29_beta import beta_pricing_ok29

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_pricing_ok29(3), 6)

if __name__ == "__main__":
    unittest.main()

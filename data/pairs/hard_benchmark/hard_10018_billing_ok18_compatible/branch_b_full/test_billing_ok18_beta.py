import unittest
from billing_ok18_beta import beta_billing_ok18

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_billing_ok18(3), 6)

if __name__ == "__main__":
    unittest.main()

import unittest
from checkout_ok22_beta import beta_checkout_ok22

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_checkout_ok22(3), 6)

if __name__ == "__main__":
    unittest.main()

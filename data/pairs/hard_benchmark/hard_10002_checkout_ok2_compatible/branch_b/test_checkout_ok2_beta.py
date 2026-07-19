import unittest
from checkout_ok2_beta import beta_checkout_ok2

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_checkout_ok2(3), 6)

if __name__ == "__main__":
    unittest.main()

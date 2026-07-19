import unittest
from payments_ok10_beta import beta_payments_ok10

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_payments_ok10(3), 6)

if __name__ == "__main__":
    unittest.main()

import unittest
from metrics_ok21_beta import beta_metrics_ok21

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_metrics_ok21(3), 6)

if __name__ == "__main__":
    unittest.main()

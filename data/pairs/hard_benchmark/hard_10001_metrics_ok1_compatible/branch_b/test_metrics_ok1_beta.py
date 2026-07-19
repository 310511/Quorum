import unittest
from metrics_ok1_beta import beta_metrics_ok1

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_metrics_ok1(3), 6)

if __name__ == "__main__":
    unittest.main()

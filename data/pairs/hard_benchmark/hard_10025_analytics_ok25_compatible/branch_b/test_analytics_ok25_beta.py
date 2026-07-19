import unittest
from analytics_ok25_beta import beta_analytics_ok25

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_analytics_ok25(3), 6)

if __name__ == "__main__":
    unittest.main()

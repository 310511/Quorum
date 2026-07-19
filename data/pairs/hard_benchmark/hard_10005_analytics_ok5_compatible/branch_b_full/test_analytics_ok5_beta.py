import unittest
from analytics_ok5_beta import beta_analytics_ok5

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_analytics_ok5(3), 6)

if __name__ == "__main__":
    unittest.main()

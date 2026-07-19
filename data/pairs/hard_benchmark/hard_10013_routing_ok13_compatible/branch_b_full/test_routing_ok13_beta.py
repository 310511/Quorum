import unittest
from routing_ok13_beta import beta_routing_ok13

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_routing_ok13(3), 6)

if __name__ == "__main__":
    unittest.main()

import unittest
from tickets_ok15_beta import beta_tickets_ok15

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_tickets_ok15(3), 6)

if __name__ == "__main__":
    unittest.main()

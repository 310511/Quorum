import unittest
from scheduler_ok16_beta import beta_scheduler_ok16

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_scheduler_ok16(3), 6)

if __name__ == "__main__":
    unittest.main()

import unittest
from profile_ok0_beta import beta_profile_ok0

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_profile_ok0(3), 6)

if __name__ == "__main__":
    unittest.main()

import unittest
from profile_ok20_beta import beta_profile_ok20

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_profile_ok20(3), 6)

if __name__ == "__main__":
    unittest.main()

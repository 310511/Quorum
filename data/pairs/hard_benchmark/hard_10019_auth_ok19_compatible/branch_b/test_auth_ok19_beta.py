import unittest
from auth_ok19_beta import beta_auth_ok19

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_auth_ok19(3), 6)

if __name__ == "__main__":
    unittest.main()

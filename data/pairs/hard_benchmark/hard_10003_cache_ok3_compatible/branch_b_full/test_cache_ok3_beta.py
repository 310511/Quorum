import unittest
from cache_ok3_beta import beta_cache_ok3

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_cache_ok3(3), 6)

if __name__ == "__main__":
    unittest.main()

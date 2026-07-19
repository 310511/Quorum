import unittest
from cache_ok23_beta import beta_cache_ok23

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_cache_ok23(3), 6)

if __name__ == "__main__":
    unittest.main()

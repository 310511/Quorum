import unittest
from search_ok7_beta import beta_search_ok7

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_search_ok7(3), 6)

if __name__ == "__main__":
    unittest.main()

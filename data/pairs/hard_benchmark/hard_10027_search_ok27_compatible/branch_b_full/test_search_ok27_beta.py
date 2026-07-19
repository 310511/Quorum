import unittest
from search_ok27_beta import beta_search_ok27

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_search_ok27(3), 6)

if __name__ == "__main__":
    unittest.main()

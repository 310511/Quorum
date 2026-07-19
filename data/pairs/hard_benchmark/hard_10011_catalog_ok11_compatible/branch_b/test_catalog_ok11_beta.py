import unittest
from catalog_ok11_beta import beta_catalog_ok11

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_catalog_ok11(3), 6)

if __name__ == "__main__":
    unittest.main()

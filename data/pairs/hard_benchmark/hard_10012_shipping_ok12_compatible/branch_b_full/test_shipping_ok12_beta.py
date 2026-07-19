import unittest
from shipping_ok12_beta import beta_shipping_ok12

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_shipping_ok12(3), 6)

if __name__ == "__main__":
    unittest.main()

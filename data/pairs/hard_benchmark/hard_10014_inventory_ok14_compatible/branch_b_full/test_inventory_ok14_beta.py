import unittest
from inventory_ok14_beta import beta_inventory_ok14

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_inventory_ok14(3), 6)

if __name__ == "__main__":
    unittest.main()

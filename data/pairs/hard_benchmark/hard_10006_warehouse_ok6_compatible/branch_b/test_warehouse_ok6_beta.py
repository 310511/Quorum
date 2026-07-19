import unittest
from warehouse_ok6_beta import beta_warehouse_ok6

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_warehouse_ok6(3), 6)

if __name__ == "__main__":
    unittest.main()

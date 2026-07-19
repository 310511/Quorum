import unittest
from inventory_ok14_alpha import alpha_inventory_ok14

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_inventory_ok14(1), 2)

if __name__ == "__main__":
    unittest.main()

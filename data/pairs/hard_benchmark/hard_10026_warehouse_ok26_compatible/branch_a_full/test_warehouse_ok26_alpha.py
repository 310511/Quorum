import unittest
from warehouse_ok26_alpha import alpha_warehouse_ok26

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_warehouse_ok26(1), 2)

if __name__ == "__main__":
    unittest.main()

import unittest
from shipping_ok12_alpha import alpha_shipping_ok12

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_shipping_ok12(1), 2)

if __name__ == "__main__":
    unittest.main()

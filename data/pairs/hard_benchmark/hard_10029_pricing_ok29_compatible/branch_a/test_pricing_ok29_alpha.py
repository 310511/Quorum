import unittest
from pricing_ok29_alpha import alpha_pricing_ok29

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_pricing_ok29(1), 2)

if __name__ == "__main__":
    unittest.main()

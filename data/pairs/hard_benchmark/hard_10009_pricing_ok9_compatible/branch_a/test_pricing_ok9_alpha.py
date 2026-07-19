import unittest
from pricing_ok9_alpha import alpha_pricing_ok9

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_pricing_ok9(1), 2)

if __name__ == "__main__":
    unittest.main()

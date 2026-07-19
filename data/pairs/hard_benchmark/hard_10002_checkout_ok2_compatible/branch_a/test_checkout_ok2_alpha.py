import unittest
from checkout_ok2_alpha import alpha_checkout_ok2

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_checkout_ok2(1), 2)

if __name__ == "__main__":
    unittest.main()

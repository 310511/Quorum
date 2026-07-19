import unittest
from billing_ok18_alpha import alpha_billing_ok18

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_billing_ok18(1), 2)

if __name__ == "__main__":
    unittest.main()

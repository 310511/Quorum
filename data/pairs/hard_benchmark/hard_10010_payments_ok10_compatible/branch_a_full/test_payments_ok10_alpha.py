import unittest
from payments_ok10_alpha import alpha_payments_ok10

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_payments_ok10(1), 2)

if __name__ == "__main__":
    unittest.main()

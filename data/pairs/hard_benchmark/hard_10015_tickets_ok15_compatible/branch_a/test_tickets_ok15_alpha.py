import unittest
from tickets_ok15_alpha import alpha_tickets_ok15

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_tickets_ok15(1), 2)

if __name__ == "__main__":
    unittest.main()

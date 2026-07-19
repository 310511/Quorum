import unittest
from routing_ok13_alpha import alpha_routing_ok13

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_routing_ok13(1), 2)

if __name__ == "__main__":
    unittest.main()

import unittest
from analytics_ok5_alpha import alpha_analytics_ok5

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_analytics_ok5(1), 2)

if __name__ == "__main__":
    unittest.main()

import unittest
from metrics_ok21_alpha import alpha_metrics_ok21

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_metrics_ok21(1), 2)

if __name__ == "__main__":
    unittest.main()

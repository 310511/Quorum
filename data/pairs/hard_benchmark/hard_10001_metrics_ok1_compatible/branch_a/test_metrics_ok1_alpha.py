import unittest
from metrics_ok1_alpha import alpha_metrics_ok1

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_metrics_ok1(1), 2)

if __name__ == "__main__":
    unittest.main()

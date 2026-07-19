import unittest
from cache_ok23_alpha import alpha_cache_ok23

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_cache_ok23(1), 2)

if __name__ == "__main__":
    unittest.main()

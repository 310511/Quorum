import unittest
from cache_ok3_alpha import alpha_cache_ok3

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_cache_ok3(1), 2)

if __name__ == "__main__":
    unittest.main()

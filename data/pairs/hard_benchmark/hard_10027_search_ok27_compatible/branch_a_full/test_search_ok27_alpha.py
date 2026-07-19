import unittest
from search_ok27_alpha import alpha_search_ok27

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_search_ok27(1), 2)

if __name__ == "__main__":
    unittest.main()

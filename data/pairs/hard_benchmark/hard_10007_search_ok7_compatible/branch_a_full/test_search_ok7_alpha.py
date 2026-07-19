import unittest
from search_ok7_alpha import alpha_search_ok7

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_search_ok7(1), 2)

if __name__ == "__main__":
    unittest.main()

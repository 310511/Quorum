import unittest
from profile_ok20_alpha import alpha_profile_ok20

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_profile_ok20(1), 2)

if __name__ == "__main__":
    unittest.main()

import unittest
from profile_ok0_alpha import alpha_profile_ok0

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_profile_ok0(1), 2)

if __name__ == "__main__":
    unittest.main()

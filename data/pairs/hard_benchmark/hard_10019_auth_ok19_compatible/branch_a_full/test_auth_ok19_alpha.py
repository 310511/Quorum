import unittest
from auth_ok19_alpha import alpha_auth_ok19

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_auth_ok19(1), 2)

if __name__ == "__main__":
    unittest.main()

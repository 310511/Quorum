import unittest
from catalog_ok11_alpha import alpha_catalog_ok11

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_catalog_ok11(1), 2)

if __name__ == "__main__":
    unittest.main()

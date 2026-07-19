import unittest
from pricing_ok9_base import identity_pricing_ok9

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_pricing_ok9(5), 5)

if __name__ == "__main__":
    unittest.main()

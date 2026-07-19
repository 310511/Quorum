import unittest
from checkout_ok22_base import identity_checkout_ok22

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_checkout_ok22(5), 5)

if __name__ == "__main__":
    unittest.main()

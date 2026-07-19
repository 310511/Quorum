import unittest
from checkout_ok2_base import identity_checkout_ok2

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_checkout_ok2(5), 5)

if __name__ == "__main__":
    unittest.main()

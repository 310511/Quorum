import unittest
from billing_ok18_base import identity_billing_ok18

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_billing_ok18(5), 5)

if __name__ == "__main__":
    unittest.main()

import unittest
from identity_016 import authorized_16

class IdentityTests(unittest.TestCase):
    def test_exact_identity(self):
        self.assertTrue(authorized_16("Admin96", "Admin96"))
    def test_different_identity(self):
        self.assertFalse(authorized_16("User96", "Admin96"))

if __name__ == "__main__":
    unittest.main()

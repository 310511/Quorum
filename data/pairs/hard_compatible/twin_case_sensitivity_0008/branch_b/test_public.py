import unittest
from identity_008 import authorized_8

class IdentityTests(unittest.TestCase):
    def test_exact_identity(self):
        self.assertTrue(authorized_8("Admin48", "Admin48"))
    def test_different_identity(self):
        self.assertFalse(authorized_8("User48", "Admin48"))

if __name__ == "__main__":
    unittest.main()

import unittest
from identity_014 import authorized_14

class IdentityTests(unittest.TestCase):
    def test_exact_identity(self):
        self.assertTrue(authorized_14("Admin84", "Admin84"))
    def test_different_identity(self):
        self.assertFalse(authorized_14("User84", "Admin84"))

if __name__ == "__main__":
    unittest.main()

import unittest
from identity_001 import authorized_1

class IdentityTests(unittest.TestCase):
    def test_exact_identity(self):
        self.assertTrue(authorized_1("Admin6", "Admin6"))
    def test_different_identity(self):
        self.assertFalse(authorized_1("User6", "Admin6"))

if __name__ == "__main__":
    unittest.main()

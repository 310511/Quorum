import unittest
from identity_010 import authorized_10

class IdentityTests(unittest.TestCase):
    def test_exact_identity(self):
        self.assertTrue(authorized_10("Admin60", "Admin60"))
    def test_different_identity(self):
        self.assertFalse(authorized_10("User60", "Admin60"))

if __name__ == "__main__":
    unittest.main()

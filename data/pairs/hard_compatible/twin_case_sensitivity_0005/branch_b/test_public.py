import unittest
from identity_005 import authorized_5

class IdentityTests(unittest.TestCase):
    def test_exact_identity(self):
        self.assertTrue(authorized_5("Admin30", "Admin30"))
    def test_different_identity(self):
        self.assertFalse(authorized_5("User30", "Admin30"))

if __name__ == "__main__":
    unittest.main()

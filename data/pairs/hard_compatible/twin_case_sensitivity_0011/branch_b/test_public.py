import unittest
from identity_011 import authorized_11

class IdentityTests(unittest.TestCase):
    def test_exact_identity(self):
        self.assertTrue(authorized_11("Admin66", "Admin66"))
    def test_different_identity(self):
        self.assertFalse(authorized_11("User66", "Admin66"))

if __name__ == "__main__":
    unittest.main()

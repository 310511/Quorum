import unittest
from identity_004 import authorized_4

class IdentityTests(unittest.TestCase):
    def test_exact_identity(self):
        self.assertTrue(authorized_4("Admin24", "Admin24"))
    def test_different_identity(self):
        self.assertFalse(authorized_4("User24", "Admin24"))

if __name__ == "__main__":
    unittest.main()

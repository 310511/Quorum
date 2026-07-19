import unittest
from identity_002 import authorized_2

class IdentityTests(unittest.TestCase):
    def test_exact_identity(self):
        self.assertTrue(authorized_2("Admin12", "Admin12"))
    def test_different_identity(self):
        self.assertFalse(authorized_2("User12", "Admin12"))

if __name__ == "__main__":
    unittest.main()

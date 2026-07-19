import unittest
from identity_013 import authorized_13

class IdentityTests(unittest.TestCase):
    def test_exact_identity(self):
        self.assertTrue(authorized_13("Admin78", "Admin78"))
    def test_different_identity(self):
        self.assertFalse(authorized_13("User78", "Admin78"))

if __name__ == "__main__":
    unittest.main()

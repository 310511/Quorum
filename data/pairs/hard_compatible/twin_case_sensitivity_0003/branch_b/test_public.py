import unittest
from identity_003 import authorized_3

class IdentityTests(unittest.TestCase):
    def test_exact_identity(self):
        self.assertTrue(authorized_3("Admin18", "Admin18"))
    def test_different_identity(self):
        self.assertFalse(authorized_3("User18", "Admin18"))

if __name__ == "__main__":
    unittest.main()

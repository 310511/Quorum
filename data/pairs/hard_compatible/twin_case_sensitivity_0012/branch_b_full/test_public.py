import unittest
from identity_012 import authorized_12

class IdentityTests(unittest.TestCase):
    def test_exact_identity(self):
        self.assertTrue(authorized_12("Admin72", "Admin72"))
    def test_different_identity(self):
        self.assertFalse(authorized_12("User72", "Admin72"))

if __name__ == "__main__":
    unittest.main()

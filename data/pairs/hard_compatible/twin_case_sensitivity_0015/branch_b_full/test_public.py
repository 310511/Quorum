import unittest
from identity_015 import authorized_15

class IdentityTests(unittest.TestCase):
    def test_exact_identity(self):
        self.assertTrue(authorized_15("Admin90", "Admin90"))
    def test_different_identity(self):
        self.assertFalse(authorized_15("User90", "Admin90"))

if __name__ == "__main__":
    unittest.main()

import unittest
from identity_017 import authorized_17

class IdentityTests(unittest.TestCase):
    def test_exact_identity(self):
        self.assertTrue(authorized_17("Admin102", "Admin102"))
    def test_different_identity(self):
        self.assertFalse(authorized_17("User102", "Admin102"))

if __name__ == "__main__":
    unittest.main()

import unittest
from identity_006 import authorized_6

class IdentityTests(unittest.TestCase):
    def test_exact_identity(self):
        self.assertTrue(authorized_6("Admin36", "Admin36"))
    def test_different_identity(self):
        self.assertFalse(authorized_6("User36", "Admin36"))

if __name__ == "__main__":
    unittest.main()

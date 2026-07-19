import unittest
from identity_007 import authorized_7

class IdentityTests(unittest.TestCase):
    def test_exact_identity(self):
        self.assertTrue(authorized_7("Admin42", "Admin42"))
    def test_different_identity(self):
        self.assertFalse(authorized_7("User42", "Admin42"))

if __name__ == "__main__":
    unittest.main()

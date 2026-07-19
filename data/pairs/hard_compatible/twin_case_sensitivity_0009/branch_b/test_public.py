import unittest
from identity_009 import authorized_9

class IdentityTests(unittest.TestCase):
    def test_exact_identity(self):
        self.assertTrue(authorized_9("Admin54", "Admin54"))
    def test_different_identity(self):
        self.assertFalse(authorized_9("User54", "Admin54"))

if __name__ == "__main__":
    unittest.main()

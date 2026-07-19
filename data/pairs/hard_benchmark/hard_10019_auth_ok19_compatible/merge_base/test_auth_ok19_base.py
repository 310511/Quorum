import unittest
from auth_ok19_base import identity_auth_ok19

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_auth_ok19(5), 5)

if __name__ == "__main__":
    unittest.main()

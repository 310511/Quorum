import unittest
from profile_ok0_base import identity_profile_ok0

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_profile_ok0(5), 5)

if __name__ == "__main__":
    unittest.main()

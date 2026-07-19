import unittest
from profile_ok20_base import identity_profile_ok20

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_profile_ok20(5), 5)

if __name__ == "__main__":
    unittest.main()

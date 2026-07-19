import unittest
from profile_2_guard import ensure_profile_2_positive, Profile_2Gone

class GuardTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(ensure_profile_2_positive(2), 2)
    def test_bad(self):
        with self.assertRaises(Profile_2Gone):
            ensure_profile_2_positive(0)

if __name__ == "__main__":
    unittest.main()

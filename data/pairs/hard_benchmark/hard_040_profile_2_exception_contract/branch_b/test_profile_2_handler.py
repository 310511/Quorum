import unittest
from profile_2_handler import safe_profile_2

class HandlerTests(unittest.TestCase):
    def test_safe(self):
        self.assertEqual(safe_profile_2(0), 0)
        self.assertEqual(safe_profile_2(4), 4)

if __name__ == "__main__":
    unittest.main()

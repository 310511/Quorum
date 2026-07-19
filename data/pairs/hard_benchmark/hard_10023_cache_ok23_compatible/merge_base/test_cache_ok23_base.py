import unittest
from cache_ok23_base import identity_cache_ok23

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_cache_ok23(5), 5)

if __name__ == "__main__":
    unittest.main()

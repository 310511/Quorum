import unittest
from search_ok27_base import identity_search_ok27

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_search_ok27(5), 5)

if __name__ == "__main__":
    unittest.main()

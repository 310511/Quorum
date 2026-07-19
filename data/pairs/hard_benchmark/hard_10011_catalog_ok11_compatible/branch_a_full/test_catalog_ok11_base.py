import unittest
from catalog_ok11_base import identity_catalog_ok11

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_catalog_ok11(5), 5)

if __name__ == "__main__":
    unittest.main()

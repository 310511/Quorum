import unittest
from inventory_ok14_base import identity_inventory_ok14

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_inventory_ok14(5), 5)

if __name__ == "__main__":
    unittest.main()

import unittest
from warehouse_ok6_base import identity_warehouse_ok6

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_warehouse_ok6(5), 5)

if __name__ == "__main__":
    unittest.main()

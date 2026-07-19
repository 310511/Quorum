import unittest
from inventory_4_guard import ensure_inventory_4_positive, Inventory_4Error

class GuardTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(ensure_inventory_4_positive(2), 2)
    def test_bad(self):
        with self.assertRaises(Inventory_4Error):
            ensure_inventory_4_positive(0)

if __name__ == "__main__":
    unittest.main()

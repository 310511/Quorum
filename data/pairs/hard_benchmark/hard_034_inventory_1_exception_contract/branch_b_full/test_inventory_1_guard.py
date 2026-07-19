import unittest
from inventory_1_guard import ensure_inventory_1_positive, Inventory_1Error

class GuardTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(ensure_inventory_1_positive(2), 2)
    def test_bad(self):
        with self.assertRaises(Inventory_1Error):
            ensure_inventory_1_positive(0)

if __name__ == "__main__":
    unittest.main()

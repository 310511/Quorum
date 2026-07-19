import unittest
from warehouse_2_guard import ensure_warehouse_2_positive, Warehouse_2Error

class GuardTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(ensure_warehouse_2_positive(2), 2)
    def test_bad(self):
        with self.assertRaises(Warehouse_2Error):
            ensure_warehouse_2_positive(0)

if __name__ == "__main__":
    unittest.main()

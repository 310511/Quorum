import unittest
from inventory_4_handler import safe_inventory_4

class HandlerTests(unittest.TestCase):
    def test_safe(self):
        self.assertEqual(safe_inventory_4(0), 0)
        self.assertEqual(safe_inventory_4(4), 4)

if __name__ == "__main__":
    unittest.main()

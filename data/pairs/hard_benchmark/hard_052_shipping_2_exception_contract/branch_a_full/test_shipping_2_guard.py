import unittest
from shipping_2_guard import ensure_shipping_2_positive, Shipping_2Gone

class GuardTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(ensure_shipping_2_positive(2), 2)
    def test_bad(self):
        with self.assertRaises(Shipping_2Gone):
            ensure_shipping_2_positive(0)

if __name__ == "__main__":
    unittest.main()

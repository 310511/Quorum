import unittest
from checkout_4_guard import ensure_checkout_4_positive, Checkout_4Gone

class GuardTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(ensure_checkout_4_positive(2), 2)
    def test_bad(self):
        with self.assertRaises(Checkout_4Gone):
            ensure_checkout_4_positive(0)

if __name__ == "__main__":
    unittest.main()

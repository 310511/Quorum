import unittest
from checkout_1_guard import ensure_checkout_1_positive, Checkout_1Error

class GuardTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(ensure_checkout_1_positive(2), 2)
    def test_bad(self):
        with self.assertRaises(Checkout_1Error):
            ensure_checkout_1_positive(0)

if __name__ == "__main__":
    unittest.main()

import unittest
from billing_2_guard import ensure_billing_2_positive, Billing_2Error

class GuardTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(ensure_billing_2_positive(2), 2)
    def test_bad(self):
        with self.assertRaises(Billing_2Error):
            ensure_billing_2_positive(0)

if __name__ == "__main__":
    unittest.main()

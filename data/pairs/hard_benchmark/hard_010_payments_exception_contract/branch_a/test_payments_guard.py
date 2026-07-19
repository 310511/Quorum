import unittest
from payments_guard import ensure_payments_positive, PaymentsGone

class GuardTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(ensure_payments_positive(2), 2)
    def test_bad(self):
        with self.assertRaises(PaymentsGone):
            ensure_payments_positive(0)

if __name__ == "__main__":
    unittest.main()
